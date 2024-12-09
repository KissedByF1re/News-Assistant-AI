from pathlib import Path
from datetime import datetime
import json
import re



input_file_path = "../data/raw/mash_news.json"
output_file_path = "../data/cleaned/mash_news_cleaned.json"


def clean_text(text):
    if not text:
        return text
    text = re.sub(r"[^\w\s,.!?\"'-]", " ", text)
    # Удаление лишних пробелов
    text = re.sub(r"\s+", " ", text).strip()
    return text



def format_date(date_str):
    try:
        date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return date_obj.strftime("%d-%m-%Y %H:%M:%S")
    except Exception as e:
        print(f"Ошибка форматирования даты {date_str}: {e}")
        return date_str



with open(input_file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

unique_data = {entry["text"]: entry for entry in data}.values()

print(f"Всего сообщений: {len(data)}")
print(f"Уникальных сообщений: {len(unique_data)}")

for entry in unique_data:
    if "datetime" in entry and entry["datetime"]:
        entry["datetime"] = format_date(entry["datetime"])
    entry["text"] = clean_text(entry.get("text", ""))

with open(output_file_path, "w", encoding="utf-8") as f:
    json.dump(list(unique_data), f, ensure_ascii=False, indent=4)
