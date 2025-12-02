import sys
import re
from datetime import datetime
from typing import List, Optional, Dict

# Текущая дата для расчёта возраста
TODAY = datetime.today()
CURRENT_YEAR = TODAY.year

def normalize_date(date_str: str) -> Optional[datetime]:
    """Поддерживает все форматы дат из условия, включая однозначные день/месяц"""
    date_str = date_str.strip()
    
    # Поддерживаемые разделители: ., -, /
    patterns = [
        r'^(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})$'
    ]
    
    for pattern in patterns:
        match = re.match(pattern, date_str)
        if not match:
            continue
        
        day_str, month_str, year_str = match.groups()
        try:
            day = int(day_str)
            month = int(month_str)
            year = int(year_str)
        except ValueError:
            return None
        
        # Проверка диапазонов
        if not (1900 <= year <= CURRENT_YEAR):
            return None
        if not (1 <= month <= 12):
            return None
        if not (1 <= day <= 31):
            return None
        
        # Проверка реальной даты (например, 31.04 — невалидно)
        try:
            dt = datetime(year, month, day)
            return dt
        except ValueError:
            return None
    
    return None


def is_valid_name(text: str) -> bool:
    """Имя и фамилия: с заглавной буквы, только кириллица"""
    return bool(re.match(r'^[А-ЯЁ][а-яё]+(-[А-ЯЁ][а-яё]+)?$', text.strip()))


def is_valid_gender(gender: str) -> bool:
    """Поддерживаемые варианты пола"""
    g = gender.strip().lower()
    return g in ['м', 'ж', 'мужской', 'женский']


def is_valid_contact(contact: str) -> bool:
    """Телефон (11 цифр, начинается с 8 или +7) ИЛИ email (только указанные домены)"""
    contact = contact.strip()
    
    # === Проверка телефона ===
    # Убираем все нецифровые символы
    digits_only = re.sub(r'\D', '', contact)
    
    # Должно быть ровно 11 цифр и начинаться на 7 или 8
    if len(digits_only) == 11 and digits_only[0] in '78':
        return True
    
    # Допустимые "красивые" форматы
    phone_patterns = [
        r'^\+7\s*\(\d{3}\)\s*\d{3}-\d{2}-\d{2}$',
        r'^8\s*\(\d{3}\)\s*\d{3}-\d{2}-\d{2}$',
        r'^\d{11}$',
        r'^8\s*\d{3}\s*\d{3}\s*\d{2}\s*\d{2}$',
        r'^8\s*\(\d{3}\)\s*\d{3}\s*\d{2}\s*\d{2}$',
    ]
    if any(re.match(p, contact.replace(' ', '')) for p in phone_patterns):
        cleaned = re.sub(r'\D', '', contact)
        if len(cleaned) == 11 and cleaned.startswith(('7', '8')):
            return True
    
    # === Проверка email ===
    email_pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]{1,64}@(gmail\.com|mail\.ru|yandex\.ru)$',
        re.IGNORECASE
    )
    if email_pattern.match(contact):
        return True
    
    return False


def is_valid_city(city: str) -> bool:
    """Город: Москва или г. Москва, Санкт-Петербург или г. Санкт-Петербург и т.д."""
    city = city.strip()
    pattern = r'^(г\. )?([А-ЯЁ][а-яё]+)(\s[А-ЯЁ][а-яё]+)*$'
    return bool(re.match(pattern, city))


def parse_person_block(block_lines: List[str]) -> Optional[Dict]:
    """Парсит блок из 6 строк в данные человека, если всё валидно"""
    lines = [line.strip() for line in block_lines if line.strip()]
    
    if len(lines) < 6:
        return None
    
    surname = lines[0]
    name = lines[1]
    gender = lines[2]
    birth_date_str = lines[3]
    contact = lines[4]
    city = lines[5]
    
    # Валидация всех полей
    if not (is_valid_name(surname) and is_valid_name(name)):
        return None
    if not is_valid_gender(gender):
        return None
    birth_date = normalize_date(birth_date_str)
    if not birth_date:
        return None
    if not is_valid_contact(contact):
        return None
    if not is_valid_city(city):
        return None
    
    # Точный расчёт возраста
    age = TODAY.year - birth_date.year
    if (TODAY.month, TODAY.day) < (birth_date.month, birth_date.day):
        age -= 1
    
    return {
        'surname': surname,
        'name': name,
        'gender': gender,
        'birth_date': birth_date,
        'contact': contact,
        'city': city,
        'age': age,
        'original_lines': block_lines  # сохраняем с пустыми строками и отступами
    }


def main():
    if len(sys.argv) != 2:
        print("Использование: python lab.py data.txt")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Ошибка: файл '{filename}' не найден!")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
        sys.exit(1)
    
    # Разделяем на блоки анкет (по пустой строке или двойному переносу)
    raw_blocks = re.split(r'\n\s*\n', content.strip())
    
    valid_people = []
    
    for block in raw_blocks:
        lines = block.split('\n')
        person = parse_person_block(lines)
        if person:
            valid_people.append(person)
    
    if not valid_people:
        print("Не найдено ни одной полностью валидной анкеты!")
        return
    
    # Находим самого старого и самого молодого
    oldest = max(valid_people, key=lambda p: p['age'])
    youngest = min(valid_people, key=lambda p: p['age'])
    
    print("САМЫЙ СТАРЫЙ ЧЕЛОВЕК")
    print(f"Возраст: {oldest['age']} лет")
    print("Анкета:")
    print('\n'.join(oldest['original_lines']).strip())
    
    print("\n" + "="*50 + "\n")
    
    print("САМЫЙ МОЛОДОЙ ЧЕЛОВЕК")
    print(f"Возраст: {youngest['age']} лет")
    print("Анкета:")
    print('\n'.join(youngest['original_lines']).strip())


if __name__ == "__main__":
    main()