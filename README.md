# Биржа яблок
Это тестовая модель биржи. Биржа торгует только яблоками (целое число).

Использование:

    >>> python stock.py <input_file> <output_file>

Или запустить функцию из Python:

    >>> process_orders(<input_fname>, <output_fname>)

По умолчанию входной файл input.txt, выходной - output.txt

Сложность добавления заявки O(log(N)), где N - число заявок.

Сложность удаления заявки O(1)

Проверок корректности входных данных не производится.

Требуется Python 3 (проверялось на Python 3.7 в Anaconda/Spyder под Windows)
