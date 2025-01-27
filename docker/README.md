**Порядок запуска:**
0. Положить файл .env с переменой `OPENAI_API_KEY` в корень проекта
1. `docker build -t tgbot .`
2. `docker run -d -p 8000:8000 tgbot`

