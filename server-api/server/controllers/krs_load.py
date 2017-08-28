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
						case --Определяем была ли стельная, если да то это нетель
				            when T4.STATUS='Бычок' then 'Бычок'
				            when 
				        	(
					            Select FIRST 1 TT2.PROV_IM As PROV_IM4
					            From REGISTER TT0
					            left join SUP_CLCALT_SELEX(6263931,T0.NANIMAL,1) TT1 on 2=2
					            left join SUP_EVENTS_SELEX(T0.NANIMAL) TT2 on 2=2
					 
					            Where (TT0.NHOZ=6263931) and (((TT0.NANIMAL>2000000000000 AND TT0.NANIMAL<3000000000000))) and
					            (TT0.NINV=T0.NINV) and (TT2.PROV_IM='Стельная')
					        )='Стельная' then 'Нетель'
				        	else 'Телочка'
				        end as status,
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




@app.route('/api/krs_load_osemeneniya/<date_start>/<date_end>/<kod_osemeneniya>', method='GET')
def krs_load_osemeneniya(date_start, date_end, kod_osemeneniya):
	
	"""Загрузка осеменения за выбранный период"""


	if date_end is None or date_start is None or kod_osemeneniya is None:
		return 'error'
	#return 'error'
	#print date
	zapros=r"""Select
				        T0.NINV As inv_nomer,
				        case
				            when T0.NANIMAL>4000000000000 AND T0.NANIMAL<5000000000000 then 'Корова'
				            else 'Телочка'
				        end as status,
				        T1.EVENT_DATE As date_o,
				        T2.IM As fio,
				        T3.KLICHKA As bik,
				        COALESCE(T1.DOZ_SPERMY,1) As doz
				 From REGISTER T0
				 left join SUP_EVENTS_SELEX(T0.NANIMAL) T1 on 2=2 
				 left join TEXN T2 on T1.NTEXN=T2.NTEXN
				 left join REGISTER T3 on T1.NBYK=T3.NANIMAL
				 
				 Where (T0.NHOZ=6263931) and (((T0.NANIMAL>4000000000000 AND T0.NANIMAL<5000000000000)) or 
				 ((T0.NANIMAL>2000000000000 AND T0.NANIMAL<3000000000000))) and 
				 		(T1.EVENT_DATE>=?) and 
				 		(T1.EVENT_DATE<=?) and 
				 		(T1.EVENT_KOD=?)
				 """
	
	param=(date_start,date_end,int(kod_osemeneniya),)
	result=con_selex(zapros,param,2)
	datas = []
	for line in result:
		datas.append(
					{
						'inv_nomer':line[0],
						'status': line[1],
						'date': str(line[2]),
						'fio': line[3],
						'bik': line[4],
						'doz': int(line[5])
					}
		
		)
	#print zagon
	
	data = json.dumps(datas)
	#print data
	
	return data





@app.route('/api/krs_load_abort/<date_start>/<date_end>/<kod_abort>', method='GET')
def krs_load_abort(date_start, date_end, kod_abort):
	
	"""Загрузка Аборты за выбранный период"""


	if date_end is None or date_start is None or kod_abort is None:
		return 'error'
	#return 'error'
	#print date
	zapros=r"""Select
				        T0.NINV As inv_nomer,
				        case
				            when T0.NANIMAL>4000000000000 AND T0.NANIMAL<5000000000000 then 'Корова'
				            else 'Нетель'
				        end as status,
				        T1.EVENT_DATE As date_a
				        
				 From REGISTER T0
				 left join SUP_EVENTS_SELEX(T0.NANIMAL) T1 on 2=2 
				 
				 Where (T0.NHOZ=6263931) and (((T0.NANIMAL>4000000000000 AND T0.NANIMAL<5000000000000)) or 
				 ((T0.NANIMAL>2000000000000 AND T0.NANIMAL<3000000000000))) and 
				 		(T1.EVENT_DATE>=?) and 
				 		(T1.EVENT_DATE<=?) and 
				 		(T1.EVENT_KOD=?)
				 """
	
	param=(date_start,date_end,int(kod_abort),)
	result=con_selex(zapros,param,2)
	datas = []
	for line in result:
		datas.append(
					{
						'inv_nomer':line[0],
						'status': line[1],
						'date': str(line[2])
					}
		
		)
	#print zagon
	
	data = json.dumps(datas)
	#print data
	
	return data





