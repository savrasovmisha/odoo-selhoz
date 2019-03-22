# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
date = '2015-01-01'
period = 11
date_last = datetime.strptime(date, "%Y-%m-%d").date()
year = 2018

m_last = date_last.month
y_last = date_last.year
m_next = m_last
y_next = y_last
y_today = year

if y_last < y_today:
	while (m_next<=12 and y_next<y_today):
		m_next += period
		if m_next>12:
		    y_next += 1
		    m_next = m_next - 12
else:
	m_next = 'err'

print u"Следующий ремонт ", m_next

for m in range(1,13):
	print m


my_dict = {'key': 'value'}
key_exists = my_dict.has_key('key')  # Устаревший способ.
key_exists = 'key1' in my_dict  # Актуальный способ.

if 'key1' not in my_dict:
	print True
else:
	print False
