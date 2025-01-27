FROM python:3.10.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем исходный код приложения
COPY . .

# Открываем порт для Streamlit
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Запускаем Streamlit приложение
CMD ["streamlit", "run", "News_Assistant_AI.py", "--server.port=8501", "--server.address=0.0.0.0"]
#