@app.route('/api/krs_load_struktura/<date>', method='GET')
def krs_load_struktura(date):
	
	"""Загрузка Структуры стада за выбранный период"""


	if date is None:
		return 'error'
	#return 'error'
	#print date
	zapros=r"""select
				    case
				        when TT.NSOST=4 then 'Осемененная телка'
				        when TT.NSOST=41 then 'Сомнительная телка'
				        when TT.NSOST=5 then 'Стельная телка'
				        when TT.NSOST=52 then 'Нетель'
				        when TT.NSOST=51 then 'Нетель транзит'
				        when TT.NSOST=6 then 'Неосемененная корова'
				        when TT.NSOST=7 then 'Осемененная корова'
				        when TT.NSOST=71 then 'Сомнительная корова'
				        when TT.NSOST=8 then 'Стельная корова'
				        when TT.NSOST=9 then 'Запущенная корова'
				        else 'Телочка'
				    end,
				    case
				        when TT.NSOST>5 and TT.NSOST <> 51 and TT.NSOST <> 41 then 'Корова'
				        when (TT.MONTHS>=15 and (TT.NSOST<=5 or TT.NSOST=51 or TT.NSOST=41)) or
				              (TT.NSOST=5 or TT.NSOST=51 or TT.NSOST=41 )
				         then 'Старше 15'
				        else 'Телочка <15'
				    end as age,

				    TT.SOST_KOD,
				    count(TT.NINV)
				From
				(
				Select
				        case
				            when T1.NSOST=7 or (T1.NSOST=4)   then
	                            case
	                                when (
	                                        Select first 1
	                                            case
	                                                 When K.PROV_IM='Сомнительная' then T1.NSOST*10+1
	                                                 else T1.NSOST
	                                              end
	                                        

	                                         from SUP_EVENTS_SELEX(T0.NANIMAL) K
	                                         Where (K.EVENT_KOD=8 or K.EVENT_KOD=10 or K.EVENT_KOD=7)  and 
	                                         		K.EVENT_DATE<=?
	                                         order by K.EVENT_DATE desc)=T1.NSOST*10+1 then T1.NSOST*10+1
	                             else T1.NSOST
	                             end


				            when T1.NSOST=5 then
	                            case
	                                when ( --Проверка. если дней стельности больше 256 (т.е за 2 недели до отела) то это нетель транзит
	                                        Select first 1
	                                              cast(? as date)-K.EVENT_DATE as SDAY

	                                                from SUP_EVENTS_SELEX(T0.NANIMAL) K
	                                                 Where (K.EVENT_KOD=7)  and K.EVENT_DATE<=?
	                                                order by K.EVENT_DATE desc
	                                    )>256 then T1.NSOST*10+1

	                                when ( --Проверка. если дней стельности больше 150 то это нетель
	                                        Select first 1
	                                              cast(? as date)-K.EVENT_DATE as SDAY

	                                                from SUP_EVENTS_SELEX(T0.NANIMAL) K
	                                                 Where (K.EVENT_KOD=7)  and K.EVENT_DATE<=?
	                                                order by K.EVENT_DATE desc
	                                    )>150 then T1.NSOST*10+2
	                                else T1.NSOST
	                              end



				            else T1.NSOST
				        end as NSOST,
				        D.MONTHS,
				        T1.SOST_KOD ,
				        T0.NINV
				 From REGISTER T0
				 left join S_GET_SOST(T0.NANIMAL, ?) T1 on 2=2
				 left join get_agemol(T0.DATE_ROGD, ?, 0) D on 2=2
				 
				 Where (T0.NHOZ=6263931) and
				        (((T0.NANIMAL>4000000000000 AND T0.NANIMAL<5000000000000)) or
				         ((T0.NANIMAL>2000000000000 AND T0.NANIMAL<3000000000000)))
				
				and T0.DATE_ROGD<=? and ( (T0.DATE_V>=?) or (T0.DATE_V is Null)   )

				) TT

				Group by  1,2,3 
				 		 
				 		
				 """
	
	param=(date,date,date,date,date,date,date,date,date,)
	result=con_selex(zapros,param,2)
	cow_neosem = cow_osem = cow_somnit = cow_stel = 0
	cow_zapusk = 0
	tel_neosem = tel_osem = tel_somnit = tel_stel = tel_netel = tel_tranzit = 0
	tel_15_neosem = tel_15_osem = tel_15_stel = 0
	datas = []
	
	n= result
	for line in result:
		
		#ТЕЛКИ
		if line[0] == u"Телочка":
			tel_neosem += line[3]

		if line[0] == u'Телочка' and line[1] == u'Старше 15':
			tel_15_neosem += line[3]

		if line[0] == u'Осемененная телка':
			tel_osem += line[3]

		if line[0] == u'Осемененная телка' and line[1] == u'Старше 15':
			tel_15_osem += line[3]

		if line[0] == u'Сомнительная телка':
			tel_somnit += line[3]

		if line[0] == u'Сомнительная телка' and line[1] == u'Старше 15':
			tel_15_stel += line[3]

		if line[0] == u'Стельная телка':
			tel_stel += line[3]

		if line[0] == u'Стельная телка' and line[1] == u'Старше 15':
			tel_15_stel += line[3]

		if line[0] == u'Нетель':
			tel_netel += line[3]

		if line[0] == u'Нетель транзит':
			tel_tranzit += line[3]

		#КОРОВЫ
		if line[0] == u'Неосемененная корова':
			cow_neosem += line[3]

		if line[0] == u'Осемененная корова':
			cow_osem += line[3]

		if line[0] == u'Сомнительная корова':
			cow_somnit += line[3]

		if line[0] == u'Стельная корова':
			cow_stel += line[3]

		if line[0] == u'Запущенная корова':
			cow_zapusk += line[3]




	datas.append(
				{
					'n':n,
					'cow_neosem':cow_neosem,
					'cow_osem': cow_osem,
					'cow_somnit': cow_somnit,
					'cow_stel': cow_stel,
					'cow_zapusk': cow_zapusk,
					'tel_neosem': tel_neosem,
					'tel_osem': tel_osem,
					'tel_somnit': tel_somnit,
					'tel_stel': tel_stel,
					'tel_netel': tel_netel,
					'tel_tranzit': tel_tranzit,
					'tel_15_neosem': tel_15_neosem,
					'tel_15_osem': tel_15_osem,
					'tel_15_stel': tel_15_stel
				}
	
	)
	#print zagon
	
	data = json.dumps(datas)
	#print data
	
	return data