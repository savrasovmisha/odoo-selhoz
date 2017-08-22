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

	abort = fields.Boolean(string=u"Аборт", default=False)

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
	_order = 'date desc'

	@api.one
	def _raschet_load(self, hoz_selex_id, result):
		
		result_otel = self.env['krs.result_otel'].search([('name', '=', result)],limit=1)
		
		#print "/////////////////////////", result_otel

		
		result_hoz = self.env['krs.hoz'].search([('selex_id', '=', hoz_selex_id)],limit=1)
		if len(result_hoz)>0:
			self.krs_hoz_id = result_hoz
			#print "\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", result_hoz

	
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
			self.abort = result_otel.abort

		self.name = self.inv_nomer
		self.nomer_lakt_str = str(self.nomer_lakt)

	@api.one
	@api.depends('krs_result_otel_id', 'inv_nomer')
	def _raschet(self):
		
		if self.krs_result_otel_id:
			
			self.kol_itog = self.krs_result_otel_id.kol_itog
			self.kol_itog_jiv = self.krs_result_otel_id.kol_itog_jiv
			self.kol_itog_mert = self.krs_result_otel_id.kol_itog_mert
			self.kol_telok_jiv = self.krs_result_otel_id.kol_telok_jiv
			self.kol_telok_mert = self.krs_result_otel_id.kol_telok_mert
			self.kol_bik_jiv = self.krs_result_otel_id.kol_bik_jiv
			self.kol_bik_mert = self.krs_result_otel_id.kol_bik_mert
			self.kol_mert = self.krs_result_otel_id.kol_mert
			self.abort = self.krs_result_otel_id.abort

		self.name = self.inv_nomer
		self.nomer_lakt_str = str(self.nomer_lakt)


	name = fields.Char(string=u"Наименование", compute='_raschet', store=True)
	inv_nomer = fields.Char(string=u"Инв. №", required=True)
	
	date = fields.Date(string='Дата', required=True, default=fields.Datetime.now)
	nomer_lakt = fields.Integer(string=u"Номер лактации",required=True)
	nomer_lakt_str = fields.Char(string=u"Номер лактации")
	
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

	abort = fields.Boolean(string=u"Аборт", default=False)


class krs_cow_vibitiya(models.Model):
	_name = 'krs.cow_vibitiya'
	_description = u'Выбытия коров'
	_order = 'date desc'


	@api.one
	@api.depends('inv_nomer')
	def _get_name(self):

		self.name = self.inv_nomer


	@api.one
	def _raschet(self, hoz_selex_id, kod_spv, kod_srashod):

		if hoz_selex_id:
			result_hoz = self.env['krs.hoz'].search([('selex_id', '=', hoz_selex_id)],limit=1)
			if len(result_hoz)>0:
				self.krs_hoz_id = result_hoz

		if kod_spv:
			result_spv = self.env['krs.spv'].search([('kod', '=', kod_spv)],limit=1)
			if len(result_spv)>0:
				self.krs_spv_id = result_spv
		if kod_srashod:
			result_srashod = self.env['krs.srashod'].search([('kod', '=', kod_srashod)],limit=1)
			if len(result_srashod)>0:
				self.krs_srashod_id = result_srashod

		self.name = self.inv_nomer
		self.nomer_lakt_str = str(self.nomer_lakt)


	name = fields.Char(string=u"Наименование", compute='_get_name', store=True)
	inv_nomer = fields.Char(string=u"Инв. №", required=True)
	date_rogd = fields.Date(string='Дата рождения', required=True)
	date = fields.Date(string='Дата выбытия', required=True, default=fields.Datetime.now)
	nomer_lakt = fields.Integer(string=u"Номер лактации",required=True)
	nomer_lakt_str = fields.Char(string=u"Номер лактации")


	krs_hoz_id = fields.Many2one('krs.hoz', string='Хозяйство рождения')

	krs_spv_id = fields.Many2one('krs.spv', string='Причина выбытия')

	krs_srashod_id = fields.Many2one('krs.srashod', string='Вид расхода')



class krs_tel_vibitiya(models.Model):
	_name = 'krs.tel_vibitiya'
	_description = u'Выбытия телят'
	_order = 'date desc'


	@api.one
	@api.depends('inv_nomer')
	def _get_name(self):

		self.name = self.inv_nomer


	@api.one
	def _raschet(self, hoz_selex_id, kod_spv, kod_srashod):

		if hoz_selex_id:
			result_hoz = self.env['krs.hoz'].search([('selex_id', '=', hoz_selex_id)],limit=1)
			if len(result_hoz)>0:
				self.krs_hoz_id = result_hoz

		if kod_spv:
			result_spv = self.env['krs.spv'].search([('kod', '=', kod_spv)],limit=1)
			if len(result_spv)>0:
				self.krs_spv_id = result_spv
		if kod_srashod:
			result_srashod = self.env['krs.srashod'].search([('kod', '=', kod_srashod)],limit=1)
			if len(result_srashod)>0:
				self.krs_srashod_id = result_srashod

		self.name = self.inv_nomer
		


	name = fields.Char(string=u"Наименование", compute='_get_name', store=True)
	inv_nomer = fields.Char(string=u"Инв. №", required=True)
	status = fields.Char(string=u"Статус", required=True)
	date_rogd = fields.Date(string='Дата рождения', required=True)
	date = fields.Date(string='Дата выбытия', required=True, default=fields.Datetime.now)

	krs_hoz_id = fields.Many2one('krs.hoz', string='Хозяйство рождения')

	krs_spv_id = fields.Many2one('krs.spv', string='Причина выбытия')

	krs_srashod_id = fields.Many2one('krs.srashod', string='Вид расхода')