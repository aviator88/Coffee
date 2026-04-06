"""Заходит тестировщик-автоматизатор в бар.
   Заказывает кружку пива, 0 кружек, 999999999 кружек, -1 кружку.
   Заказывает undefined.
   Заказывает null. Тут заходит реальный пользователь, спрашивает, где ттуалет.
   Бар сгорает в адском пламени, убивая всех вокруг,
   так как автоматизатор не учел пользовательский сценарий."""

import os
import csv
import tempfile
from unittest.mock import patch
import pytest
import coffee_analyzer as ca


# Фикстура для создания временных CSV файлов
@pytest.fixture
def temp_csv_files():
    """Создание временных CSV файлы с тестовыми данными"""
    file_paths = []

    # Данные для файла 1
    data1 = [
        ['student', 'date', 'coffee_spent', 'sleep_hours', 'study_hours', 'mood', 'exam'],
        ['Алексей Смирнов', '2024-06-01', '450', '4.5', '12', 'норм', 'Математика'],
        ['Алексей Смирнов', '2024-06-02', '500', '4.0', '14', 'устал', 'Математика'],
        ['Алексей Смирнов', '2024-06-03', '550', '3.5', '16', 'зомби', 'Математика'],
        ['Дарья Петрова', '2024-06-01', '200', '7.0', '6', 'отл', 'Математика'],
        ['Дарья Петрова', '2024-06-02', '250', '6.5', '8', 'норм', 'Математика'],
        ['Дарья Петрова', '2024-06-03', '300', '6.0', '9', 'норм', 'Математика'],
        ['Иван Кузнецов', '2024-06-01', '600', '3.0', '15', 'зомби', 'Математика'],
        ['Иван Кузнецов', '2024-06-02', '650', '2.5', '17', 'зомби', 'Математика'],
        ['Алексей Смирнов', '2024-06-03', '700', '2.0', '18', 'не выжил', 'Математика'],
    ]

    # Данные для файла 2
    data2 = [
        ['student', 'date', 'coffee_spent', 'sleep_hours', 'study_hours', 'mood', 'exam'],
        ['Алексей Смирнов', '2024-06-06', '480', '4.0', '13', 'устал', 'Физика'],
        ['Алексей Смирнов', '2024-06-07', '530', '3.5', '15', 'зомби', 'Физика'],
        ['Алексей Смирнов', '2024-06-08', '580', '3.0', '17', 'зомби', 'Физика'],
        ['Дарья Петрова', '2024-06-06', '280', '6.5', '7', 'норм', 'Физика'],
        ['Дарья Петрова', '2024-06-07', '310', '6.0', '8', 'устал', 'Физика'],
        ['Дарья Петрова', '2024-06-08', '340', '5.5', '9', 'устал', 'Физика'],
        ['Дарья Петрова', '2024-06-06', '650', '2.5', '16', 'зомби', 'Физика'],
        ['Иван Кузнецов', '2024-06-07', '700', '2.0', '18', 'не выжил', 'Физика'],
        ['Алексей Смирнов', '2024-06-08', '750', '1.5', '20', 'труп', 'Физика'],
    ]

    # Данные для пустого файла (только заголовок)
    data3 = [
        ['student', 'date', 'coffee_spent', 'sleep_hours', 'study_hours', 'mood', 'exam'],
    ]

    # Создаем временные файлы
    for i, data in enumerate([data1, data2, data3]):
        fd, path = tempfile.mkstemp(suffix='.csv', prefix=f'test_{i}_')
        with os.fdopen(fd, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)
        file_paths.append(path)

    yield file_paths

    # Очистка
    for path in file_paths:
        if os.path.exists(path):
            os.remove(path)


@pytest.fixture
def temp_output_dir():
    """Создание временной директтории для отчетов"""
    with tempfile.TemporaryDirectory() as tmpdir:
        return tmpdir


# === Happy Path тесты ===

def test_hp_process_files(temp_csv_files):
    """Тест happy-path обработки файлов"""
    files = temp_csv_files[:2]  # используем первые два файла с данными
    result = ca.process_files(files)

    assert isinstance(result, dict)
    assert len(result) == 3  # Алексей Смирнов, Дарья Петрова, Иван Кузнецов
    assert 'Алексей Смирнов' in result
    assert 'Дарья Петрова' in result
    assert 'Иван Кузнецов' in result
    assert result['Алексей Смирнов'] == [450, 500, 550, 700, 480, 530, 580, 750]  # из обоих файлов
    assert result['Дарья Петрова'] == [200, 250, 300, 280, 310, 340, 650]
    assert result['Иван Кузнецов'] == [600, 650, 700]


