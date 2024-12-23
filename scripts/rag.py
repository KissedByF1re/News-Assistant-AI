import json
import os
from typing import List
import pathlib

from pathlib import Path
# from IPython.display import Image, display

from langchain_community.document_loaders import JSONLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from langchain_core.messages import SystemMessage
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.documents import Document
from langchain_core.tools import tool

from dotenv import load_dotenv


load_dotenv(".env")
OPENAI_API_KEY = os.getenv("GPT_TOKEN")

global llm
llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)    

# Define the metadata extraction function.
def metadata_func(record: dict, metadata: dict) -> dict:

    metadata["datetime"] = record.get("datetime")
    metadata["link"] = record.get("link")

    return metadata

def refresh_index(json_file_path):
    assert os.path.isfile(json_file_path), "File is not exists!"
    loader = JSONLoader(
        file_path = json_file_path,
        jq_schema='.[]',
        content_key="text",
        metadata_func=metadata_func
    )
    data = loader.load() 
    # Разделение документов на фрагменты для улучшения поиска
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=20,
        is_separator_regex=False,
    )
    texts = text_splitter.split_documents(data)
    return texts

def set_faiss(is_indexed: bool = True,
              path_to_faiss: str = "../data/index/faiss_index",
              texts: list = None):
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
    # assert os.path.isdir(path_to_faiss), "FAISS is not created!"
    faiss_store = FAISS.load_local(
        path_to_faiss, embeddings, allow_dangerous_deserialization=True
    )
    global faiss_retriever
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
def query_or_respond(state: State):
    """Generate tool call for retrieval or respond."""
    # llm = ChatOpenAI(model=model, api_key=OPENAI_API_KEY)
    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])
    # MessagesState appends messages to state instead of overwriting
    return {"messages": [response]}


# Step 2: Execute the retrieval.
tools = ToolNode([retrieve])

# Step 3: Generate a response using the retrieved content.
def generate(state: MessagesState):
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
    breakpoint
    for tool_message in tool_messages:
        context.extend(tool_message.artifact)
    return {"messages": [response], "context": context}


def compile_graph():
    graph_builder = StateGraph(MessagesState)
    graph_builder.add_node(query_or_respond)
    graph_builder.add_node(tools)
    graph_builder.add_node(generate)

    graph_builder.set_entry_point("query_or_respond")
    graph_builder.add_conditional_edges(
        "query_or_respond",
        tools_condition,
        {END: END, "tools": "tools"},
    )
    graph_builder.add_edge("tools", "generate")
    graph_builder.add_edge("generate", END)

    graph = graph_builder.compile()
    return graph
