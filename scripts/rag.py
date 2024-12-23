import json
import os
from typing import List

from pathlib import Path
from IPython.display import Image, display

from langchain_community.document_loaders import JSONLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain.embeddings import OpenAIEmbeddings
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from langchain_core.messages import SystemMessage
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.documents import Document
from langchain_core.tools import tool

from dotenv import load_dotenv

OPENAI_API_KEY = os.getenv("GPT_TOKEN")

def set_env_file(path_to_env: str = ".env"):
    """Set your env file

    Args:
        path_to_env (str, optional): path to your env file. Defaults to ".env".
    """
    load_dotenv(Path(path_to_env).as_posix())

def set_faiss(is_indexed: bool = True,
              path_to_faiss: str = "../data/index/faiss_index",
              texts: list = None) -> type[VectorStoreRetrieve]:
    """Set faiss

    Args:
        is_indexed (bool, optional): if you have indexed faiss-store. Defaults to True.
        path_to_faiss (str, optional): path to your store. Defaults to "../data/index/faiss_index".
        texts (list, optional): list with Documents to refresh faiss. Defaults to None.
    """
    api_key = os.getenv("GPT_TOKEN")
    embeddings = OpenAIEmbeddings(api_key=api_key)
    if not is_indexed:
        assert texts is not None, "Put your texts with Document"
        faiss_store = FAISS.from_documents(texts, embeddings)
        faiss_store.save_local(path_to_faiss)
    assert os.path.isdir(path_to_faiss), "FAISS is not created!"
    faiss_store = FAISS.load_local(
        path_to_faiss, embeddings, allow_dangerous_deserialization=True
    )
    faiss_retriever = faiss_store.as_retriever(k=5)
    return faiss_retriever

@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve information related to a query."""
    faiss_retriever = set_faiss()
    retrieved_docs = faiss_retriever.get_relevant_documents(query, k=5)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

class State(MessagesState):
    context: List[Document]

# Step 1: Generate an AIMessage that may include a tool-call to be sent.
def query_or_respond(state: State, 
                     model: ChatOpenAI):
    """Generate tool call for retrieval or respond."""
    llm = ChatOpenAI(model=model, api_key=OPENAI_API_KEY)
    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])
    # MessagesState appends messages to state instead of overwriting
    return {"messages": [response]}


# Step 2: Execute the retrieval.
tools = ToolNode([retrieve])

# Step 3: Generate a response using the retrieved content.
def generate(state: MessagesState,
             ):
    """Generate answer."""
    # Get generated ToolMessages
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]

    # Format into prompt
    docs_content = "\n\n".join(doc.content for doc in tool_messages)
    system_message_content = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        f"{docs_content}"
    )
    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]
    prompt = [SystemMessage(system_message_content)] + conversation_messages

    # Run
    response = llm.invoke(prompt)
    context = []
    for tool_message in tool_messages:
        context.extend(tool_message.artifact)
    return {"messages": [response], "context": context}