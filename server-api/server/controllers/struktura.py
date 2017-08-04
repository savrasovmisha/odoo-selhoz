#!/usr/bin/env python
# -*- coding: utf-8 -*-
from server import app
from bottle import request, jinja2_template as template
import json
from db_connect import con_uniform

@app.route('/api/struktura_stada', method='GET')
def index():
 
	zapros=r"""SELECT 
					r.GROEPID,
					g.OMSCHRIJVING as ZAGON,
					count(r.DIERID)
					
					FROM DIER r
					left join GROEP g on 
                            case 
                                when r.GROEPID is Null then '-2147483645' 
                                else r.GROEPID 
                            end=g.GROEPID
					Where r.STATUS!='9' and r.STATUS!='10'  
					Group by r.GROEPID, g.OMSCHRIJVING
					Order by g.OMSCHRIJVING"""
   
	result=con_uniform(zapros,'',2)
	zagon = []
	for line in result:
		zagon.append(
					{
						'id':line[0],
						'name': line[1],
						'kol_golov_zagon': line[2]
					}
		
		)
	print zagon
	
	data = json.dumps(zagon)
	print data
	
	return data
   
