# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError
import math


class krs_result_otel(models.Model):
	_name = 'krs.result_otel'
	_description = u'Результаты отелов'
	_order = 'name'

	@api.one
	@api.depends('kol_telok_jiv', 'kol_telok_mert', 'kol_bik_jiv', 'kol_bik_mert', 'kol_mert')
	def _raschet(self):
		self.kol_itog_jiv = self.kol_telok_jiv + self.kol_bik_jiv
		self.kol_itog_mert = self.kol_telok_mert + self.kol_bik_mert + self.kol_mert
		self.kol_itog = self.kol_itog_jiv + self.kol_itog_mert


	name = fields.Char(string=u"Наименование", required=True)

	kol_itog = fields.Integer(string=u"Всего родилось", store=True, compute='_raschet')
	kol_itog_jiv = fields.Integer(string=u"Всего Живых", store=True, compute='_raschet')
	kol_itog_mert = fields.Integer(string=u"Всего Мертвородов", store=True, compute='_raschet')
	kol_telok_jiv = fields.Integer(string=u"Живых телок", store=True)
	kol_telok_mert = fields.Integer(string=u"Мертв. телок", store=True)
	kol_bik_jiv = fields.Integer(string=u"Живых бычков", store=True)
	kol_bik_mert = fields.Integer(string=u"Мертв. бычков", store=True)
	kol_mert = fields.Integer(string=u"Мертвородов", store=True)



class krs_hoz(models.Model):
	_name = 'krs.hoz'
	_description = u'Хозяйства'
	_order = 'name'


	name = fields.Char(string=u"Наименование", required=True)

	kod = fields.Integer(string=u"Код", store=True)
	nashe = fields.Boolean(string=u"Наше хозяйство", default=False)
	selex_id = fields.Integer(string=u"selex_id", default=False)



class krs_spv(models.Model):
	_name = 'krs.spv'
	_description = u'Справочник Причины выбытия'
	_order = 'name'

	name = fields.Char(string=u"Наименование", required=True)
	
	kod = fields.Integer(string=u"Код",required=True)


class krs_srashod(models.Model):
	_name = 'krs.srashod'
	_description = u'Справочник Расход КРС'
	_order = 'name'

	name = fields.Char(string=u"Наименование", required=True)
	
	kod = fields.Integer(string=u"Код",required=True)






class krs_otel(models.Model):
	_name = 'krs.otel'
	_description = u'Отелы КРС'
	_order = 'name'

	@api.one
	def _raschet_load(self):
		
		result_otel = self.env['krs.result_otel'].search([('name', '=', self.result)],limit=1)
		
		print "/////////////////////////", result_otel

		
		result_hoz = self.env['krs.hoz'].search([('kod', '=', self.kod_hoz)],limit=1)
		if len(result_hoz)>0:
			self.krs_hoz_id = result_hoz
			print "\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", result_hoz

	
		if len(result_otel)>0:
			self.krs_result_otel_id = result_otel.id
			self.kol_itog = result_otel.kol_itog
			self.kol_itog_jiv = result_otel.kol_itog_jiv
			self.kol_itog_mert = result_otel.kol_itog_mert
			self.kol_telok_jiv = result_otel.kol_telok_jiv
			self.kol_telok_mert = result_otel.kol_telok_mert
			self.kol_bik_jiv = result_otel.kol_bik_jiv
			self.kol_bik_mert = result_otel.kol_bik_mert
			self.kol_mert = result_otel.kol_mert

		self.name = self.inv_nomer

	@api.one
	@api.depends('krs_result_otel_id','result', 'inv_nomer','kod_hoz')
	def _raschet(self):
		result_otel = []
		if self.result:
			result_otel = self.env['krs.result_otel'].search([('name', '=', self.result)],limit=1)
		elif self.krs_result_otel_id:
			result_otel = self.krs_result_otel_id
			self.result = self.krs_result_otel_id.name

		if self.kod_hoz:
			result_hoz = self.env['krs.hoz'].search([('kod', '=', self.kod_hoz)],limit=1)
			if len(result_hoz)>0:
				self.krs_hoz_id = result_hoz.id
		elif self.krs_hoz_id:
			self.kod_hoz = self.krs_hoz_id.kod

		if len(result_otel)>0:
			self.krs_result_otel_id = result_otel.id
			self.kol_itog = result_otel.kol_itog
			self.kol_itog_jiv = result_otel.kol_itog_jiv
			self.kol_itog_mert = result_otel.kol_itog_mert
			self.kol_telok_jiv = result_otel.kol_telok_jiv
			self.kol_telok_mert = result_otel.kol_telok_mert
			self.kol_bik_jiv = result_otel.kol_bik_jiv
			self.kol_bik_mert = result_otel.kol_bik_mert
			self.kol_mert = result_otel.kol_mert

		self.name = self.inv_nomer


	name = fields.Char(string=u"Наименование", compute='_raschet', store=True)
	inv_nomer = fields.Char(string=u"Инв. №", required=True)
	kod_hoz = fields.Integer(string=u"Код хоз. рождения",required=True)
	date = fields.Date(string='Дата', required=True, default=fields.Datetime.now)
	nomer_lakt = fields.Integer(string=u"Номер лактации",required=True)
	result = fields.Char(string=u"Результат", required=True)
	krs_result_otel_id = fields.Many2one('krs.result_otel', string='Результат отела')
	krs_hoz_id = fields.Many2one('krs.hoz', string='Хозяйство рождения')
	
	kol_itog = fields.Integer(string=u"Всего родилось", store=True, compute='_raschet')
	kol_itog_jiv = fields.Integer(string=u"Всего Живых", store=True, compute='_raschet')
	kol_itog_mert = fields.Integer(string=u"Всего Мертвородов", store=True, compute='_raschet')
	kol_telok_jiv = fields.Integer(string=u"Живых телок", store=True, compute='_raschet')
	kol_telok_mert = fields.Integer(string=u"Мертв. телок", store=True, compute='_raschet')
	kol_bik_jiv = fields.Integer(string=u"Живых бычков", store=True, compute='_raschet')
	kol_bik_mert = fields.Integer(string=u"Мертв. бычков", store=True, compute='_raschet')
	kol_mert = fields.Integer(string=u"Мертвородов", store=True, compute='_raschet')



