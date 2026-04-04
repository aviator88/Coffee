"""Скрипт читает файлы с данными о подготовке студентов к экзаменам
    и формирует отчет, в котором будет медианная сумма трат на кофе
    по каждому студенту за весь период сессии."""

import os.path
import argparse
import csv
import statistics as stat
from tabulate import tabulate


def parse_args():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--files', nargs='*', type=str, help='Название файлов')
    parser.add_argument('-r', '--report', type=str, help='Название отчета')
    args = parser.parse_args()
    return args


def process_files(files):
    """Обработка CSV файлов и сбор данных"""
    data_dict = {}
    for file in files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)

                for row in enumerate(reader, 0):

                    if row[0] != 0:
                        lst = list(row[1])
                    else:
                        continue

                    if lst[0] in data_dict:
                        data_dict[lst[0]].append(float(lst[2]))
                    else:
                        data_dict[lst[0]] = [float(lst[2])]
        else:
            print(f'Файл {file} не существует!')
    return data_dict


def calculate_median(data_dict):
    """Вычисление медианы для каждого студента"""
    result = []
    for student, spent in data_dict.items():
        result.append([student, stat.median(spent)])
    return result


def print_table(result):
    """Вывод таблицы в консоль"""
    headers = ["student", "median_coffee"]
    print(tabulate(result, headers, tablefmt="fancy_grid"))


def generate_report(result, report_name):
    """Генерация CSV отчета"""
    if report_name.find('.csv') != -1:
        report = report_name
    else:
        report = f'{report_name}.csv'
    with open(report, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(result)


def main():
    """Основная функция"""
    args = parse_args()
    if not args.files:
        print("Ошибка: не указаны файлы для обработки")
        return

    data_dict = process_files(args.files)
    if not data_dict:
        print("Нет данных для обработки")
        return

    result = calculate_median(data_dict)
    print_table(result)

    if args.report:
        generate_report(result, args.report)


if __name__ == "__main__":
    main()
