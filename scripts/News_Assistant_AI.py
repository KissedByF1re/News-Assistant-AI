import streamlit as st
from dotenv import load_dotenv
import os
import pdb

from rag import *

# Подгружаем данные и FAISS-индекс
# INDEX_PATH = "data/cleaned/news_faiss_openai.index"
# METADATA_PATH = "data/cleaned/combined_news.json"

# Вводная информация о проекте
st.markdown(
    """
    <h1 style='text-align: center;'>
        Добро пожаловать на страницу News Assistant AI! 
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style='text-align: justify; max-width: 800px; margin: 0 auto; margin-bottom: 20px;'>
        News Assistant AI - это RAG-система, построенная на базе Chat-GPT, FAISS и информации из 
        новостных Telegram-каналов Mash и РИА Новости. Если вы хотите найти интересующую вас новость, 
        то введите ваш запрос в поле ниже.
    </div>
    """,
    unsafe_allow_html=True
)

# Поле для ввода запроса
query = st.text_input("Введите ваш запрос:", "")

# Кнопка для поиска
button_clicked = st.button("Поиск")

# Логика обработки запроса (реагирует на Enter или нажатие кнопки "Поиск")
if query and (button_clicked or st.session_state.get("last_query") != query):
    st.session_state["last_query"] = query  # Сохраняем последний введённый запрос
    # pdb.set_trace()
    # texts = refresh_index(pathlib.Path(r"C:\Users\vallo\Documents\Projects\News-Assistant-AI\data\cleaned\combined_news.json").as_posix())
    path_to_faiss = pathlib.Path(r"C:\Users\vallo\Documents\Projects\News-Assistant-AI\data\index\faiss_index").as_posix()
    faiss_retriever = set_faiss(path_to_faiss=path_to_faiss)
    graph = compile_graph()
    # pdb.set_trace()
    result = graph.invoke({"messages": [{"role": "user", "content": query}]})
    # pdb.set_trace()
    # answer = result["messages"][-1].content
    # for step in graph.stream(
    #     {"messages": [{"role": "user", "content": query}]},
    #     stream_mode="values",
    # ):
    #     pass
#     answer = step["messages"][-1].content
#     # links = [link.metadata["link"] for link in step["context"]]
#     #Здесь должна быть обработка запрос + поиск в FAISS

#     # Отображение результатов
    st.subheader("Результаты поиска:")
    st.write(result)

#     st.subheader("Источники:")
#     st.write("www")
#     # for link in links:
#     #     st.write(link)
# else:
#     st.error("Пожалуйста, введите запрос!")


# Добавление секции "Контакты"
st.markdown(
    """
    <div style='text-align: center; margin-top: 50px;'>
        <h3>Контакты</h3>
        <p>
            <a href='https://github.com/KissedByF1re' style='font-size: 16px; margin: 0 10px;' target='_blank'>Developer 1</a>
            |
            <a href='https://github.com/datanalist' style='font-size: 16px; margin: 0 10px;' target='_blank'>Developer 2</a>
            |
            <a href='https://github.com/KissedByF1re/News-Assistant-AI' style='font-size: 16px; margin: 0 10px;' target='_blank'>GitHub проекта</a>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Добавление надписи внизу страницы
st.markdown(
    """
    <div style='text-align: center; margin-top: 10px;'>
        <h6>Powered by Streamlit</h6>
    </div>
    """,
    unsafe_allow_html=True
)

if __name__ == "__main__":
    # aa = os.getcwd()
    # print()
    # texts = refresh_index(pathlib.Path(r"C:\Users\R1\Documents\Projects\News-Assistant-AI\data\raw\combined_news.json").as_posix())
    path_to_faiss = pathlib.Path(r"C:\Users\R1\Documents\Projects\News-Assistant-AI\data\index\faiss_index").as_posix()
    faiss_retriever = set_faiss()
    graph = compile_graph()
    result = graph.invoke({"messages": [{"role": "user", "content": query}]})
    answer = result["messages"][-1].content