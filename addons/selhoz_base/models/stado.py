# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError
import math




class stado_vid_fiz_group(models.Model):
	_name = 'stado.vid_fiz_group'
	_description = u'Вид физиологической группы'
	_order = 'name'

	name = fields.Char(string=u"Наименование", required=True)
	_sql_constraints = [
							('name_unique', 'unique(name)', u'Такой вид физиологической группы уже существует!')
						]

class stado_podvid_fiz_group(models.Model):
	_name = 'stado.podvid_fiz_group'
	_description = u'Подвид физиологической группы'
	_order = 'name'

	name = fields.Char(string=u"Наименование", required=True)
	_sql_constraints = [
							('name_unique', 'unique(name)', u'Такой подвид физиологической группы уже существует!')
						]


class stado_fiz_group(models.Model):
	_name = 'stado.fiz_group'
	_description = u'Физиологическая группа'
	_order = 'name'

	name = fields.Char(string=u"Наименование", required=True)
	stado_vid_fiz_group_id = fields.Many2one('stado.vid_fiz_group', string='Вид физ. группы')
	stado_podvid_fiz_group_id = fields.Many2one('stado.podvid_fiz_group', string='Подвид физ. группы')
	_sql_constraints = [
							('name_unique', 'unique(name)', u'Такая физиологическая группа уже существует!')
						]
	


class stado_zagon(models.Model):
	_name = 'stado.zagon'
	_description = u'Загоны'
	_order = 'nomer'

	@api.multi
	def name_get(self):
		zagon_tolko_nomer = self.env.context.get('zagon_tolko_nomer', False)
		
		if zagon_tolko_nomer:
			res = []
			for doc in self:
				res.append((doc.id, doc.nomer))
			
		else:
			res = super(stado_zagon, self).name_get()


		return res
	@api.one
	def toggle_activ(self):
		if self.activ == True:
			self.activ = False
		else:
			self.activ =True
		

	name = fields.Char(string=u"Наименование", readonly=False, index=True, store=True)
	nomer = fields.Integer(string=u"Номер", required=True)
	stado_fiz_group_id = fields.Many2one('stado.fiz_group', string='Физиологическая группа', required=True)
	uniform_id = fields.Integer(string=u"ID Uniform",default=-1)
	utro = fields.Integer(string=u"Утро,%", default=100)
	vecher = fields.Integer(string=u"Вечер,%", default=0)
	#active = fields.Boolean(string=u"Активный", default=True)
	activ = fields.Boolean(string=u"Используется", default=True, oldname='active')
	date_start = fields.Date(string=u"Дата начала", default=fields.Datetime.now)
	date_end = fields.Date(string=u"Дата окончания")
	doynie = fields.Boolean(string=u"Дойные", default=False)
	mastit = fields.Boolean(string=u"Маститные", default=False)
	suhostoy = fields.Boolean(string=u"Сухостой", default=False)