# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import tools
from openerp import models, fields, api
from datetime import datetime, timedelta, date
from openerp.exceptions import ValidationError

import sys
import os
import base64
import zipfile
import tempfile
from pandas import DataFrame, pivot_table
from xlsxwriter.utility import xl_rowcol_to_cell
import xlsxwriter
import pandas as pd
import numpy as np

def week_magic(day):
	if type(day)==str:
		day = datetime.strptime(day, "%Y-%m-%d").date()
	day_of_week = day.weekday()

	to_beginning_of_week = timedelta(days=day_of_week)
	beginning_of_week = day - to_beginning_of_week

	to_end_of_week = timedelta(days=6 - day_of_week)
	end_of_week = day + to_end_of_week
	number_of_week = day.isocalendar()[1]

	return (beginning_of_week, end_of_week, number_of_week)

def last_day_of_month(date):
	if type(date)==str:
		date = datetime.strptime(date, "%Y-%m-%d").date()
	if date.month == 12:
		return date.replace(day=31)
	return date.replace(month=date.month+1, day=1) - timedelta(days=1)



class sklad_ostatok_report(models.Model):
	_name = "sklad.ostatok_report"
	_description = "Остатки склада"
	_auto = False
	_rec_name = 'nomen_nomen_id'
	_order = 'nomen_nomen_id desc'

	

	sklad_osnovnoy_id = fields.Many2one('sklad.sklad', string='Склад основной')
	sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад')
	nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура')
	kol = fields.Float(digits=(10, 3), string=u"Кол-во")
	price = fields.Float(digits=(10, 2), string=u"Цена" , group_operator="avg")
	amount = fields.Float(digits=(10, 2), string=u"Сумма")


	def init(self, cr):

		tools.sql.drop_view_if_exists(cr, self._table)
		cr.execute("""
			create or replace view sklad_ostatok_report as (
				WITH currency_rate as (%s)
				SELECT
					o.id as id,
					o.nomen_nomen_id as nomen_nomen_id,
					s.sklad_osnovnoy_id as sklad_osnovnoy_id,
					o.sklad_sklad_id as sklad_sklad_id,
					o.kol as kol,
					p.price as price,
					(p.price*o.kol) as amount
				FROM sklad_ostatok o
				LEFT JOIN sklad_ostatok_price p on (p.nomen_nomen_id = o.nomen_nomen_id)
				LEFT JOIN sklad_sklad s on (s.id = o.sklad_sklad_id)
				WHERE o.kol != 0





					

						
				)
		""" % self.pool['res.currency']._select_companies_rates())
