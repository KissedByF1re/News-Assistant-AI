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

<<<<<<< HEAD
- **Интеграция с RAG:**
  - Набор данных может быть использован для построения индекса (например, с использованием FAISS, LangChain или LlamaIndex).
=======
- **Построение RAG:**
  - Для создания эмбеддингов используется [OpenAIEmbeddings](https://python.langchain.com/docs/integrations/text_embedding/openai/)
  - Для построения индекса и поиска релевантных новостей применяется [Faiss](https://github.com/facebookresearch/faiss)
  - В качестве LLM модели используется ChatGPT (4o-mini)

- **Оценка работы сервиса:** 
  - Таблица с проверочными вопросами доступна по [ссылке](https://docs.google.com/spreadsheets/d/1M4PAOxSmMsAqZOXbxrQge-SqjCcrYNreGDisKOfUZQE/edit?usp=sharing)
  - Запись с демонстрацией работы сервиса доступна по [ссылке](https://drive.google.com/file/d/1KBfNuyDmX1wVZPR_TIIz0GqlAscP-cBS/view?usp=sharing)
  - Для peer-rewiev предоставим временную ссылку ([автор 1](https://t.medatanalist), [автор 2](https://t.me/kbf02))


## Ограничения
- Сервис работает только с использованием API-ключа для ChatGPT и VPN
- На данный момент не настроено автоматическое обновление новостей (новые данные подгружаются самостоятельно)
>>>>>>> parent of 87e694f (fix: correct link)

## Структура проекта
```plaintext
.
├── data/                     # Скачанные данные (JSON)
├── notebooks/                # Jupyter Notebooks для анализа и тестов
├── scripts/                  # Основные скрипты проекта
│   ├── parcing_data.py       # Скрипт для парсинга данных из Telegram-канала
├── venv/                     # Виртуальное окружение Python
├── requirements.txt          # Зависимости Python
├── LICENSE                   # Лицензия
└── README.md                 # Описание проекта