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


class korm_analiz_kormleniya_report(models.Model):
	_name = "korm.analiz_kormleniya_report"
	_description = "analiz_kormleniya_report"
	#_auto = False
	# _rec_name = 'nomen_nomen_id'


	@api.one
	@api.depends('month', 'year')
	def return_name(self):
		if self.month and self.year:
			self.name = self.year + '-' + self.month
			self.date_start = datetime.strptime(self.year+'-'+self.month+'-01', "%Y-%m-%d").date()
			last_day = last_day_of_month(self.date_start)
			self.date_end = last_day
			self.count_day = last_day.day
		#if month == '01' : month_text = u"Январь"
		if self.month == '01' : self.month_text = u"Январь"
		if self.month == '02' : self.month_text = u"Февряль"
		if self.month == '03' : self.month_text = u"Март"
		if self.month == '04' : self.month_text = u"Апрель"
		if self.month == '05' : self.month_text = u"Май"
		if self.month == '06' : self.month_text = u"Июнь"
		if self.month == '07' : self.month_text = u"Июль"
		if self.month == '08' : self.month_text = u"Август"
		if self.month == '09' : self.month_text = u"Сентябрь"
		if self.month == '10' : self.month_text = u"Октябрь"
		if self.month == '11' : self.month_text = u"Ноябрь"
		if self.month == '12' : self.month_text = u"Декабрь"


	
	# date = fields.Date(string='Дата')
	# # nomen_nomen_id = fields.Many2one('nomen.nomen', string=u'Наименование корма')
	# stado_fiz_group_id = fields.Many2one('stado.fiz_group', string=u'Физ. группа')
	# stado_vid_fiz_group_id = fields.Many2one('stado.vid_fiz_group', string=u'Вид физ. группы')

	# month = fields.Text(string=u"Месяц")
	# year = fields.Text(string=u"Год")

	month = fields.Selection([
		('01', "Январь"),
		('02', "Февряль"),
		('03', "Март"),
		('04', "Апрель"),
		('05', "Май"),
		('06', "Июнь"),
		('07', "Июль"),
		('08', "Август"),
		('09', "Сентябрь"),
		('10', "Октябрь"),
		('11', "Ноябрь"),
		('12', "Декабрь"),
	], default='', required=True, string=u"Месяц")
	
	year = fields.Char(string=u"Год", required=True, default=str(datetime.today().year))
	month_text = fields.Char(string=u"Год", compute='return_name')

	date = fields.Date(string='Дата', required=True, index=True, copy=False, default=fields.Date.today())
	date_start = fields.Date(string='Дата начала', required=True, index=True, copy=False, compute='return_name')
	date_end = fields.Date(string='Дата окончания', required=True, index=True, copy=False, compute='return_name')
	
	count_day = fields.Integer(string=u"Кол-во дней в периоде", compute='return_name')
