from selenium import webdriver
import time
import json
from bs4 import BeautifulSoup


channel_url = "https://t.me/s/rian_ru"

# Настройка WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

driver.get(channel_url)
time.sleep(1)

# Прокрутка страницы вверх
scroll_count = 0
max_scrolls = 500
last_position = None
last_message_count = 0
no_new_messages = 0

while True:
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)

    # Проверяем количество сообщений
    soup = BeautifulSoup(driver.page_source, "html.parser")
    messages = soup.find_all("div", class_="tgme_widget_message_text")
    current_message_count = len(messages)

    print(f"Прокрутка #{scroll_count + 1}, сообщений: {current_message_count}")

    if current_message_count == last_message_count:
        no_new_messages += 1
        if no_new_messages > 3:
            print("Сообщения больше не подгружаются.")
            break
    else:
        no_new_messages = 0

    last_message_count = current_message_count
    scroll_count += 1

    if scroll_count >= max_scrolls:
        print("Достигнуто максимальное количество прокруток.")
        break

# Парсим данные
soup = BeautifulSoup(driver.page_source, "html.parser")
messages = soup.find_all("div", class_="tgme_widget_message")

data = []
for message in messages:
    # Извлекаем текст сообщения
    text_element = message.find("div", class_="tgme_widget_message_text")
    text = text_element.get_text(strip=True) if text_element else None

    # Извлекаем дату
    date_element = message.find("time")
    raw_date = date_element.get("datetime") if date_element else None

    # Извлекаем ссылку
    link_element = message.find("a", class_="tgme_widget_message_date")
    link = link_element.get("href") if link_element else None

    # Добавляем сообщение в список
    if text:
        data.append({
            "text": text,
            "datetime": raw_date,
            "link": link
        })

with open("../data/raw/ria_news.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"Скачано сообщений: {len(data)}")
driver.quit()