def test_hp_calculate_median():
    """Тест расчета медианы"""
    data = {
        'Алексей Смирнов': [450, 500, 550, 700, 480, 530, 580, 750],
        'Дарья Петрова': [200, 250, 300, 280, 310, 340, 650],
        'Иван Кузнецов': [600, 650, 700]
    }
    result = ca.calculate_median(data)

    expected = [
        ['Алексей Смирнов', 540],       # (530 + 550) / 2
        ['Дарья Петрова', 300],
        ['Иван Кузнецов', 650]
    ]
    assert result == expected


@patch('builtins.print')
def test_hp_print_table(mock_print):
    """Тест вывода таблицы"""
    result_data = [['Алексей Смирнов', 540], ['Дарья Петрова', 300], ['Иван Кузнецов', 650]]
    ca.print_table(result_data)
    mock_print.assert_called_once()
    call_args = mock_print.call_args[0][0]

    assert 'Алексей Смирнов' in call_args
    assert 'Дарья Петрова' in call_args
    assert 'Иван Кузнецов' in call_args
    assert '540' in call_args
    assert '300' in call_args
    assert '650' in call_args


def content_read(file):
    """Небольшая функция для чтения содержимого файлаБ чтобы 2 раза не повторяться"""
    with open(file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)
        return data


def test_hp_generate_report(temp_output_dir):
    """Тест генерации отчета"""
    result_data = [
        ['Алексей Смирнов', 540],
        ['Дарья Петрова', 300],
        ['Иван Кузнецов', 650]
    ]
    report_name = os.path.join(temp_output_dir, 'test_report')

    # Тест без расширения
    report_path = ca.generate_report(result_data, report_name)
    assert report_path == f'{report_name}.csv'
    assert os.path.exists(report_path)

    # Проверяем содержимое
    data = content_read(report_path)
    assert data == [['Алексей Смирнов', '540'], ['Дарья Петрова', '300'], ['Иван Кузнецов', '650']]

    # Тест с расширением
    report_name_ext = os.path.join(temp_output_dir, 'report_with_ext.csv')
    report_path_ext = ca.generate_report(result_data, report_name_ext)
    assert report_path_ext == report_name_ext
    assert os.path.exists(report_path_ext)

    # Проверяем содержимое
    data = content_read(report_path_ext)
    assert data == [['Алексей Смирнов', '540'], ['Дарья Петрова', '300'], ['Иван Кузнецов', '650']]


# === EDGE CASES ===
def test_ec_process_files_wmf(capsys):  # wmf - with missing file
    """Тест обработки несуществующего файла"""
    result = ca.process_files(['nonexistent_file.csv'])

    assert result == {}  # пустой словарь
    captured = capsys.readouterr()
    assert 'Файл nonexistent_file.csv не существует!' in captured.out


def test_ec_process_files_wef(temp_csv_files):  # wef - with empty file
    """Тест обработки файла только с заголовком"""
    files = [temp_csv_files[2]]  # файл только с заголовком
    result = ca.process_files(files)

    assert result == {}  # нет данных о студентах


def test_ec_process_files_wmc(temp_csv_files):  # wmc - with mixed content
    """Тест обработки смешанных данных (существующие и отсутствующие файлы)"""
    existing_file = temp_csv_files[0]
    missing_file = 'missing.csv'

    with patch('builtins.print') as mock_print:
        result = ca.process_files([existing_file, missing_file])

        assert 'Алексей Смирнов' in result
        assert 'Дарья Петрова' in result
        assert 'Иван Кузнецов' in result
        mock_print.assert_called_with(f'Файл {missing_file} не существует!')


def test_ec_calculate_median_wsv():     # wsv - with single value
    """Тест медианы для одного значения"""
    data = {'СтудентФИО': [100]}
    result = ca.calculate_median(data)
    assert result == [['СтудентФИО', 100]]


def test_ec_calculate_median_wec():     # wec - with even count
    """Тест медианы для четного количества значений"""
    data = {'СтудентФИО': [100, 200, 300, 400]}
    result = ca.calculate_median(data)
    assert result == [['СтудентФИО', 250]]  # (200 + 300) / 2


def test_ec_generate_report_wod(temp_output_dir):   # wod - without data
    """Тест генерации пустого отчета"""
    result_data = []
    report_name = os.path.join(temp_output_dir, 'empty_report')

    report_path = ca.generate_report(result_data, report_name)
    assert os.path.exists(report_path)

    # Проверяем, что файл пустой
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert content == '' or len(content.strip()) == 0


