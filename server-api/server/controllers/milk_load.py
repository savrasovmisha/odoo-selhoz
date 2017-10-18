#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division #при делении будет возвращаться float
from server import app
from bottle import request, jinja2_template as template
import json
from db_connect import con_uniform, con_selex
from decimal import Decimal
import datetime

from pandas import DataFrame, pivot_table
import pandas as pd
import numpy as np

## Фильтр для преобразования ДАТЫ в российский формат

def datetimeformat(value, format='%d.%m.%Y'):
    if type(value) == type(datetime.date.today()):
        return value.strftime(format).decode('utf-8')
    else:
        print value,u'Это не дата'
        return value


@app.route('/api/milk_nadoy_group/:date', method='GET')
def milk_nadoy_group(date):
	if date is None:
		return 'error'
	print date
	res = []
	

	####   По загонам  ################
	zapros=r"""SELECT 
					g.GROEPNR,
					r.DIERID,
					Sum(r.HOEVEELHEIDMELK) as kol_milk
					FROM DIER_MELKGIFT r 
					left join DIER d on d.DIERID=r.DIERID
					left join GROEP g on g.GROEPID=d.GROEPID
					where r.HOEVEELHEIDMELK<100 and (case
                                            when r.TIJDSTIPEIND<'03:00:00.000' then r.DATUM-1
                                            else r.DATUM
                                        end)=?	
		Group By g.GROEPNR, r.DIERID"""
	param=(date,)
	result=con_uniform(zapros,param,2)
	zagon = []
	if len(result)>0:
		

		datas = DataFrame(data=result,columns=['GROEPNR', 'DIERID', 'kol_milk'], dtype=int )


		table = pivot_table(datas,  values=['kol_milk'], 
									index=['GROEPNR'],
									aggfunc= [np.mean, np.std, len],
									fill_value=0 #Если NaN то 0
									)
		for line in table.index: #Iterate through columns
			#print a, table.ix[a,0], table.ix[a,1]
			zagon.append(
						{
							'GROEPNR':line,
							'kol': table.ix[line,0],
							'sko': table.ix[line,1],
							'kol_golov': int(table.ix[line,2])
						}
			
			)
	res.append({'zagons': zagon})


	####   % голов по надоям  ################
	zapros=r"""select
				    count(case
				        when z1.kol_milk<15 then 1
				        
				    end) as n015,
				    count(case
				        when z1.kol_milk>=15 and z1.kol_milk<20 then 1
				        
				    end) as n1520,
				    count(case
				        when z1.kol_milk>=20 and z1.kol_milk<25 then 1
				        
				    end) as n2025,
				    count(case
				        when z1.kol_milk>=25 and z1.kol_milk<30 then 1
				        
				    end) as n2530,
				    count(case
				        when z1.kol_milk>=30 and z1.kol_milk<35 then 1
				        
				    end) as n3035,
				    count(case
				        when z1.kol_milk>=35 and z1.kol_milk<40 then 1
				        
				    end) as n3540,
				    count(case
				        when z1.kol_milk>=40 and z1.kol_milk<45 then 1
				        
				    end) as n4045,
				    count(case
				        when z1.kol_milk>=45 then 1
				        
				    end) as n45
				    
				    
				        
				FROM   (        
				        SELECT 
									
									r.DIERID,
									Sum(r.HOEVEELHEIDMELK) as kol_milk
									FROM DIER_MELKGIFT r 
									where r.HOEVEELHEIDMELK<100 and (case
				                                            when r.TIJDSTIPEIND<'03:00:00.000' then r.DATUM-1
				                                            else r.DATUM
				                                        end)=?	
						Group By r.DIERID
						) as z1"""
	param=(date,)
	result=con_uniform(zapros,param,2)
	n015 = 0.0
	n1520 = 0.0
	n2025 = 0.0
	n2530 = 0.0
	n3035 = 0.0
	n3540 = 0.0
	n4045 = 0.0
	n45 = 0.0

	if len(result)>0:
		line = result[0]
		kol_golov = line[0] + line[1] + line[2] + line[3] + line[4] + line[5] + line[6] + line[7]
		
		if kol_golov>0:
			n015 = line[0]/kol_golov*100
			n1520 = line[1]/kol_golov*100
			n2025 = line[2]/kol_golov*100
			n2530 = line[3]/kol_golov*100
			n3035 = line[4]/kol_golov*100
			n3540 = line[5]/kol_golov*100
			n4045 = line[6]/kol_golov*100
			n45 = line[7]/kol_golov*100

	res.append({'procent':
						{
						'procent_0_15': n015,
						'procent_15_20': n1520,
						'procent_20_25': n2025,
						'procent_25_30': n2530,
						'procent_30_35': n3035,
						'procent_35_40': n3540,
						'procent_40_45': n4045,
						'procent_45': n45
						}
				})


	#print zagon
	
	data = json.dumps(res)
	#print data
	
	return data