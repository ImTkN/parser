import csv
import time

import requests
from bs4 import BeautifulSoup


# Функция для получения HTML-контента страницы
def get_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе: {e}")
        return None


# Функция для парсинга всех данных со страницы
def parse_all_data(html):
    soup = BeautifulSoup(html, "html.parser")

    # Собираем весь текст на странице
    page_text = soup.get_text(separator=" ", strip=True)

    # Собираем все ссылки
    links = [a['href'] for a in soup.find_all('a', href=True)]

    # Собираем все изображения
    images = [img['src'] for img in soup.find_all('img', src=True)]

    return {
        "Текст": page_text,
        "Ссылки": links,
        "Изображения": images
    }


# Сохранение данных в CSV
def save_to_csv(data, filename="site_data.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Тип данных", "Содержимое"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Сохраняем текст
        writer.writerow({"Тип данных": "Текст", "Содержимое": data["Текст"]})

        # Сохраняем ссылки
        for link in data["Ссылки"]:
            writer.writerow({"Тип данных": "Ссылка", "Содержимое": link})

        # Сохраняем изображения
        for image in data["Изображения"]:
            writer.writerow({"Тип данных": "Изображение", "Содержимое": image})


# Основная функция для итерации по страницам
def main():
    # Запрашиваем начальный URL у пользователя, используя `{}` как маркер для подстановки номера страницы
    base_url = input("Введите URL сайта для парсинга (например, https://example.com/page={}): ")

    # Проверка, что в URL содержится маркер `{}`, куда будет подставлен номер страницы
    if '{}' not in base_url:
        print("Пожалуйста, убедитесь, что в URL присутствует `{}` для подстановки номера страницы.")
        return

    page = 1
    all_data = {
        "Текст": "",
        "Ссылки": [],
        "Изображения": []
    }

    while True:
        print(f"Парсинг страницы {page}...")
        url = base_url.format(page)
        html = get_html(url)

        # Проверка на наличие контента на странице
        if not html:
            print("Ошибка загрузки страницы или достигнут конец.")
            break

        page_data = parse_all_data(html)

        # Если на странице нет данных, прекращаем цикл
        if not page_data["Текст"] and not page_data["Ссылки"] and not page_data["Изображения"]:
            print("Достигнут конец сайта.")
            break

        # Объединяем данные со всех страниц
        all_data["Текст"] += " " + page_data["Текст"]
        all_data["Ссылки"].extend(page_data["Ссылки"])
        all_data["Изображения"].extend(page_data["Изображения"])

        page += 1  # Переход к следующей странице
        time.sleep(1)  # Задержка, чтобы не нагружать сайт

    # Сохранение всех данных в CSV
    save_to_csv(all_data)
    print("Данные успешно сохранены в site_data.csv")


if __name__ == "__main__":
    main()
