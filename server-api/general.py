# -*- coding: utf-8 -*-
"""Общий модуль"""

import decimal
from datetime import datetime, timedelta

def decimal_default(obj):
    """Возвращает объект в формате float, предназаначена для формирования json данных"""
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

def json_serial(obj):
	"""JSON serializer for objects not serializable by default json code"""
	
	if isinstance(obj, datetime):
		serial = obj.isoformat()
		return serial
	if isinstance(obj, decimal.Decimal):
		return float(obj)
	raise TypeError ("Type not serializable")




def last_day_of_month(date):
    """Возвращает дату последнего дня месяца"""
    if date.month == 12:
        return date.replace(day=31)
    return date.replace(month=date.month+1, day=1) - timedelta(days=1)
