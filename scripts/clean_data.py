from datetime import datetime
import re


def clean_text(text: str):
    '''
    Функция удаляет мусор из сообщений - эмодзи, лишние пробелы
    text (str): Текстовое сообщение из поста
    return (str): Очищенное сообщение
    '''
    if not text:
        return text
    text = re.sub(r"[^\w\s,.!?\"'-]", " ", text)

    # Удаление лишних пробелов
    text = re.sub(r"\s+", " ", text).strip()
    return text


def format_date(date_str: str):
    '''
    Функция переводит формат даты в привычный вид
    date_str (str): Дата в питонячем формате
    return (str): Дата в привычном формате
    '''
    try:
        date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return date_obj.strftime("%d-%m-%Y %H:%M:%S")
    except Exception as e:
        print(f"Ошибка форматирования даты {date_str}: {e}")
        return date_str
