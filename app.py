import json
import re

from flask import Flask, request, jsonify
import base64
from io import BytesIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import pandas as pd

app = Flask(__name__)


@app.route('/bank_statement/', methods=['POST'])
def process_bank_statement():
    data = request.get_json()
    encoded_pdf = data['base64-bank_statement']

    # Декодирование base64
    decoded_pdf = base64.b64decode(encoded_pdf)

    # Извлечение текста из PDF
    transactions = extract_data_from_pdf(decoded_pdf)

    # Создание JSON-ответа
    response = {
        'personal_data': {
            'name': 'John Doe',
            'account_number': '1234567890'
        },
        'transactions': transactions
    }

    return jsonify(response)


def extract_data_from_pdf(pdf_data):
    transactions = []

    # Создание объекта BytesIO для работы с данными PDF
    pdf_stream = BytesIO(pdf_data)

    # Создание ресурсного менеджера и интерпретатора PDF
    resource_manager = PDFResourceManager()
    output_string = BytesIO()
    laparams = LAParams()
    device = TextConverter(resource_manager, output_string, laparams=laparams)

    # Обработка страниц PDF-файла
    interpreter = PDFPageInterpreter(resource_manager, device)

    for page in PDFPage.get_pages(pdf_stream):
        interpreter.process_page(page)
        # print(output_string.getvalue().decode())

        # Извлечение текста с текущей страницы
        text = output_string.getvalue().decode()
        # print(text)


        # (\d{2}\.\d{2}\.\d{4})
        # r"(\d{2}\.\d{2}\.\d{4})\s+(\d{2}\.\d{2}\.\d{4}\s\d{2}:\d{2}:\d{2})"
        data_pattern = r"\d{2}\.\d{2}\.\d{4}"
        full_data_pattern = r"(\d{2}\.\d{2}\.\d{4}\s\d{2}:\d{2}:\d{2})"
        inf_about_tr = r"(\d+\.\.\d+)\s+(.*?)\s+(\d+)\s+(.*?)\s+(\d+)\. (MCC)\s+(\d+)|(Зачисление.*\nраб.*я?\)?)"
        money = r'-?\d{0,} -?\d{3}\.\d{2}'
        rx_dict = re.compile(data_pattern)
        data_matches = re.findall(data_pattern, text)
        full_data_matches = re.findall(full_data_pattern, text)
        info_about_tr_matches = re.findall(inf_about_tr, text)

        transaction_info = {}
        for match in data_matches:
            # print(match, 'mached')
            transaction_info['Дата'] = match
        for f_data_much in full_data_matches:
            transaction_info['Полная дата'] = f_data_much
        for info_tr in info_about_tr_matches:
            transaction_info['Информация о транзакции']=' '.join(list(info_tr))

            transactions.append(transaction_info)
        output_string.truncate(0)
        output_string.seek(0)
    # Закрытие объектов
    device.close()
    output_string.close()
    pdf_stream.close()

    return transactions


def get_personal_data():

    personal_data = {
        'name': 'Иван Иванов',
        'account_number': '1234567890',
        'email': 'ivan@example.com'
    }

    return personal_data


if __name__ == '__main__':
    app.run(debug=True)