# News Assistant AI

## Описание проекта
Этот проект направлен на построение системы **Retrieval-Augmented Generation (RAG)** на основе новостных сообщений из публичных Telegram-каналов [Mash](https://t.me/s/mash) и [РИА Новости](https://t.me/s/rian_ru). Проект включает парсинг сообщений каналов, обработку данных и создание поисковой системы для генерации ответов на основе новостного контекста.

## Функциональность
- **Сбор данных из Telegram-каналов:**
  - Используется [Selenium](https://www.selenium.dev/documentation/) и [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc.ru/bs4ru.html) для парсинга сообщений с веб-версии Telegram.
  - Поддерживается извлечение текста, даты и времени из сообщений.

- **Создание набора данных:**
  - Скачанные сообщения сохраняются в формате JSON.
  - Данные структурированы для удобной интеграции с RAG-системой.

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

## Структура проекта
```plaintext
.
├── notebooks/                    # Jupyter Notebooks для анализа и тестов
│   ├── async_parser.ipynb        # Ноутбук с проверкой возможности скачки новостей с помощью библиотеки Telethon
│   ├── Combine_data.ipynb        # Объединение JSON-файлов с новостями из разных каналов
│   ├── Create_FAISS_index.ipynb  # Первый эксперимент по созданию эмбеддингов и индекса
│   ├── TelegramNewsNinja.ipynb   # Черновая версия RAG-системы для тестирования
├── scripts/                  # Основные скрипты проекта
│   ├── data_parser.py        # Скрипт для парсинга данных из Telegram-канала
│   ├── clean_data.py         # Скрипт с набором функций, для очистки и форматированая данных
│   ├── rag.py                # скрипт RAG
│   ├── News_Assistant_AI.py  # Frontend-проекта, интегрированный с Backend (rag.py)
├── requirements.txt          # Зависимости Python
├── LICENSE                   # Лицензия
└── README.md                 # Описание проекта
```

## Клонируем репозиторий
```bash
git clone https://github.com/KissedByF1re/News-Assistant-AI
cd News-Assistant-AI/scripts
```

## Установка зависимостей
```bash
pip install -r requirements.txt
```

## Запускаем проект из директории со скриптом
```bash
streamlit run .\News_Assistant_AI.py
```

## Авторы проекта
Михаил Макаров - сборка RAG-системы, интеграция с фронтом

Розанов Константин - создание парсера, сбор данных, создания фронта
