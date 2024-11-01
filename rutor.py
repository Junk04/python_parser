import requests 
from bs4 import BeautifulSoup
import json

# Преобразуем строку, содержащюю количество сообщений, в число
def parse_numeric(string):
    if 'K' in string:
        number = float(string.replace('K', '').replace(',', '').strip()) * 1000
    elif 'M' in string:
        number = float(string.replace('M', '').replace(',', '').strip()) * 1000000
    else:
        number = float(string.replace(',', '').strip())
    return int(number) if number.is_integer() else number


url = "https://rutor8.com"


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
}


response = requests.get(url, headers=headers)

# Сохраняем ответ в бинарном формате
with open("response.bin", "wb") as file:
    file.write(response.content)

# Чтение бинарного файла и попытка его декодирования в HTML
try:
    with open("response.bin", "rb") as bin_file:
        binary_content = bin_file.read()

    html_content = binary_content.decode('utf-8', errors='replace')

    with open("response.html", "w", encoding='utf-8') as html_file:
        html_file.write(html_content)

except Exception as e:
    print(f"Произошла ошибка: {e}")



with open("response.html", encoding='utf-8') as file:
    src = file.read()

soup = BeautifulSoup(src, 'lxml')

data = []

# Ищем все контейнеры категории
all_container = soup.find_all(class_="block-container")

for container in all_container:
    # Извлекаем название категории
    category_name = None
    header = container.find(class_="block-header--left")
    if header:
        link = header.find("a")
        if link:
            category_name = link.get_text(strip=True)
    
    # Извлекаем разделы в данной категории
    sections = []
    titles = container.find_all("h3", class_="node-title")
    for title in titles:
        section_link = title.find("a")
        if section_link:
            section_name = section_link.get_text(strip=True)

            # Извлекаем количество тем и сообщений
            node_meta = title.find_next_sibling(class_="node-meta")
            topics = messages = None
            if node_meta:
                # Получаем количество тем
                topics_tag = node_meta.find("dt", string="Темы")
                if topics_tag:
                    topics = topics_tag.find_next("dd").get_text(strip=True)
                    topics = parse_numeric(topics)

                # Получаем количество сообщений
                messages_tag = node_meta.find("dt", string="Сообщения")
                if messages_tag:
                    messages = messages_tag.find_next("dd").get_text(strip=True)
                    messages = parse_numeric(messages)

            # Добавляем информацию о разделе
            sections.append({
                "name": section_name,
                "topics": topics,
                "messages": messages
            })

    # Добавляем категорию с разделами, если найдена категория и хотя бы один раздел
    if category_name and sections:
        data.append({
            "category": category_name,
            "sections": sections
        })


json_data = json.dumps(data, ensure_ascii=False, indent=4)

with open("output.json", "w", encoding='utf-8') as f:
    f.write(json_data)


with open("output.json", 'r', encoding='utf-8') as file:
    data = json.load(file)

# Словарь для хранения количества сообщений в каждой категории
category_messages = {}

# Подсчет сообщений в каждой категории
for category in data:
    total_messages = 0
    for section in category['sections']:
        messages = section['messages']
        if messages is not None:
            total_messages += messages
    category_messages[category['category']] = total_messages

# Сортировка категорий по количеству сообщений в порядке убывания
sorted_categories = sorted(category_messages.items(), key=lambda item: item[1], reverse=True)


message_count = 0
for category, total in sorted_categories:
    print(f"Категория: '{category}', Количество сообщений: {total}")
    message_count += total

print(f'\nОбщее количество сообщений на форуме: {message_count}')

