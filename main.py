"""Скрипт читает файлы с данными о подготовке студентов к экзаменам
    и формирует отчет, в котором будет медианная сумма трат на кофе
    по каждому студенту за весь период сессии."""

import os.path
import argparse
import csv
import statistics as stat
from tabulate import tabulate

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--files', nargs='*', type=str, help='Название файлов')
parser.add_argument('-r', '--report', type=str, help='Название отчета')
args = parser.parse_args()

dct = {}
for file in args.files:
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)

            for row in enumerate(reader, 0):

                if row[0] != 0:
                    lst = list(row[1])
                else:
                    continue

                if lst[0] in dct:
                    dct[lst[0]].append(float(lst[2]))
                else:
                    dct[lst[0]] = [float(lst[2])]
    else:
        print(f'Файл {file} не существует!')

result = []
for student, spent in dct.items():
    result.append([student, stat.median(spent)])

headers = ["student", "median_coffee"]
print(tabulate(result, headers, tablefmt="fancy_grid"))

if args.report.find('.csv') != -1:
    report = args.report
else:
    report = f'{args.report}.csv'
with open(report, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(result)
