#!/usr/bin/env python
# -*- coding: utf-8 -*-
from server import app
from bottle import request, jinja2_template as template

@app.route('/', method='GET')
def index():
   #tree=menuleft()
   return template('index.html')