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
	zapros=r"""select
				    z1.GROEPNR,
				    z1.DIERID,
				    z1.kol_milk,
				    case
				        when z1.kol_milk<15 then 1
				        else 0
				    end as n015,
				    case
				        when z1.kol_milk>=15 and z1.kol_milk<20 then 1
				        else 0
				    end as n1520,
				    case
				        when z1.kol_milk>=20 and z1.kol_milk<25 then 1
				        else 0
				    end as n2025,
				    case
				        when z1.kol_milk>=25 and z1.kol_milk<30 then 1
				        else 0
				    end as n2530,
				    case
				        when z1.kol_milk>=30 and z1.kol_milk<35 then 1
				        else 0
				    end as n3035,
				    case
				        when z1.kol_milk>=35 and z1.kol_milk<40 then 1
				        else 0
				    end as n3540,
				    case
				        when z1.kol_milk>=40 and z1.kol_milk<45 then 1
				        else 0
				    end as n4045,
				    case
				        when z1.kol_milk>=45 then 1
				        else 0
				    end as n45
				    
				    
				        
				FROM   ( 

						SELECT 
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
						Group By g.GROEPNR, r.DIERID
						) as z1

						"""
	param=(date,)
	result=con_uniform(zapros,param,2)
	zagon = []
	if len(result)>0:

		datas = DataFrame(data=result,columns=[ 'GROEPNR', 
												'DIERID', 
												'kol_milk', 
												'n015',
												'n1520',
												'n2025',
												'n2530',
												'n3035',
												'n3540',
												'n4045',
												'n45',
												 ], dtype=int )


		table = pivot_table(datas,  values=['kol_milk',
											'n015',
											'n1520',
											'n2025',
											'n2530',
											'n3035',
											'n3540',
											'n4045',
											'n45'
											], 
									index=['GROEPNR'],
									aggfunc= {
												'kol_milk': [np.mean, np.std, len],
												'n015': [np.sum],
												'n1520': [np.sum],
												'n2025': [np.sum],
												'n2530': [np.sum],
												'n3035': [np.sum],
												'n3540': [np.sum],
												'n4045': [np.sum],
												'n45': [np.sum],


												},
									fill_value=0 #Если NaN то 0
									)

		# cols = [('kol_milk', 'mean'), 
		# 		('kol_milk', 'len'), 
		# 		('kol_milk', 'std'), 
		# 		('n015', 'sum'), 
		# 		('n1520', 'sum'),
		# 		('n2025', 'sum'),
		# 		('n2530', 'sum'),
		# 		('n1520', 'sum'),
		# 		('n1520', 'sum'),
		# 		('n1520', 'sum'),
		# 		]
		# table = table.reindex(columns=cols)
		table1 = table
		table2 = []
		for line in table.index: #Iterate through columns
			#print a, table.ix[a,0], table.ix[a,1]
			n015 = 0.0
			n1520 = 0.0
			n2025 = 0.0
			n2530 = 0.0
			n3035 = 0.0
			n3540 = 0.0
			n4045 = 0.0
			n45 = 0.0

			kol_golov = int(table.ix[line,('kol_milk', 'len')])# + 1 #Добавляем 1 т.к len начинает отсчет с нуля
			if kol_golov>0:
				n015 = table.ix[line,('n015', 'sum')]/kol_golov*100
				n1520 = table.ix[line,('n1520', 'sum')]/kol_golov*100
				n2025 = table.ix[line,('n2025', 'sum')]/kol_golov*100
				n2530 = table.ix[line,('n2530', 'sum')]/kol_golov*100
				n3035 = table.ix[line,('n3035', 'sum')]/kol_golov*100
				n3540 = table.ix[line,('n3540', 'sum')]/kol_golov*100
				n4045 = table.ix[line,('n4045', 'sum')]/kol_golov*100
				n45 = table.ix[line,('n45', 'sum')]/kol_golov*100
			table2.append([	line,
							table.ix[line,('kol_milk', 'mean')],
							kol_golov,
							n015,
							 n1520,
							 n2025,
							 n2530,
							 n3035,
							 n3540,
							 n4045,
							 n45])


			zagon.append(
						{
							'GROEPNR':line,
							'kol': table.ix[line,('kol_milk', 'mean')],
							'sko': table.ix[line,('kol_milk', 'std')],
							'kol_golov': kol_golov,
							'procent_0_15': n015,
							'procent_15_20': n1520,
							'procent_20_25': n2025,
							'procent_25_30': n2530,
							'procent_30_35': n3035,
							'procent_35_40': n3540,
							'procent_40_45': n4045,
							'procent_45': n45
						}
			
			)
	#res.append({'zagons': zagon})


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
	kol_golov = 0

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

	



	####   Надой по лактация и дням лактации  ################
	zapros=r""" select
 
				        (case
				            when l.LACTATIENR>2 then 3
				            else l.LACTATIENR
				        end) nomer_lakt,
				        
				        
		                count(DISTINCT case 
		                    when (z1.DATUM-l.DATUMAFKALVEN)<=40 Then z1.DIERID
		                    
		                end) as kg40,
		                AVG(case 
		                    when (z1.DATUM-l.DATUMAFKALVEN)<=40 Then z1.kol_milk
		                    
		                end) as mg40,
		                    
		                count(DISTINCT case     
		                    when (z1.DATUM-l.DATUMAFKALVEN)>40 and (z1.DATUM-l.DATUMAFKALVEN)<=150 Then z1.DIERID
		                end) as kg40150, 
		                AVG(case     
		                    when (z1.DATUM-l.DATUMAFKALVEN)>40 and (z1.DATUM-l.DATUMAFKALVEN)<=150 Then z1.kol_milk
		                end) as mg40150,
		                
		                count(DISTINCT case   
		                    when (z1.DATUM-l.DATUMAFKALVEN)>150 and (z1.DATUM-l.DATUMAFKALVEN)<=300 Then z1.DIERID
		                end) as kg150300,  
		                AVG(case   
		                    when (z1.DATUM-l.DATUMAFKALVEN)>150 and (z1.DATUM-l.DATUMAFKALVEN)<=300 Then z1.kol_milk
		                end) as mg150300,
		                  
		                count(DISTINCT case
		                    when (z1.DATUM-l.DATUMAFKALVEN)>300  Then z1.DIERID
		                end) as kg300,
		                AVG(case
		                    when (z1.DATUM-l.DATUMAFKALVEN)>300  Then z1.kol_milk
		                end) as mg300,
		                
		                count(z1.DIERID) as vsego_gol,
		                AVG(z1.kol_milk) as vsego_milk
				                       
				                
				From             
		                (SELECT 
							(case
		                        when r.TIJDSTIPEIND<'03:00:00.000' then r.DATUM-1
		                        else r.DATUM
		                    end) as DATUM,
							r.DIERID,
							Sum(r.HOEVEELHEIDMELK) as kol_milk
							FROM DIER_MELKGIFT r 
							where r.HOEVEELHEIDMELK<100 and (case
		                                            when r.TIJDSTIPEIND<'03:00:00.000' then r.DATUM-1
		                                            else r.DATUM
		                                        end)=?	
		                Group By 1, r.DIERID
		                ) as z1,
		                
		                DIER_MELKGIFT_LACTATIE l
		                Where l.DIERID=z1.DIERID and l.DATUMAFKALVEN=(
		                    Select first 1 T.DATUMAFKALVEN From DIER_MELKGIFT_LACTATIE T 
		                    Where T.DATUMAFKALVEN<z1.DATUM and T.DIERID=z1.DIERID
		                    Order by T.DATUMAFKALVEN Desc
		                )
		                and l.LACTATIENR=(
		                    Select first 1 T.LACTATIENR From DIER_MELKGIFT_LACTATIE T 
		                    Where T.DATUMAFKALVEN<z1.DATUM and T.DIERID=z1.DIERID
		                    Order by T.DATUMAFKALVEN Desc
		                )
				                
				Group by 1"""
	param=(date,)
	result=con_uniform(zapros,param,2)

	nadoy_l1=nadoy_l2=nadoy_l3=0
	nadoy_0_40=nadoy_40_150=nadoy_150_300=nadoy_300=0
	nadoy_l1_0_40=nadoy_l1_40_150=nadoy_l1_150_300=nadoy_l1_300=0
	nadoy_l2_0_40=nadoy_l2_40_150=nadoy_l2_150_300=nadoy_l2_300=0
	nadoy_l3_0_40=nadoy_l3_40_150=nadoy_l3_150_300=nadoy_l3_300=0

	itog_gol=itog_gol040=itog_gol40150=itog_gol150300=itog_gol300=0
	itog=itog040=itog40150=itog150300=itog300=0


	if len(result)>0:

		for line in result:

			if line[0] == 1:
				nadoy_l1 = line[10]
				nadoy_l1_0_40 = line[2]
				nadoy_l1_40_150 = line[4]
				nadoy_l1_150_300 = line[6]
				nadoy_l1_300 = line[8]

			if line[0] == 2:
				nadoy_l2 = line[10]
				nadoy_l2_0_40 = line[2]
				nadoy_l2_40_150 = line[4]
				nadoy_l2_150_300 = line[6]
				nadoy_l2_300 = line[8]

			if line[0] == 3:
				nadoy_l3 = line[10]
				nadoy_l3_0_40 = line[2]
				nadoy_l3_40_150 = line[4]
				nadoy_l3_150_300 = line[6]
				nadoy_l3_300 = line[8]

			#Средневзвешенное по дням лактации
			itog040 += line[2] * line[1]
			itog40150 += line[4] * line[3]
			itog150300 += line[6] * line[5]
			itog300 += line[8] * line[7]

			itog_gol += line[9]
			itog_gol040 += line[1]
			itog_gol40150 += line[3]
			itog_gol150300 += line[5]
			itog_gol300 += line[7]

		nadoy_0_40 = itog040 / itog_gol040
		nadoy_40_150 = itog40150 / itog_gol40150
		nadoy_150_300 = itog150300 / itog_gol150300
		nadoy_300 = itog300 / itog_gol300


	res= {
				'nadoy' : 
						{
							'nadoy_l1': float(nadoy_l1),
							'nadoy_l2': float(nadoy_l2),
							'nadoy_l3': float(nadoy_l3),
							'nadoy_0_40': float(nadoy_0_40),
							'nadoy_40_150': float(nadoy_40_150),
							'nadoy_150_300': float(nadoy_150_300),
							'nadoy_300': float(nadoy_300),
							'nadoy_l1_0_40': float(nadoy_l1_0_40),
							'nadoy_l1_40_150': float(nadoy_l1_40_150),
							'nadoy_l1_150_300': float(nadoy_l1_150_300),
							'nadoy_l1_300': float(nadoy_l1_300),
							'nadoy_l2_0_40': float(nadoy_l2_0_40),
							'nadoy_l2_40_150': float(nadoy_l2_40_150),
							'nadoy_l2_150_300': float(nadoy_l2_150_300),
							'nadoy_l2_300': float(nadoy_l2_300),
							'nadoy_l3_0_40': float(nadoy_l3_0_40),
							'nadoy_l3_40_150': float(nadoy_l3_40_150),
							'nadoy_l3_150_300': float(nadoy_l3_150_300),
							'nadoy_l3_300': float(nadoy_l3_300)
						},
				#'table' : table1,
				'kol_golov' : kol_golov,

				'zagons': zagon,

				'procent':
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
				}


	#print zagon
	
	data = json.dumps(res)
	#print data
	
	return data