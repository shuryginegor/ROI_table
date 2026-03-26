from flask import Flask, render_template, request, jsonify
import logging
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


def get_filtered_data(search_query):
    url = "https://nerc.itmo.ru/school/archive/2025-2026/ru-olymp-roi-2026-standings.html"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ищем именно таблицу с результатами
        table = soup.find('table', class_='standings')
        if not table:
            table = soup.find('table')  # Если класс другой, берем первую попавшуюся

        all_rows = []
        for row in table.find_all('tr'):
            # Извлекаем текст ячеек, разделяя вложенные теги пробелом
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all(['td', 'th'])]
            if cells:
                all_rows.append(cells)

        if not all_rows:
            return [["Данные не найдены"]]

        # Шапка (Место, Участник, Баллы...) — обычно первая строка
        header = all_rows[0]
        end = all_rows[-2:]

        # Фильтруем данные (пропускаем заголовок)
        # Ищем по ВСЕЙ строке, чтобы не ошибиться с индексом столбца
        query = search_query.lower()
        filtered = [
            r for r in all_rows[1:-2]
            if query in str(r[1]).lower()
        ]

        # Возвращаем заголовок + отфильтрованные строки
        return [header] + filtered + end

    except Exception as e:
        logging.error(e)
        return [[f"Error: {e}"]]


@app.route('/')
def index():
    # Просто отдаем пустую страницу с JS
    return render_template('index.html')


@app.route('/api/data')
def api_data():
    query = request.args.get('filter', '')
    url = "https://nerc.itmo.ru"
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = "https://nerc.itmo.ru/school/archive/2025-2026/ru-olymp-roi-2026-standings.html"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ищем именно таблицу с результатами
        table = soup.find('table', class_='standings')
        if not table:
            table = soup.find('table')  # Если класс другой, берем первую попавшуюся

        all_rows = []
        threshold = 400
        if len(all_rows) >= 220:  # +1 за заголовок
            score_219 = int(all_rows[219][-1])
            threshold = max(score_219, 400)
        for row in table.find_all('tr'):
            # Извлекаем текст ячеек, разделяя вложенные теги пробелом
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all(['td', 'th'])]
            if cells:
                all_rows.append(cells)

        if not all_rows:
            return [["Данные не найдены"]]

        # Шапка (Место, Участник, Баллы...) — обычно первая строка
        header = all_rows[0]
        end = all_rows[-2:]

        # Фильтруем данные (пропускаем заголовок)
        # Ищем по ВСЕЙ строке, чтобы не ошибиться с индексом столбца
        query = query.lower()
        filtered = [
            r for r in all_rows[1:-2]
            if query in str(r[1]).lower()
        ]

        # Возвращаем заголовок + отфильтрованные строки
        return jsonify({
            "table": [header] + filtered + end,
            "threshold": threshold
        })

    except Exception as e:
        logging.error(e)
        return jsonify({"table": [[f"Error: {e}"]], "threshold": 0})



if __name__ == '__main__':
    app.run(hostd="0.0.0.0", port=5000)
