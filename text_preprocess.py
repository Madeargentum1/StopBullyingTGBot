import inspect
import re

import pymorphy2
from nltk import word_tokenize
from nltk.corpus import stopwords
from sklearn.base import BaseEstimator, TransformerMixin


if not hasattr(inspect, 'getargspec'):
    def getargspec(func):
        full = inspect.getfullargspec(func)
        return full.args, full.varargs, full.varkw, full.defaults
    inspect.getargspec = getargspec


stop_words = set(stopwords.words('russian'))
morph = pymorphy2.MorphAnalyzer()


class TextPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self, method='lemmatize'):
        self.method = method

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        processed = []
        for text in X:
            clean = clean_text(text)
            if self.method == 'lemmatize':
                processed.append(lemmatize(clean))
            else:
                processed.append(clean)
        return processed


def clean_text(text):
    # Удаляем эмодзи и спец. символы юникода
    # text = ''.join(c for c in text if not unicodedata.category(c).startswith('So'))
    # Удаляем Telegram-теги пользователей
    text = re.sub(r'@\w{1,32}', '', text)
    text = re.sub(r'<@!?\d+>', '', text)  # Discord ID ping
    # Удаляем переносы строк
    text = text.replace('\n', ' ')
    # Общая чистка, только буквы
    # text = re.sub(r'[^A-Za-zА-Яа-яЁё\s]', ' ', text)
    text = re.sub(r'[^а-яё\s]', ' ', text)
    # Удаляем лишние пробелы
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()


def lemmatize(text):
    tokens = word_tokenize(text, language='russian')
    lemmas = [morph.parse(tok)[0].normal_form for tok in tokens if tok not in stop_words and len(tok) > 2]
    return ' '.join(lemmas)


def telegram_is_bot_message(msg):
    from_name_div = msg.find('div', class_='from_name')
    if not from_name_div:
        return False
    name = from_name_div.get_text(strip=True)
    known_bots = [
        'Komaru Cards',
        '888 Cards',
        'Iris | Moonlight Dyla',
        'Bitget Wallet Support',
        'New bot -> @eightclub8000bot',
        'RazeChatBot',
        'Москва сейчас',
        'Combot',
        'Telegram Analytics Bot',
        'Protectron',
        'NameFilterBot',
        'No PM Bot',
        'DeFensy 🛡⚔️ AntiSpamBot',
        'MILANA TARBA Цифровой Психолог',
        'Антимат',
        'Антиспам',
        'Mobile Legends: Bang Bang',
    ]
    return any(bot in name for bot in known_bots)


def text_contains_trash(msg: str):
    trash_content = ['так ты с ботом что лиа', '[', '{', 'бан', 'кик', 'мут']
    trash_start = ['ирис', 'погода', 'камар', 'комар', 'карта', 'стат', '888', 'рулетка', 'дуэль', 'команда']
    for i in trash_start:
        if msg.startswith(i):
            return True
    for i in trash_content:
        if i in msg:
            return True
    return False
