#!/usr/bin/env python
# -*- coding: utf-8 -*-
from server import app
from bottle import request, jinja2_template as template
import json
from db_connect import con_uniform
from decimal import Decimal
import datetime

## Фильтр для преобразования ДАТЫ в российский формат

def datetimeformat(value, format='%d.%m.%Y'):
    if type(value) == type(datetime.date.today()):
        return value.strftime(format).decode('utf-8')
    else:
        print value,u'Это не дата'
        return value



@app.route('/api/struktura_stada', method='GET')
def index():
 
	zapros=r"""SELECT 
					g.GROEPNR,
					g.OMSCHRIJVING as ZAGON,
					count(r.DIERID)
					
					FROM DIER r
					left join GROEP g on 
                            case 
                                when r.GROEPID is Null then '-2147483645' 
                                else r.GROEPID 
                            end=g.GROEPID
					Where r.STATUS!='9' and r.STATUS!='10'  
					Group by g.GROEPNR, g.OMSCHRIJVING
					Order by g.OMSCHRIJVING"""
   
	result=con_uniform(zapros,'',2)
	zagon = []
	for line in result:
		zagon.append(
					{
						'GROEPNR':line[0],
						'name': line[1],
						'kol_golov_zagon': line[2]
					}
		
		)
	print zagon
	
	data = json.dumps(zagon)
	print data
	
	return data
   
@app.route('/api/struktura_stada_milk/:date', method='GET')
def struktura_stada_milk(date):
	if date is None:
		return 'error'
	date = "{date:%Y-%m-%d}"
	zapros=r"""SELECT 
					g.GROEPNR,
					Count(r.DIERID)/2 as kol_golov,
					Sum(r.HOEVEELHEIDMELK) as kol_milk,
					Sum(r.HOEVEELHEIDMELK)/Count(r.DIERID)*2 as kol_milk_sr
					
					
					FROM DIER_MELKGIFT r 
					left join DIER d on d.DIERID=r.DIERID
					left join GROEP g on g.GROEPID=d.GROEPID
					where r.HOEVEELHEIDMELK<100 and (case
                                            when r.TIJDSTIPEIND<'03:00:00.000' then r.DATUM-1
                                            else r.DATUM
                                        end)=?	
		Group By g.GROEPNR"""
	param=(date,)
	result=con_uniform(zapros,param,2)
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
