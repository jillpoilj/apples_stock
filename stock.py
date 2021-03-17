# -*- coding: utf-8 -*-
# by Alex Stroev

from __future__ import division

import heapq

from decimal import Decimal

import sys

"""
Это тестовая модель биржи. Биржа торгует только яблоками (целое число).
Использование:
    >>> python stock.py <input_file> <output_file>
По умолчанию входной файл input.txt, выходной - output.txt
Сложность добавления заявки O(log(N)), где N - число заявок
Сложность удаления заявки O(1)
Проверок корректности входных данных не производится.
Требуется Python 3 (проверялось на Python 3.7 в Anaconda/Spyder под Windows)
"""

class Order(object):
    
    """
    Заявка на покупку или продажу.
    ID - номер заявки. Должен быть уникальным.
    side - 'B' для заявки на покупку, 'S' - на продажу
    qty - количество
    price - цена    
    side_price - цена с учетом типа сделки (отрицательная для покупки)
    """
    
    def __init__(self, ID, side, qty, price):
        self.ID = int(ID)
        self.side = str(side)
        self.qty = int(qty)
        self.price = Decimal(price)
        
        self.side_price = self.price if self.side == 'S' else -self.price
    
    def __str__(self):
        return f'O, {self.ID}, {self.side}, {self.qty}, {self.price}'
    
    def __repr__(self):
        return self.__str__()
    
        
class Deal(object):
    
    """
    Сделка
    ID - номер сделки. Выставляется автоматически
    side - side заявки, которая совершила сделку (более поздняя)
    OID1, OID2 - номера заявок, совершивших сделку. OID2 более поздняя
    qty - количество
    price - цена
    """
    
    next_ID = 0
    
    def __init__(self, side, OID1, OID2, qty, price):
        self.ID = Deal.next_ID
        Deal.next_ID += 1
        self.side = str(side)
        self.OID1 = int(OID1)
        self.OID2 = int(OID2)
        self.qty = int(qty)
        self.price = Decimal(price)
        
    def __str__(self):
        return f'T, {self.ID}, {self.side}, {self.OID1}, '\
            f'{self.OID2}, {self.qty}, {self.price}\n'
    
    def __repr__(self):
        return self.__str__()
        

class Cancel(object):
    
    """
    Отмена заявки
    OID - Номер отмененной заявки
    """
    
    def __init__(self, OID):
        self.OID = int(OID)
        
    def __str__(self):
        return f'X, {self.OID}\n'
    
    def __repr__(self):
        return self.__str__()

def process_new_order(orders, price_heaps, new_order, deals):
    
    """
    Вызывается при поступлении новой заявки. Пытается заключить сделки по 
    существующим заявкам, затем создает новую заявку на оставшуюся часть.
    Заключенные сделки добавляются в deals, новая заявка (если осталась)
    добавляется в orders и в price_heaps.

    Parameters
    ----------
    orders : dict
        Текущие заявки.
    price_heaps : dict
        Номера заявок, отсортированные по возрастанию цены продажи и по 
        убыванию цены покупки.
    new_order : Order
        Новая заявка.
    deals : list
        Список сделок.

    Returns
    -------
    None.

    """
    
    other_side = 'S' if new_order.side == 'B' else 'B'
    same_heap = price_heaps[new_order.side]
    other_heap = price_heaps[other_side]
    
    make_deals(orders, other_heap, new_order, deals)
    if new_order.qty > 0:
        add_order(orders, same_heap, new_order)

def add_order(orders, same_heap, new_order):
    
    """
    Добавить заявку

    Parameters
    ----------
    orders : dict
        Текущие заявки.
    same_heap : list
        Отсортированные заявки соответствующего типа: price_heaps['B'] 
        или price_heaps['S'].
    new_order : Order
        Новая заявка.

    Raises
    ------
    KeyError
        Если заявка с таким номером уже существует.

    Returns
    -------
    None.

    """
    
    if new_order.ID in orders:
        raise KeyError('Order with that ID already exists!')
    orders[new_order.ID] = new_order
    heapq.heappush(same_heap, (new_order.side_price, new_order.ID))

def make_deals(orders, other_heap, new_order, deals):
    
    """
    Выбрать самые выгодные заявки и заключить с ними сделки.
    """
    
    while len(other_heap) > 0:
        other_ID = other_heap[0][1]
        
        # если самая выгодная заявка была удалена
        if other_ID not in orders:
            heapq.heappop(other_heap)
            continue
        
        other_order = orders[other_ID]
        
        # если цена продажи выше цены покупки
        if new_order.side_price + other_order.side_price > 0:
            break
        
        # сделка
        if other_order.qty > 0:
            deal_qty = min(new_order.qty, other_order.qty)
            deal = Deal(new_order.side, other_order.ID, 
                        new_order.ID, deal_qty, other_order.price)
            deals.append(deal)
            new_order.qty -= deal_qty
            other_order.qty -= deal_qty
        
        # другая заявка закончилась
        if other_order.qty <= 0:
            del orders[other_order.ID]
            heapq.heappop(other_heap)
        # новая заявка закончилась
        if new_order.qty <= 0:
            break
        
def cancel_order(orders, ID, deals):
    
    """
    Отмена заявки с номером ID. Добавляется в список сделок deals.
    """
    
    int_ID = int(ID)
    if int_ID in orders:        
        del orders[int_ID]
        deals.append(Cancel(int_ID))

def process_orders(input_fname='input.txt', output_fname='output.txt'):
    
    """
    Чтение файла, запуск обработки, запись результатов в файл
    """
    
    orders = {}
    price_heaps = {'B': [], 'S': []}
    deals = []
    
    with open(input_fname, 'r') as input_file:
        for line in input_file:
            tokens = line.split(',')
            if tokens[0] == 'O':
                new_order = Order(*tokens[1:])
                process_new_order(orders, price_heaps, new_order, deals)
            elif tokens[0] == 'C':
                cancel_order(orders, int(tokens[1]), deals)
    
    with open(output_fname, 'w') as output_file:
        for deal in deals:
            output_file.write(str(deal))
            
if __name__ == '__main__':
    if len(sys.argv) > 1:
        input_fname = sys.argv[1]
    else:
        input_fname = 'input.txt'
    if len(sys.argv) > 2:
        output_fname = sys.argv[2]
    else:
        output_fname = 'output.txt'
    process_orders(input_fname, output_fname)
            