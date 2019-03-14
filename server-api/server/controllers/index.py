#!/usr/bin/env python
# -*- coding: utf-8 -*-
from server import app
from bottle import request, jinja2_template as template, TEMPLATE_PATH

TEMPLATE_PATH.append("./views")

@app.route('/', method='GET')
def index():
   #tree=menuleft()
   return template('index.html')



@app.route('/zatrati', method='GET')
def zatrati():
   #tree=menuleft()
   out = u"""
   <table>
	    <tr>
	   		<th>Date</th>
	   		<th>Value</th>

	   	</tr>
	   
	   	<tr>
	   		<td>22.11.2018</td>
	   		<td>14</td>

	   	</tr>
	   	<tr>
	   		<td>23.11.2018</td>
	   		<td>16</td>

	   	</tr>

   </table>




   """
   return out#template('./views/zatrati.html')