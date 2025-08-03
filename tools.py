import csv
import os
import re
from collections import defaultdict

import joblib


FP_PATH = r"E:\PycharmProjects\detectbully\false_positives.csv"
FN_PATH = r"E:\PycharmProjects\detectbully\false_negatives.csv"
USER_STATS_DB = "user_stats.csv"
CSV_FILENAME = "moderation_results.csv"
MODEL_PATH = "model.pkl"
model = joblib.load(r"E:\PycharmProjects\detectbully\bullying_detector_model.pkl")

user_buffers = {}
user_stats = defaultdict(int)
pending_texts = {}


def is_bullying(text: str) -> bool:
    return bool(model.predict([text])[0])


def save_to_csv(text: str, label: int):
    with open(CSV_FILENAME, mode="a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([text, label])


def update_user_stats(user_id: int):
    user_stats[user_id] += 1
    with open(USER_STATS_DB, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['user_id', 'count'])
        for uid, count in user_stats.items():
            writer.writerow([uid, count])


def load_samples():
    texts = set()
    for path in [FP_PATH, FN_PATH]:
        if os.path.exists(path):
            with open(path, encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        texts.add(row[0])
    return list(texts)


def clean_text(text):
    # Удаляем эмодзи и спец. символы юникода
    # text = ''.join(c for c in text if not unicodedata.category(c).startswith('So'))
    # Удаляем Telegram-теги пользователей
    text = re.sub(r'@\w{1,32}', '', text)
    text = re.sub(r'<@!?\d+>', '', text)  # Discord ID ping
    # Удаляем переносы строк
    text = text.replace('\n', ' ')
    # Общая чистка, только буквы и цифры
    text = re.sub(r'[^A-Za-zА-Яа-яЁё\s]', ' ', text)
    # Удаляем лишние пробелы
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()
