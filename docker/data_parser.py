import asyncio
from selenium import webdriver
from bs4 import BeautifulSoup
import json
import time
import os
from concurrent.futures import ThreadPoolExecutor
from clean_data import *


# Функция для загрузки JSON-файла
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# Функция для сохранения JSON-файла
def save_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# Функция для мерджа новостей без дубликатов (по тексту)
def merge_news(old_news, new_news):
    seen_texts = {news["text"] for news in old_news}
    merged_news = old_news.copy()

    for news in new_news:
        if news["text"] not in seen_texts:
            merged_news.append(news)
            seen_texts.add(news["text"])

    return merged_news


def fetch_channel_data(channel_url: str, max_scrolls: int, output_path: str):
    '''
    Эта функция открывает браузер, прокручивает страницу и подгружает новости

    channel_url (str): Адрес канала
    max_scrolls (int): Максимальное количество прокруток страницы, которое мы задаем
    output_path (str): Путь куда сохранять новости

    '''
    if channel_url == "https://t.me/s/rian_ru":
        channel_name = "РИА Новости"
    else:
        channel_name = "Мэш Новости"

    # Настройка WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(channel_url)
        time.sleep(1)

        scroll_count = 0
        last_message_count = 0
        no_new_messages = 0

        while scroll_count < max_scrolls:
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            messages = soup.find_all("div", class_="tgme_widget_message_text")
            current_message_count = len(messages)

            print(f"{channel_name}: прокрутка №{scroll_count + 1}, сообщений: {current_message_count}")

            if current_message_count == last_message_count:
                no_new_messages += 1
                if no_new_messages > 3:
                    print(f"[{channel_name}] Сообщения больше не подгружаются.")
                    break
            else:
                no_new_messages = 0

            last_message_count = current_message_count
            scroll_count += 1

        # Парсим новости
        soup = BeautifulSoup(driver.page_source, "html.parser")
        messages = soup.find_all("div", class_="tgme_widget_message")

        data = []
        for message in messages:
            text_element = message.find("div", class_="tgme_widget_message_text")
            text = text_element.get_text(strip=True) if text_element else None

            date_element = message.find("time")
            raw_date = date_element.get("datetime") if date_element else None

            link_element = message.find("a", class_="tgme_widget_message_date")
            link = link_element.get("href") if link_element else None

            if text:
                data.append({
                    "text": text,
                    "datetime": raw_date,
                    "link": link
                })

        unique_data = {entry["text"]: entry for entry in data}.values()

        for entry in unique_data:
            # Обновляем форматы даты
            if entry["datetime"]:
                entry["datetime"] = format_date(entry["datetime"])
            # Очищаем текстовые сообщения
            entry["text"] = clean_text(entry.get("text", ""))

        # Сохраняем новости в формате JSON
        save_json(data, output_path)

    finally:
        driver.quit()


async def main():
    max_scrolls = int(input("Введите число прокруток страницы: "))
    directory_path = input("Введите путь для сохранения JSON-файла с новостями: ")

    channels = [
        {"url": "https://t.me/s/rian_ru", "output_path": f"{directory_path}/ria_news_test.json"},
        {"url": "https://t.me/s/mash", "output_path": f"{directory_path}/mash_news_test.json"}
    ]

    # ThreadPoolExecutor для выполнения парсинга параллельно, так как Selenium не поддерживаем асинхронность
    with ThreadPoolExecutor(max_workers=len(channels)) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                executor,
                fetch_channel_data,
                channel["url"],
                max_scrolls,
                channel["output_path"]
            )
            for channel in channels
        ]
        await asyncio.gather(*tasks)

    # Открываем наши JSON файлы, чтобы их объединить в один
    ria_path = channels[0]["output_path"]
    mash_path = channels[1]["output_path"]
    output_path = f"{directory_path}/combined_news_new.json"

    data_mash = load_json(mash_path)
    data_ria = load_json(ria_path)

    # Объединяем данные
    combined_data = data_mash + data_ria

    # Сохранение объединенных данных в новый файл
    save_json(combined_data, output_path)

    # Удаляем теперь уже ненужные файлы
    os.remove(ria_path)
    os.remove(mash_path)
    print(f"Собрано новых сообщений: {len(combined_data)}")

    old_news_path = f"{directory_path}/combined_news.json"
    merged_news_path = f"{directory_path}/merged_news.json"

    # Загрузка данных
    old_news = load_json(old_news_path)
    new_news = load_json(output_path)

    # Мердж данных
    merged_news = merge_news(old_news, new_news)

    # Сохранение результата
    save_json(merged_news, merged_news_path)


if __name__ == "__main__":
    asyncio.run(main())
