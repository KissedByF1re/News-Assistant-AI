import pathlib
from dotenv import load_dotenv
import os
import getpass
from typing import Optional, Union

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import JSONLoader
from typing_extensions import List, TypedDict
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from langchain_core.prompts import PromptTemplate


class State(TypedDict):
    """
    Класс для хранения состояния системы.
    """
    question: str
    context: List[Document]
    answer: str

def load_api_env(env_file: str="../.env"):
    """
    Загружает переменные окружения из файла .env.

    Args:
        env_file (str): Путь к файлу .env. По умолчанию "../.env"

    Returns:
        None
    """
    if os.path.isfile(env_file):
        status = load_dotenv(env_file)
    else:
        env_file = input("Введите путь к .env файлу: ")
        status = load_dotenv(env_file)
    return status

def metadata_func(record: dict, metadata: dict) -> dict:
    """
    Функция для добавления метаданных к документу.

    Args:
        record (dict): Словарь с данными о документе.
        metadata (dict): Словарь с текущими метаданными документа.

    Returns:
        dict: Словарь с обновленными метаданными документа.
    """
    metadata["datetime"] = record.get("datetime")
    metadata["link"] = record.get("link")

    return metadata

def prepare_data(json_file_path: str) -> List[Document]:
    """
    Подготавливает данные из JSON файла для использования в RAG.

    Args:
        json_file_path (str): Путь к JSON файлу с данными.

    Returns:
        List[Document]: Список документов, каждый из которых содержит текст и метаданные.
    """
    json_file_path = pathlib.Path(json_file_path).as_posix()
    loader = JSONLoader(
            file_path = json_file_path,
            jq_schema='.[]',
            content_key="text", 
            metadata_func=metadata_func
        )
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=20,
        is_separator_regex=False,
    )
    texts = text_splitter.split_documents(data)
    return texts

def set_faiss(faiss_path: str="../data/index/faiss_index",
              json_file_path: Optional[str]="../data/cleaned/combined_news.json") -> FAISS:
    """
    Создает или загружает индекс FAISS для векторного поиска.

    Args:
        faiss_path (str): Путь для сохранения/загрузки индекса FAISS. По умолчанию "../data/index/faiss_index"
        json_file_path (Optional[str]): Путь к JSON файлу с данными. По умолчанию "../data/cleaned/combined_news.json"

    Returns:
        FAISS: Объект векторного хранилища FAISS с загруженными эмбеддингами документов.

    Raises:
        AssertionError: Если не указан путь для индекса FAISS или отсутствуют тексты при создании нового индекса.
    """
    load_dotenv("../.env")
    embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
    path_to_faiss = pathlib.Path(faiss_path).as_posix()
    is_indexed = os.path.isdir(path_to_faiss)
    if not is_indexed:
        assert isinstance(faiss_path, (str, pathlib.Path)), "Путь к индексу FAISS должен быть строкой или объектом Path"
        assert json_file_path is not None, "Необходимо указать путь к JSON файлу с данными"
        texts = prepare_data(json_file_path)
        assert texts, "Не удалось загрузить тексты из JSON файла"
        faiss_store = FAISS.from_documents(texts, embeddings)
        faiss_store.save_local(path_to_faiss)
    faiss_store = FAISS.load_local(
        path_to_faiss, embeddings, allow_dangerous_deserialization=True
    )
    return faiss_store

def initialize_components(faiss_path: Optional[str],
                          json_file_path: Optional[str],
                          openai_key: Optional[str],
                          components: List[str]=["faiss_retriever", "llm"]) -> List[Union[FAISS, ChatOpenAI]]:
    """
    Инициализирует компоненты для работы системы вопросов и ответов.

    Args:
        faiss_path (Optional[str]): Путь к индексу FAISS. 
        json_file_path (Optional[str]): Путь к JSON файлу с данными.
        openai_key (Optional[str]): API ключ OpenAI.
        components (List[str]): Список компонентов для инициализации. 
            По умолчанию ["faiss_retriever", "llm"].

    Returns:
        List[Union[FAISS, ChatOpenAI]]: Список инициализированных компонентов.
            Возвращает [faiss_retriever, llm], где компоненты могут быть None,
            если они не указаны в списке components.
    """
    if "faiss_retriever" in components: 
        faiss_store = set_faiss(faiss_path=faiss_path, 
                                json_file_path=None)
        faiss_retriever = faiss_store.as_retriever(k=5) 
    else:
        faiss_retriever = None
    if "llm" in components:
        llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_key)
    else:
        llm = None
    return [faiss_retriever, llm]



PROMPT_TEMPLATE = """You are a news-assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, say that you don't know.
Use three sentences maximum and keep the answer concise.

{context}

Question: {question}

Helpful Answer:"""

def set_prompt(template: str):
    """
    Создает шаблон промпта для RAG-системы.

    Args:
        template (str): Строка шаблона с плейсхолдерами {context} и {question}.

    Returns:
        PromptTemplate: Объект шаблона промпта для использования в RAG-системе.
    """
    custom_rag_prompt = PromptTemplate.from_template(template)
    return custom_rag_prompt

def retrieve(state: State):
    """
    Извлекает релевантные документы из FAISS индекса.

    Args:
        state (State): Объект состояния, содержащий вопрос пользователя.

    Returns:
        dict: Словарь с ключом "context", содержащий список релевантных документов.
    """
    faiss_path = pathlib.Path(r"../data/index/faiss_index").as_posix()
    faiss_retriever = initialize_components(faiss_path=faiss_path, 
                                            json_file_path=None, 
                                            openai_key="", 
                                            components=["faiss_retriever"])[0]
    retrieved_docs = faiss_retriever.get_relevant_documents(state["question"])
    return {"context": retrieved_docs}

def generate(state: State):
    """
    Генерирует ответ на вопрос пользователя на основе извлеченного контекста.

    Args:
        state (State): Объект состояния, содержащий вопрос пользователя и извлеченный контекст.

    Returns:
        dict: Словарь с ключом "answer", содержащий сгенерированный ответ на вопрос.
    """
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    custom_rag_prompt = set_prompt(PROMPT_TEMPLATE)
    messages = custom_rag_prompt.invoke({"question": state["question"], "context": docs_content})
    load_dotenv("../.env")
    api_key = os.getenv("OPENAI_API_KEY")
    llm = initialize_components(faiss_path=None,
                                json_file_path=None,
                                openai_key=api_key,
                                components=["llm"])[1]
    response = llm.invoke(messages)
    return {"answer": response.content}

def get_answer_and_links(question: str) -> dict:
    """
    Получает ответ на вопрос пользователя и список источников информации.

    Args:
        question (str): Вопрос пользователя.

    Returns:
        dict: Словарь, содержащий ответ на вопрос ('answer') и список ссылок на источники ('links').
    """
    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    graph = graph_builder.compile()
    result = graph.invoke({"question": question})
    
    links = set()
    for doc in result["context"]:
        links.add(doc.metadata["link"])
        
    return {
        "answer": result["answer"],
        "links": list(links)
    }
