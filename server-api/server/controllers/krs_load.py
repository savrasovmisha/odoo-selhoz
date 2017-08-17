#!/usr/bin/env python
# -*- coding: utf-8 -*-
from server import app
from bottle import request, jinja2_template as template
import json
from db_connect import con_uniform, con_selex
from decimal import Decimal
import datetime

## Фильтр для преобразования ДАТЫ в российский формат

def datetimeformat(value, format='%d.%m.%Y'):
    if type(value) == type(datetime.date.today()):
        return value.strftime(format).decode('utf-8')
    else:
        print value,u'Это не дата'
        return value



   
@app.route('/api/krs_load_otel/<date_start>/<date_end>/<kod_otel>', method='GET')
def krs_load_otel(date_start, date_end, kod_otel):
	if date_end is None or date_start is None or kod_otel is None:
		return 'error'
	#print date
	zapros=r"""Select 
					T0.NINV As NINV0,
					T1.HOZ As HOZ1,
					T2.EVENT_DATE As EVENT_DATE2,
					T2.EVENT_KOD As EVENT_KOD3,
					T2.EVENT_IM As EVENT_IM4,
					T2.LAKT As LAKT5,
					T2.OTEL_REZ As OTEL_REZ6,
					T0.NANIMAL 
				 From REGISTER T0
				 left join SHOZ_ALL T1 on T0.NHOZ_ROGD=T1.NHOZ
				 left join SUP_EVENTS_SELEX(T0.NANIMAL) T2 on 2=2 
				 
				 Where  (T0.NHOZ=6263931) and 
				 		(((T0.NANIMAL>4000000000000 AND T0.NANIMAL<5000000000000))) and 
				 		(T2.EVENT_DATE>=?) and 
				 		(T2.EVENT_DATE<=?) and 
				 		(T2.EVENT_KOD=?)
				 """
	
	param=(date_start,date_end,int(kod_otel),)
	result=con_selex(zapros,param,2)
	zagon = []
	for line in result:
		zagon.append(
					{
						'GROEPNR':line[0],
						'sred_kol_milk': float(line[3])
					}
		
		)
	#print zagon
	
	data = json.dumps(zagon)
	#print data
	
	return data
