import argparse, csv
from tabulate import tabulate
import statistics as stat

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--files', nargs='*', type=str, help='Название файлов')
parser.add_argument('-r', '--report', type=str, help='Название отчета')
args = parser.parse_args()

# print(args.files)
# print(args.report)

dct = {}
for file in args.files:
    with open(file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)

        # print(reader)

        for row in enumerate(reader,0):

            # print(row)

            if row[0] == 0:
                continue
            else:
                lst = list(row[1])

            # print(lst)

            if lst[0] in dct:
                dct[lst[0]].append(lst[2])
            else:
                dct[lst[0]] = [lst[2]]

# print(dct)

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