#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from server import app
from bottle import debug, run
from config import IP, PORT_API



debug(True) #"""Включаем отладку"""
if __name__ == '__main__':
    port = int(os.environ.get("PORT", PORT_API))
    run(app, reloader=True, host=IP, port=port)