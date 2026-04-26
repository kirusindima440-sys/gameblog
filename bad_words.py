import re

# Шаблоны для поиска (ловим корни слов)
BAD_WORDS_PATTERNS = [
    r'бл[яю]',           # бля, блю
    r'бля[дт]',          # бляд, блят
    r'сук[ау]',          # сука, суку
    r'пизд[аоуыеи]',     # пизда, пизду, пизде
    r'ху[йеёи]',         # хуй, хуе, хуё
    r'ху[яю]',           # хуя, хую
    r'еба[тнс]',         # ебат, ебан, ебас
    r'еб[ау]',           # еба, ебу
    r'мудак',            # мудак
    r'шлюх[аи]',         # шлюха, шлюхи
    r'гандон',           # гандон
    r'пид[оа]р',         # пидор, пидар
    r'fuck',             # fuck
    r'shit',             # shit
    r'bitch',            # bitch
    r'asshole',          # asshole
    r'dick',             # dick
]

# Компилируем всё в один быстрый поиск
BAD_WORDS_REGEX = re.compile('|'.join(BAD_WORDS_PATTERNS), re.IGNORECASE)

# Замена подозрительных символов (обход фильтра)
LEET_REPLACEMENTS = {
    '@': 'а',
    '#': '',
    '$': 's',
    '0': 'о',
    '1': 'и',
    '3': 'е',
    '4': 'ч',
    '5': 'с',
    '6': 'б',
    '7': 'т',
    '8': 'в',
    '9': 'д',
    '?': '',
    '!': '',
    '*': '',
}


def normalize_text(text):
    """Заменяет подозрительные символы на обычные буквы"""
    if not text:
        return text
    text_lower = text.lower()
    for leet, normal in LEET_REPLACEMENTS.items():
        text_lower = text_lower.replace(leet, normal)
    return text_lower


def contains_bad_words(text):
    """
    Проверяет, есть ли в тексте неприличные слова.
    Возвращает True, если есть мат, иначе False.
    """
    if not text:
        return False
    
    # Нормализуем текст (заменяем @ → а, # → "" и т.д.)
    normalized = normalize_text(text)
    
    # Ищем совпадения по шаблонам
    if BAD_WORDS_REGEX.search(normalized):
        return True
    
    return False


# Тесты (для проверки)
if __name__ == '__main__':
    test_phrases = [
        ("Ты бля", True),
        ("Сук@", True),
        ("Всё отлично", False),
        ("Какой хyi", True),
        ("pizda", True),
        ("fuck you", True),
        ("Нормальный обзор", False),
    ]
    
    for phrase, expected in test_phrases:
        result = contains_bad_words(phrase)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{phrase}' → {result} (ожидалось {expected})")