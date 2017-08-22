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
	
	"""Загрузка отелов за выбранный период"""


	if date_end is None or date_start is None or kod_otel is None:
		return 'error'
	#return 'error'
	#print date
	zapros=r"""Select 
					T0.NINV As inv_nomer,
					T1.NHOZ As hoz_selex_id,
					T2.EVENT_DATE As date_o,
					T2.LAKT As nomer_lakt,
					T2.OTEL_REZ As result,
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
	otels = []
	for line in result:
		otels.append(
					{
						'inv_nomer':line[0],
						'hoz_selex_id': int(line[1]),
						'date': str(line[2]),
						'nomer_lakt': int(line[3]),
						'result': line[4]
					}
		
		)
	#print zagon
	
	data = json.dumps(otels)
	#print data
	
	return data



@app.route('/api/krs_sync_spv/', method='GET')
def krs_sync_spv():

	"""Синхронизация справочника Причины выбытия"""
	
	zapros = r"""Select 
					T2.PV As kod, 
					T2.IM As name
 				From  SPV T2
				 """
	
	param = []
	result = con_selex(zapros,param,2)
	spv = []
	for line in result:
		spv.append(
					{
						'kod': line[0],
						'name':line[1]
					}
		
		)
	
	data = json.dumps(spv)
	
	return data




@app.route('/api/krs_sync_hoz/', method='GET')
def krs_sync_hoz():

	"""Синхронизация справочника Хозяйства рождения"""
	
	zapros = r"""Select 
						T1.NHOZ as selex_id, 
						T1.HOZ As kod,
						T1.IM As name
				 From REGISTER T0
				 left join SHOZ_ALL T1 on T0.NHOZ_ROGD=T1.NHOZ
				 
				 Where (((T0.NANIMAL>4000000000000 AND T0.NANIMAL<5000000000000)))

				 group by    
				 		T1.IM, 
				 		T1.NHOZ, 
				 		T1.HOZ
				 """
	
	param = []
	result = con_selex(zapros,param,2)
	spv = []
	for line in result:
		spv.append(
					{
						'selex_id': line[0],
						'kod': line[1],
						'name':line[2]
					}
		
		)
	
	data = json.dumps(spv)
	
	return data




@app.route('/api/krs_sync_srashod/', method='GET')
def krs_sync_srashod():

	"""Синхронизация справочника Вид расхода"""
	
	zapros = r"""
				Select
					T3.RASHOD As kod,
					T3.IM As name
				From  SRASHOD T3
				 """
	
	param = []
	result = con_selex(zapros,param,2)
	spv = []
	for line in result:
		spv.append(
					{
						'kod': line[0],
						'name':line[1]
					}
		
		)
	
	data = json.dumps(spv)
	
	return data




@app.route('/api/krs_load_cow_vibitiya/<date_start>/<date_end>/', method='GET')
def krs_load_cow_vibitiya(date_start, date_end):
	
	"""Загрузка Выбытия коров за выбранный период"""


	if date_end is None or date_start is None:
		return 'error'

	zapros=r""" Select 
					T0.NINV As inv_nomer,
					T0.DATE_ROGD As date_rogd,
					T1.NHOZ As hoz_selex_id,
					T0.DATE_V As date_v,
					T2.PV As kod_spv,
					T3.RASHOD As kod_srashod,
					T4.LAKTAC As nomer_lakt,
					T0.NANIMAL 
				 From REGISTER T0
				 left join SHOZ_ALL T1 on T0.NHOZ_ROGD=T1.NHOZ
				 left join SPV T2 on T0.NPV=T2.NPV
				 left join SRASHOD T3 on T0.NRASHOD=T3.NRASHOD
				 left join SUP_CLCFLDFTL_SELEX(T0.NANIMAL,'2') T4 on 2=2  
								 
				 Where  (T0.NHOZ=6263931) and 
				 		(((T0.NANIMAL>4000000000000 AND T0.NANIMAL<5000000000000))) and 
				 		(T0.DATE_V>=?) and 
				 		(T0.DATE_V<=?) 
				 """
	
	param=(date_start,date_end,)
	result=con_selex(zapros,param,2)
	datas = []
	for line in result:
		datas.append({
						'inv_nomer':line[0],
						'date_rogd':str(line[1]),
						'hoz_selex_id':int(line[2]),
						'date':str(line[3]),
						'kod_spv':int(line[4]),
						'kod_srashod':int(line[5]),
						'nomer_lakt': int(line[6])
		
					})
	#print zagon
	
	data = json.dumps(datas)
	#print data
	
	return data





@app.route('/api/krs_load_tel_vibitiya/<date_start>/<date_end>/', method='GET')
def krs_load_tel_vibitiya(date_start, date_end):
	
	"""Загрузка Выбытия телят за выбранный период"""


	if date_end is None or date_start is None:
		return 'error'

	zapros=r""" Select 
						T0.NINV As inv_nomer,
						T0.DATE_ROGD As date_rogd,
						T1.NHOZ As hoz_selex_id,
						T0.DATE_V As date_v,
						T2.PV As kod_spv,
						T3.RASHOD As kod_srashod,
						T4.STATUS As status,
						T0.NANIMAL 
				 From REGISTER T0
				 left join SHOZ_ALL T1 on T0.NHOZ_ROGD=T1.NHOZ
				 left join SPV T2 on T0.NPV=T2.NPV
				 left join SRASHOD T3 on T0.NRASHOD=T3.NRASHOD
				 left join GET_STATUSANIMAL(T0.NANIMAL) T4 on 2=2  
								 
				 Where  (T0.NHOZ=6263931) and 
				 		(((T0.NANIMAL>2000000000000 AND T0.NANIMAL<3000000000000)) or 
				 		 ((T0.NANIMAL>1000000000000 AND T0.NANIMAL<2000000000000))) and 
				 		(T0.DATE_V>=?) and 
				 		(T0.DATE_V<=?) 
				 """
	
	param=(date_start,date_end,)
	result=con_selex(zapros,param,2)
	datas = []
	for line in result:
		datas.append({
						'inv_nomer':line[0],
						'date_rogd':str(line[1]),
						'hoz_selex_id':int(line[2]),
						'date':str(line[3]),
						'kod_spv':int(line[4]),
						'kod_srashod':int(line[5]),
						'status': line[6]
		
					})
	#print zagon
	
	data = json.dumps(datas)
	#print data
	
	return data