# === PARAMETRIZED TESTS ===

@pytest.mark.parametrize('file_content, expected_result', [
   (
            # 1: Нормальные данные
            [
                ['student','date','coffee_spent','sleep_hours','study_hours','mood','exam'],
                ['Мария Соколова','2024-06-06','130','8.0','3','отл','Физика'],
                ['Павел Новиков', '2024-06-06', '410', '4.5', '11', 'устал', 'Физика'],
            ],
            {'Мария Соколова': [130], 'Павел Новиков': [410]}
    ),
   (
            # 2: Один и тот же студент несколько раз в одном файле.
            [
                ['student','date','coffee_spent','sleep_hours','study_hours','mood','exam'],
                ['Елена Волкова','2024-06-01','280','6.0','8','норм','Математика'],
                ['Елена Волкова','2024-06-06','300','5.5','9','норм','Физика'],
                ['Елена Волкова','2024-06-11','340','5.0','10','устал','Программирование'],
            ],
            {'Елена Волкова': [280, 300, 340]}
    ),
   (
            # 3: Пустой файл (только заголовок)
            [['student','date','coffee_spent','sleep_hours','study_hours','mood','exam'],],
            {}
    ),
])
def test_pt_process_files(file_content, expected_result):
    """Парам. тестт обработки файлов"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv',
                                     encoding='utf-8', newline='',
                                     delete=False) as tmp:
        writer = csv.writer(tmp)
        writer.writerows(file_content)
        tmp_path = tmp.name

    try:
        result = ca.process_files([tmp_path])
        assert result == expected_result
    finally:
        os.unlink(tmp_path)


@pytest.mark.parametrize('input_data, expected_output', [
   ([['Алексей Смирнов', 500]], [['Алексей Смирнов', 500]]),
   (
           [
               ['Дарья Петрова', 100],
               ['Иван Кузнецов', 150]
           ],
           [
               ['Дарья Петрова', 100],
               ['Иван Кузнецов', 150]
           ]
   ),
   ([], []),
])
def test_pt_generate_report(temp_output_dir, input_data, expected_output):
    """Парам. тест генерации отчетов"""
    report_path = os.path.join(temp_output_dir, 'param_test')
    ca.generate_report(input_data, report_path)

    with open(f'{report_path}.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        result = [[row[0], float(row[1])] for row in reader if row]

    assert result == expected_output


@pytest.mark.parametrize('values, expected_median', [
   ([1, 2, 3, 4, 5], 3.0),
   ([1, 2, 3, 4], 2.5),
   ([10], 10.0),
   ([1.5, 2.5, 3.5], 2.5),
])
def test_pt_median_calculation(values, expected_median):
    """Парам. тест расчета медианы"""
    data = {'СтудентФИО': values}
    result = ca.calculate_median(data)
    assert result[0][1] == expected_median


# === INTEGRATION TESTS ===

def test_it_main(temp_csv_files, temp_output_dir, capsys):
    """Тест всего скрипта"""
    report_path = os.path.join(temp_output_dir, 'integration_report')
    args = ['-f', temp_csv_files[0], temp_csv_files[1], '-r', report_path]
    with patch('sys.argv', ['script.py'] + args):
        ca.main()

    # Проверяем вывод в консоль
    captured = capsys.readouterr()
    assert 'Алексей Смирнов' in captured.out
    assert 'Дарья Петрова' in captured.out
    assert 'Иван Кузнецов' in captured.out

    # Проверяем создание отчета
    report_file = f'{report_path}.csv'
    assert os.path.exists(report_file)

    # Проверяем содержимое отчета
    with open(report_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        result = list(reader)
        # Сортируем для стабильности
        result_sorted = sorted(result, key=lambda x: x[0])
        expected = [
            ['Алексей Смирнов', '540.0'],
            ['Дарья Петрова', '300.0'],
            ['Иван Кузнецов', '650.0']
        ]
        assert result_sorted == expected


def test_it_main_wif(temp_output_dir, capsys): # wif - with invalid files
    """Тест запуска с несущесттвующими файлами"""
    report_path = os.path.join(temp_output_dir, 'invalid_report')
    args = ['-f', 'missing1.csv', 'missing2.csv', '-r', report_path]

    with patch('sys.argv', ['script.py'] + args):
        ca.main()

    captured = capsys.readouterr()
    assert 'Файл missing1.csv не существует!' in captured.out
    assert 'Файл missing2.csv не существует!' in captured.out
    assert 'Нет данных для обработки' in captured.out
