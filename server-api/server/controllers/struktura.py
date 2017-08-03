#!/usr/bin/env python
# -*- coding: utf-8 -*-
from server import app
from bottle import request, jinja2_template as template
import json
from db_connect import con_uniform

@app.route('/api/struktura_stada', method='GET')
def index():
   #tree=menuleft()
   tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
	]
   #return  json.dumps({'tasks': tasks})
   """SELECT 
r.status,
g.OMSCHRIJVING as ZAGON,

 
					count(r.DIERID)
					
					FROM DIER r
					left join GROEP g on 
                            case 
                                when r.GROEPID is Null then '-2147483645' 
                                else r.GROEPID 
                            end=g.GROEPID
					Where r.STATUS!='9' and r.STATUS!='10'-- and r.STATUS!='5'
					--where ((r.STATUS!='9' and r.STATUS!='10') or ((r.STATUS='9' or r.STATUS='10') ))  
					Group by r.GROEPID, g.OMSCHRIJVING, r.status Order by r.status"""
   
   
   
