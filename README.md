# News Assistant AI

## Описание проекта
Этот проект направлен на построение системы **Retrieval-Augmented Generation (RAG)** на основе новостных сообщений из публичных Telegram-каналов [Mash](https://t.me/s/mash) и [РИА Новости](https://t.me/s/rian_ru). Проект включает парсинг сообщений каналов, обработку данных и создание поисковой системы для генерации ответов на основе новостного контекста.

## Функциональность
- **Сбор данных из Telegram-каналов:**
  - Используется Selenium и BeautifulSoup для парсинга сообщений с веб-версии Telegram.
  - Поддерживается извлечение текста, даты и времени из сообщений.

- **Создание набора данных:**
  - Скачанные сообщения сохраняются в формате JSON.
  - Данные структурированы для удобной интеграции с RAG-системой.

- **Интеграция с RAG:**
  - Набор данных может быть использован для построения индекса (например, с использованием FAISS, LangChain или LlamaIndex).

## Структура проекта
```plaintext
.
├── notebooks/                # Jupyter Notebooks для анализа и тестов
├── scripts/                  # Основные скрипты проекта
│   ├── parcing_data.py       # Скрипт для парсинга данных из Telegram-канала
├── requirements.txt          # Зависимости Python
├── LICENSE                   # Лицензия
└── README.md                 # Описание проекта
```

## Установка зависимостей
```bash
pip install -r requirements.txt
```
## Запускаем проект из директории со скриптом
```bash
streamlit run News_Assistant_AI.py
```
