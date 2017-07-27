# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError
import math

parametrs = ['ov', 'sv', 'oe', 'sp', 'pp', 'sk', 'sj', 'ca', 'p', 
		'sahar', 'krahmal', 'bev', 'magniy', 'natriy', 'kaliy', 'hlor', 'sera', 
		'udp', 'me', 'xp', 'nrp', 'rnb', 'nrp_p']

class korm_pit_standart(models.Model):
	_name = 'korm.pit_standart'
	_description = u'Питательность кормов по стандарту'
	_order = 'nomen_nomen_id'


	@api.one
	@api.depends('nomen_nomen_id')
	def return_name(self):
		self.name = self.nomen_nomen_id.name


	@api.one
	@api.depends('sv', 'oe', 'sv', 'nrp_p')
	def _raschet(self):
		
		if self.sv and self.nrp_p:
			self.nrp = self.sp * self.nrp_p/100.00
		
		if self.sv>0 and self.nrp:
			self.udp = self.nrp/self.sv

		if self.sv>0 and self.oe:
			self.me = self.oe/self.sv

		if self.sv>0 and self.sp:
			self.xp = self.sp/self.sv

		if self.xp!=0 and self.me and self.udp:
			self.rnb = (self.xp-((11.93-(6.82*(self.udp/self.xp)))*self.me+(1.03*self.udp)))/6.25



	name = fields.Char(string=u"Наименование", compute='return_name')
	nomen_nomen_id = fields.Many2one('nomen.nomen', string='Наименование корма', required=True)
	ov = fields.Float(digits=(10, 2), string=u"ОВ")
	sv = fields.Float(digits=(10, 2), string=u"СВ")
	oe = fields.Float(digits=(10, 2), string=u"ОЭ")
	sp = fields.Float(digits=(10, 2), string=u"СП")
	pp = fields.Float(digits=(10, 2), string=u"ПП")
	sk = fields.Float(digits=(10, 2), string=u"СК")
	sj = fields.Float(digits=(10, 2), string=u"СЖ")
	ca = fields.Float(digits=(10, 2), string=u"Ca")
	p = fields.Float(digits=(10, 2), string=u"P")
	sahar = fields.Float(digits=(10, 2), string=u"Сахар")
	krahmal = fields.Float(digits=(10, 2), string=u"Крахмал")
	bev = fields.Float(digits=(10, 2), string=u"БЭВ")
	magniy = fields.Float(digits=(10, 2), string=u"Магний")
	natriy = fields.Float(digits=(10, 2), string=u"Натрий")
	kaliy = fields.Float(digits=(10, 2), string=u"Калий")
	hlor = fields.Float(digits=(10, 2), string=u"Хлор")
	sera = fields.Float(digits=(10, 2), string=u"Сера")
	udp = fields.Float(digits=(10, 2), string=u"UDP", store=True, compute='_raschet')
	me = fields.Float(digits=(10, 2), string=u"ME", store=True, compute='_raschet')
	xp = fields.Float(digits=(10, 2), string=u"XP", store=True, compute='_raschet')
	nrp = fields.Float(digits=(10, 2), string=u"НРП", store=True, compute='_raschet')
	rnb = fields.Float(digits=(10, 2), string=u"RNB", store=True, compute='_raschet')
	nrp_p = fields.Float(digits=(10, 2), string=u"%НРП")

	_sql_constraints = [
							('nomen_nomen_id_unique', 'unique(nomen_nomen_id)', u'Питательность для такого корма уже существует!')
						]

class stado_vid_fiz_group(models.Model):
	_name = 'stado.vid_fiz_group'
	_description = u'Вид физиологической группы'
	_order = 'name'

	name = fields.Char(string=u"Наименование", required=True)
	_sql_constraints = [
							('name_unique', 'unique(name)', u'Такой вид физиологической группы уже существует!')
						]

class stado_fiz_group(models.Model):
	_name = 'stado.fiz_group'
	_description = u'Физиологическая группа'
	_order = 'name'

	name = fields.Char(string=u"Наименование", required=True)
	stado_vid_fiz_group_id = fields.Many2one('stado.vid_fiz_group', string='Вид физ. группы')
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


	name = fields.Char(string=u"Наименование", readonly=False, index=True, store=True)
	nomer = fields.Integer(string=u"Номер", required=True)
	stado_fiz_group_id = fields.Many2one('stado.fiz_group', string='Физиологическая группа', required=True)
	uniform_id = fields.Integer(string=u"ID Uniform")
	utro = fields.Integer(string=u"Утро,%", default=100)
	vecher = fields.Integer(string=u"Вечер,%", default=0)


class korm_analiz_pit(models.Model):
	_name = 'korm.analiz_pit'
	_description = u'Анализ питательности кормов'
	_order = 'date desc, nomen_nomen_id'




	@api.multi
	def unlink(self):
		
		for pp in self:
			if pp.korm_receptura_id:
				raise exceptions.ValidationError(_(u"Документ анализа %s от %s не может быть удален, т.к создан на основании Рецептуры комбикорма и удаляется вместе с ним!  " % (pp.nomen_nomen_id.name, pp.date)))

		return super(korm_analiz_pit, self).unlink()

	@api.one
	@api.depends('nomen_nomen_id')
	def return_name(self):
		self.name = self.nomen_nomen_id.name + u" от " + self.date


	@api.one
	@api.depends('sv', 'oe', 'sv', 'nrp_p')
	def _raschet(self):
		
		if self.sv and self.nrp_p:
			self.nrp = self.sp * self.nrp_p/100.00
		
		if self.sv>0 and self.nrp:
			self.udp = self.nrp/self.sv

		if self.sv>0 and self.oe:
			self.me = self.oe/self.sv

		if self.sv>0 and self.sp:
			self.xp = self.sp/self.sv

		if self.xp!=0 and self.me and self.udp:
			self.rnb = (self.xp-((11.93-(6.82*(self.udp/self.xp)))*self.me+(1.03*self.udp)))/6.25

	#@api.one
	@api.depends('nomen_nomen_id')
	def _standart(self):
		for st in self:
			if st.nomen_nomen_id:
				standart = self.env['korm.pit_standart'].search([('nomen_nomen_id', '=', st.nomen_nomen_id.id)],limit=1)
				if len(standart)>0:
					st.ov_s=standart.ov
					st.sv_s=standart.sv
					st.oe_s=standart.oe
					st.sp_s=standart.sp
					st.pp_s=standart.pp
					st.sk_s=standart.sk
					st.sj_s=standart.sj
					st.ca_s=standart.ca
					st.p_s=standart.p
					st.sahar_s=standart.sahar
					st.krahmal_s=standart.krahmal
					st.bev_s=standart.bev
					st.magniy_s=standart.magniy
					st.natriy_s=standart.natriy
					st.kaliy_s=standart.kaliy
					st.hlor_s=standart.hlor
					st.sera_s=standart.sera
					st.udp_s=standart.udp
					st.me_s=standart.me
					st.xp_s=standart.xp
					st.nrp_s=standart.nrp
					st.rnb_s=standart.rnb
					st.nrp_p_s=standart.nrp_p


	name = fields.Char(string=u"Наименование", compute='return_name')
	nomen_nomen_id = fields.Many2one('nomen.nomen', string='Наименование корма', required=True)
	korm_receptura_id = fields.Many2one('korm.receptura', ondelete='cascade', string='Рецептура комбикорма')

	date = fields.Date(string='Дата', required=True, default=fields.Datetime.now)
	ov = fields.Float(digits=(10, 2), string=u"ОВ")
	sv = fields.Float(digits=(10, 2), string=u"СВ")
	oe = fields.Float(digits=(10, 2), string=u"ОЭ")
	sp = fields.Float(digits=(10, 2), string=u"СП")
	pp = fields.Float(digits=(10, 2), string=u"ПП")
	sk = fields.Float(digits=(10, 2), string=u"СК")
	sj = fields.Float(digits=(10, 2), string=u"СЖ")
	ca = fields.Float(digits=(10, 2), string=u"Ca")
	p = fields.Float(digits=(10, 2), string=u"P")
	sahar = fields.Float(digits=(10, 2), string=u"Сахар")
	krahmal = fields.Float(digits=(10, 2), string=u"Крахмал")
	bev = fields.Float(digits=(10, 2), string=u"БЭВ")
	magniy = fields.Float(digits=(10, 2), string=u"Магний")
	natriy = fields.Float(digits=(10, 2), string=u"Натрий")
	kaliy = fields.Float(digits=(10, 2), string=u"Калий")
	hlor = fields.Float(digits=(10, 2), string=u"Хлор")
	sera = fields.Float(digits=(10, 2), string=u"Сера")
	udp = fields.Float(digits=(10, 2), string=u"UDP", store=True, compute='_raschet')
	me = fields.Float(digits=(10, 2), string=u"ME", store=True, compute='_raschet')
	xp = fields.Float(digits=(10, 2), string=u"XP", store=True, compute='_raschet')
	nrp = fields.Float(digits=(10, 2), string=u"НРП", store=True, compute='_raschet')
	rnb = fields.Float(digits=(10, 2), string=u"RNB", store=True, compute='_raschet')
	nrp_p = fields.Float(digits=(10, 2), string=u"%НРП")
	#Параметры питательности по стандарту:
	ov_s = fields.Float(digits=(10, 2), string=u"ОВ", compute='_standart')
	sv_s = fields.Float(digits=(10, 2), string=u"СВ", compute='_standart')
	oe_s = fields.Float(digits=(10, 2), string=u"ОЭ", compute='_standart')
	sp_s = fields.Float(digits=(10, 2), string=u"СП", compute='_standart')
	pp_s = fields.Float(digits=(10, 2), string=u"ПП", compute='_standart')
	sk_s = fields.Float(digits=(10, 2), string=u"СК", compute='_standart')
	sj_s = fields.Float(digits=(10, 2), string=u"СЖ", compute='_standart')
	ca_s = fields.Float(digits=(10, 2), string=u"Ca", compute='_standart')
	p_s = fields.Float(digits=(10, 2), string=u"P", compute='_standart')
	sahar_s = fields.Float(digits=(10, 2), string=u"Сахар", compute='_standart')
	krahmal_s = fields.Float(digits=(10, 2), string=u"Крахмал", compute='_standart')
	bev_s = fields.Float(digits=(10, 2), string=u"БЭВ", compute='_standart')
	magniy_s = fields.Float(digits=(10, 2), string=u"Магний", compute='_standart')
	natriy_s = fields.Float(digits=(10, 2), string=u"Натрий", compute='_standart')
	kaliy_s = fields.Float(digits=(10, 2), string=u"Калий", compute='_standart')
	hlor_s = fields.Float(digits=(10, 2), string=u"Хлор", compute='_standart')
	sera_s = fields.Float(digits=(10, 2), string=u"Сера", compute='_standart')
	udp_s = fields.Float(digits=(10, 2), string=u"UDP", compute='_standart')
	me_s = fields.Float(digits=(10, 2), string=u"ME", compute='_standart')
	xp_s = fields.Float(digits=(10, 2), string=u"XP", compute='_standart')
	nrp_s = fields.Float(digits=(10, 2), string=u"НРП", compute='_standart')
	rnb_s = fields.Float(digits=(10, 2), string=u"RNB", compute='_standart')
	nrp_p_s = fields.Float(digits=(10, 2), string=u"%НРП", compute='_standart')



class korm_receptura(models.Model):
	_name = 'korm.receptura'
	_description = u'Рецептура комбикормов'
	_order = 'date desc, nomen_nomen_id'


	@api.one
	@api.depends('nomen_nomen_id')
	def return_name(self):
		self.name = self.nomen_nomen_id.name


	@api.model
	def create(self, vals):
		result = super(korm_receptura, self).create(vals)
		vals['korm_receptura_id'] = result.id
		self.env['korm.analiz_pit'].create(vals)
		return result

	@api.multi
	def write(self, vals):
		result = super(korm_receptura, self).write(vals)
		vals['korm_receptura_id'] = self.id
		analiz = self.env['korm.analiz_pit']
		poisk = analiz.search([('korm_receptura_id', '=', self.id)],limit=1)
		if len(poisk)>0:
			analiz.browse(poisk.id).write(vals)

		return result

	@api.depends('nomen_nomen_id')
	def _standart(self):
		for st in self:
			if st.nomen_nomen_id:
				standart = self.env['korm.pit_standart'].search([('nomen_nomen_id', '=', st.nomen_nomen_id.id)],limit=1)
				if len(standart)>0:
					st.ov_s=standart.ov
					st.sv_s=standart.sv
					st.oe_s=standart.oe
					st.sp_s=standart.sp
					st.pp_s=standart.pp
					st.sk_s=standart.sk
					st.sj_s=standart.sj
					st.ca_s=standart.ca
					st.p_s=standart.p
					st.sahar_s=standart.sahar
					st.krahmal_s=standart.krahmal
					st.bev_s=standart.bev
					st.magniy_s=standart.magniy
					st.natriy_s=standart.natriy
					st.kaliy_s=standart.kaliy
					st.hlor_s=standart.hlor
					st.sera_s=standart.sera
					st.udp_s=standart.udp
					st.me_s=standart.me
					st.xp_s=standart.xp
					st.nrp_s=standart.nrp
					st.rnb_s=standart.rnb
					st.nrp_p_s=standart.nrp_p

	@api.one
	@api.depends('korm_receptura_line.kol')
	def _raschet(self):

		self.amount=self.ov=self.sv = 0

		for line in self.korm_receptura_line:
			self.amount += line.kol
			for par in parametrs:
				self[par] += line.kol * line.korm_analiz_pit_id[par]
			
		if self.amount>0:
			
			for par in parametrs:
				self[par] = self[par]/self.amount

				
		if self.sv and self.nrp_p:
			self.nrp = self.sp * self.nrp_p/100.00
		
		if self.sv>0 and self.nrp:
			self.udp = self.nrp/self.sv

		if self.sv>0 and self.oe:
			self.me = self.oe/self.sv

		if self.sv>0 and self.sp:
			self.xp = self.sp/self.sv

		if self.xp!=0 and self.me and self.udp:
			self.rnb = (self.xp-((11.93-(6.82*(self.udp/self.xp)))*self.me+(1.03*self.udp)))/6.25


	@api.one
	def action_raschet(self):
		
		if self.amount>0:
			
			k = round(1000 / self.amount, 3)
		
			for line in self.korm_receptura_line:
				line.kol_tonna = k * line.kol
				line.procent = line.kol_tonna / 1000 * 100
				#print "ffffffffsssssssss========", r.kol_tonna


	name = fields.Char(string=u"Наименование", compute='return_name')
	nomen_nomen_id = fields.Many2one('nomen.nomen', string='Наименование', required=True)
	date = fields.Date(string='Дата', required=True, default=fields.Datetime.now)
	#korm_analiz_pit_id = fields.One2many('korm.analiz_pit', 'korm_receptura_id', string=u"Анализ кормов")
	korm_receptura_line = fields.One2many('korm.receptura_line', 'korm_receptura_id', string=u"Строка Рецептура комбикормов")
	amount = fields.Float(digits=(10, 3), string=u"Всего Кол-во", store=True, compute='_raschet')
	active = fields.Boolean(string=u"Используется", default=True)
	
	ov = fields.Float(digits=(10, 2), string=u"ОВ", store=True, compute='_raschet')
	sv = fields.Float(digits=(10, 2), string=u"СВ", store=True, compute='_raschet')
	oe = fields.Float(digits=(10, 2), string=u"ОЭ", store=True, compute='_raschet')
	sp = fields.Float(digits=(10, 2), string=u"СП", store=True, compute='_raschet')
	pp = fields.Float(digits=(10, 2), string=u"ПП", store=True, compute='_raschet')
	sk = fields.Float(digits=(10, 2), string=u"СК", store=True, compute='_raschet')
	sj = fields.Float(digits=(10, 2), string=u"СЖ", store=True, compute='_raschet')
	ca = fields.Float(digits=(10, 2), string=u"Ca", store=True, compute='_raschet')
	p = fields.Float(digits=(10, 2), string=u"P", store=True, compute='_raschet')
	sahar = fields.Float(digits=(10, 2), string=u"Сахар", store=True, compute='_raschet')
	krahmal = fields.Float(digits=(10, 2), string=u"Крахмал", store=True, compute='_raschet')
	bev = fields.Float(digits=(10, 2), string=u"БЭВ", store=True, compute='_raschet')
	magniy = fields.Float(digits=(10, 2), string=u"Магний", store=True, compute='_raschet')
	natriy = fields.Float(digits=(10, 2), string=u"Натрий", store=True, compute='_raschet')
	kaliy = fields.Float(digits=(10, 2), string=u"Калий", store=True, compute='_raschet')
	hlor = fields.Float(digits=(10, 2), string=u"Хлор", store=True, compute='_raschet')
	sera = fields.Float(digits=(10, 2), string=u"Сера", store=True, compute='_raschet')
	udp = fields.Float(digits=(10, 2), string=u"UDP", store=True, compute='_raschet')
	me = fields.Float(digits=(10, 2), string=u"ME", store=True, compute='_raschet')
	xp = fields.Float(digits=(10, 2), string=u"XP", store=True, compute='_raschet')
	nrp = fields.Float(digits=(10, 2), string=u"НРП", store=True, compute='_raschet')
	rnb = fields.Float(digits=(10, 2), string=u"RNB", store=True, compute='_raschet')
	nrp_p = fields.Float(digits=(10, 2), string=u"%НРП", store=True, compute='_raschet')
	#Параметры питательности по стандарту:
	ov_s = fields.Float(digits=(10, 2), string=u"ОВ", compute='_standart')
	sv_s = fields.Float(digits=(10, 2), string=u"СВ", compute='_standart')
	oe_s = fields.Float(digits=(10, 2), string=u"ОЭ", compute='_standart')
	sp_s = fields.Float(digits=(10, 2), string=u"СП", compute='_standart')
	pp_s = fields.Float(digits=(10, 2), string=u"ПП", compute='_standart')
	sk_s = fields.Float(digits=(10, 2), string=u"СК", compute='_standart')
	sj_s = fields.Float(digits=(10, 2), string=u"СЖ", compute='_standart')
	ca_s = fields.Float(digits=(10, 2), string=u"Ca", compute='_standart')
	p_s = fields.Float(digits=(10, 2), string=u"P", compute='_standart')
	sahar_s = fields.Float(digits=(10, 2), string=u"Сахар", compute='_standart')
	krahmal_s = fields.Float(digits=(10, 2), string=u"Крахмал", compute='_standart')
	bev_s = fields.Float(digits=(10, 2), string=u"БЭВ", compute='_standart')
	magniy_s = fields.Float(digits=(10, 2), string=u"Магний", compute='_standart')
	natriy_s = fields.Float(digits=(10, 2), string=u"Натрий", compute='_standart')
	kaliy_s = fields.Float(digits=(10, 2), string=u"Калий", compute='_standart')
	hlor_s = fields.Float(digits=(10, 2), string=u"Хлор", compute='_standart')
	sera_s = fields.Float(digits=(10, 2), string=u"Сера", compute='_standart')
	udp_s = fields.Float(digits=(10, 2), string=u"UDP", compute='_standart')
	me_s = fields.Float(digits=(10, 2), string=u"ME", compute='_standart')
	xp_s = fields.Float(digits=(10, 2), string=u"XP", compute='_standart')
	nrp_s = fields.Float(digits=(10, 2), string=u"НРП", compute='_standart')
	rnb_s = fields.Float(digits=(10, 2), string=u"RNB", compute='_standart')
	nrp_p_s = fields.Float(digits=(10, 2), string=u"%НРП", compute='_standart')


class korm_receptura_line(models.Model):
	_name = 'korm.receptura_line'
	_description = u'Строка Рецептура комбикормов'
	#_order = 'date desc, nomen_nomen_id'


	@api.one
	@api.depends('nomen_nomen_id')
	def return_name(self):
		self.name = self.nomen_nomen_id.name

	@api.one
	@api.depends('nomen_nomen_id')
	def _nomen(self):
		"""
		Compute the total amounts.
		"""
		  
		if self.nomen_nomen_id:
			analiz = self.env['korm.analiz_pit']
			analiz_id = analiz.search([('nomen_nomen_id', '=', self.nomen_nomen_id.id)], order="date desc",limit=1).id
			self.korm_analiz_pit_id = analiz_id

	#@api.onchange('kol')
	# @api.one
	# def _raschet_tonna(self):
	# 	self.kol_tonna = 100 * self.kol
		# amount = self.korm_receptura_id.amount
		# # for line in self:
		# # 	amount += line.kol
		# print "werwrwerwerwer========", amount
		# # for line in self:
		# if amount>0:
		# 	k = round(1000 / amount, 3)
		# 	self.kol_tonna = k * self.kol
		# 	self.procent = self.kol_tonna / 1000 * 100




	name = fields.Char(string=u"Наименование", compute='return_name')
	nomen_nomen_id = fields.Many2one('nomen.nomen', string='Наименование корма', required=True)
	korm_analiz_pit_id = fields.Many2one('korm.analiz_pit', string='Анализ корма', store=True, compute='_nomen')
	korm_receptura_id = fields.Many2one('korm.receptura', ondelete='cascade', string=u"Рецептура комбикормов", required=True)
	ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", related='nomen_nomen_id.ed_izm_id', readonly=True,  store=True)
	kol = fields.Float(digits=(10, 3), string=u"Кол-во", required=True)
	kol_tonna = fields.Float(digits=(10, 3), string=u"Кол-во на тонну", store=True, readonly=True)
	procent = fields.Float(digits=(10, 1), string=u"%", store=True, readonly=True)




class korm_norm(models.Model):
	_name = 'korm.norm'
	_description = u'Нормы кормления'
	_order = 'date desc, stado_fiz_group_id'



	@api.one
	@api.depends('stado_fiz_group_id')
	def return_name(self):
		self.name = self.stado_fiz_group_id.name + u" от " + self.date


	@api.one
	@api.depends('sv_min', 'oe_min', 'sv_min', 'nrp_p_min','sv_max', 'oe_max', 'sv_max', 'nrp_p_max')
	def _raschet(self):
		
		#MIN
		if self.sv_min and self.nrp_p_min:
			self.nrp_min = self.sp_min * self.nrp_p_min/100.00
		
		if self.sv_min>0 and self.nrp_min:
			self.udp_min = self.nrp_min/self.sv_min

		if self.sv_min>0 and self.oe_min:
			self.me_min = self.oe_min/self.sv_min

		if self.sv_min>0 and self.sp_min:
			self.xp_min = self.sp_min/self.sv_min

		if self.xp_min!=0 and self.me_min and self.udp_min:
			self.rnb_min = (self.xp_min-((11.93-(6.82*(self.udp_min/self.xp_min)))*self.me_min+(1.03*self.udp_min)))/6.25

		#MAX
		if self.sv_max and self.nrp_p_max:
			self.nrp_max = self.sp_max * self.nrp_p_max/100.00
		
		if self.sv_max>0 and self.nrp_max:
			self.udp_max = self.nrp_max/self.sv_max

		if self.sv_max>0 and self.oe_max:
			self.me_max = self.oe_max/self.sv_max

		if self.sv_max>0 and self.sp_max:
			self.xp_max = self.sp_max/self.sv_max

		if self.xp_max!=0 and self.me_max and self.udp_max:
			self.rnb_max = (self.xp_max-((11.93-(6.82*(self.udp_max/self.xp_max)))*self.me_max+(1.03*self.udp_max)))/6.25

	


	name = fields.Char(string=u"Наименование", compute='return_name')
	stado_fiz_group_id = fields.Many2one('stado.fiz_group', string='Физиологическая группа', required=True)
	date = fields.Date(string='Дата', required=True, default=fields.Datetime.now)
	
	ov_min = fields.Float(digits=(10, 2), string=u"ОВ")
	sv_min = fields.Float(digits=(10, 2), string=u"СВ")
	oe_min = fields.Float(digits=(10, 2), string=u"ОЭ")
	sp_min = fields.Float(digits=(10, 2), string=u"СП")
	pp_min = fields.Float(digits=(10, 2), string=u"ПП")
	sk_min = fields.Float(digits=(10, 2), string=u"СК")
	sj_min = fields.Float(digits=(10, 2), string=u"СЖ")
	ca_min = fields.Float(digits=(10, 2), string=u"Ca")
	p_min = fields.Float(digits=(10, 2), string=u"P")
	sahar_min = fields.Float(digits=(10, 2), string=u"Сахар")
	krahmal_min = fields.Float(digits=(10, 2), string=u"Крахмал")
	bev_min = fields.Float(digits=(10, 2), string=u"БЭВ")
	magniy_min = fields.Float(digits=(10, 2), string=u"Магний")
	natriy_min = fields.Float(digits=(10, 2), string=u"Натрий")
	kaliy_min = fields.Float(digits=(10, 2), string=u"Калий")
	hlor_min = fields.Float(digits=(10, 2), string=u"Хлор")
	sera_min = fields.Float(digits=(10, 2), string=u"Сера")
	udp_min = fields.Float(digits=(10, 2), string=u"UDP", store=True, compute='_raschet')
	me_min = fields.Float(digits=(10, 2), string=u"ME", store=True, compute='_raschet')
	xp_min = fields.Float(digits=(10, 2), string=u"XP", store=True, compute='_raschet')
	nrp_min = fields.Float(digits=(10, 2), string=u"НРП", store=True, compute='_raschet')
	rnb_min = fields.Float(digits=(10, 2), string=u"RNB", store=True, compute='_raschet')
	nrp_p_min = fields.Float(digits=(10, 2), string=u"%НРП")
	

	ov_max = fields.Float(digits=(10, 2), string=u"ОВ")
	sv_max = fields.Float(digits=(10, 2), string=u"СВ")
	oe_max = fields.Float(digits=(10, 2), string=u"ОЭ")
	sp_max = fields.Float(digits=(10, 2), string=u"СП")
	pp_max = fields.Float(digits=(10, 2), string=u"ПП")
	sk_max = fields.Float(digits=(10, 2), string=u"СК")
	sj_max = fields.Float(digits=(10, 2), string=u"СЖ")
	ca_max = fields.Float(digits=(10, 2), string=u"Ca")
	p_max = fields.Float(digits=(10, 2), string=u"P")
	sahar_max = fields.Float(digits=(10, 2), string=u"Сахар")
	krahmal_max = fields.Float(digits=(10, 2), string=u"Крахмал")
	bev_max = fields.Float(digits=(10, 2), string=u"БЭВ")
	magniy_max = fields.Float(digits=(10, 2), string=u"Магний")
	natriy_max = fields.Float(digits=(10, 2), string=u"Натрий")
	kaliy_max = fields.Float(digits=(10, 2), string=u"Калий")
	hlor_max = fields.Float(digits=(10, 2), string=u"Хлор")
	sera_max = fields.Float(digits=(10, 2), string=u"Сера")
	udp_max = fields.Float(digits=(10, 2), string=u"UDP", store=True, compute='_raschet')
	me_max = fields.Float(digits=(10, 2), string=u"ME", store=True, compute='_raschet')
	xp_max = fields.Float(digits=(10, 2), string=u"XP", store=True, compute='_raschet')
	nrp_max = fields.Float(digits=(10, 2), string=u"НРП", store=True, compute='_raschet')
	rnb_max = fields.Float(digits=(10, 2), string=u"RNB", store=True, compute='_raschet')
	nrp_p_max = fields.Float(digits=(10, 2), string=u"%НРП")




class korm_racion(models.Model):
	_name = 'korm.racion'
	_description = u'Рацион кормления'
	_order = 'date desc, stado_fiz_group_id'


	@api.one
	@api.depends('stado_fiz_group_id')
	def return_name(self):
		self.name = self.stado_fiz_group_id.name + u' от ' + self.date


 
	@api.depends('stado_fiz_group_id')
	def _norm(self):
		for st in self:
			if st.stado_fiz_group_id:
				standart = self.env['korm.norm'].search([('stado_fiz_group_id', '=', st.stado_fiz_group_id.id)],limit=1)
				if len(standart)>0:
					for par in parametrs:
						self[par+'_min'] = standart[par+'_min']
						self[par+'_max'] = standart[par+'_max']



	@api.one
	@api.depends('korm_racion_line.kol')
	def _raschet(self):

		self.amount=self.ov=self.sv = 0

		for line in self.korm_racion_line:
			self.amount += line.kol
			for par in parametrs:
				self[par] += line.kol * line.korm_analiz_pit_id[par]
			
		if self.amount>0:
			for par in parametrs:
				self[par] = self[par]/self.amount

				
		if self.sv and self.nrp_p:
			self.nrp = self.sp * self.nrp_p/100.00
		
		if self.sv>0 and self.nrp:
			self.udp = self.nrp/self.sv

		if self.sv>0 and self.oe:
			self.me = self.oe/self.sv

		if self.sv>0 and self.sp:
			self.xp = self.sp/self.sv

		if self.xp!=0 and self.me and self.udp:
			self.rnb = (self.xp-((11.93-(6.82*(self.udp/self.xp)))*self.me+(1.03*self.udp)))/6.25

		self.kol = self.amount = 0.00
		for line in self.korm_racion_line:
			self.kol += line.kol
			self.amount += line.amount

		if self.kol>0:
			self.price = self.amount/self.kol

				

	name = fields.Char(string=u"Наименование", compute='return_name')
	stado_fiz_group_id = fields.Many2one('stado.fiz_group', string='Физиологическая группа', required=True)
	date = fields.Date(string='Дата', required=True, default=fields.Datetime.now)
	korm_racion_line = fields.One2many('korm.racion_line', 'korm_racion_id', string=u"Строка Рацион кормления")
	kol = fields.Float(digits=(10, 3), string=u"Всего Кол-во", store=True, compute='_raschet')
	amount = fields.Float(digits=(10, 2), string=u"Всего стоимость", store=True, compute='_raschet')
	price = fields.Float(digits=(10, 2), string=u"Стоимость еденицы", store=True, compute='_raschet')
	milk = fields.Float(digits=(10, 1), string=u"Молоко, кг", store=True)
	jir = fields.Float(digits=(10, 2), string=u"Жир, %", store=True)
	belok = fields.Float(digits=(10, 2), string=u"Белок, %", store=True)
	massa = fields.Integer(string=u"Живая масса, кг", store=True)

	ov = fields.Float(digits=(10, 2), string=u"ОВ", store=True, compute='_raschet')
	sv = fields.Float(digits=(10, 2), string=u"СВ", store=True, compute='_raschet')
	oe = fields.Float(digits=(10, 2), string=u"ОЭ", store=True, compute='_raschet')
	sp = fields.Float(digits=(10, 2), string=u"СП", store=True, compute='_raschet')
	pp = fields.Float(digits=(10, 2), string=u"ПП", store=True, compute='_raschet')
	sk = fields.Float(digits=(10, 2), string=u"СК", store=True, compute='_raschet')
	sj = fields.Float(digits=(10, 2), string=u"СЖ", store=True, compute='_raschet')
	ca = fields.Float(digits=(10, 2), string=u"Ca", store=True, compute='_raschet')
	p = fields.Float(digits=(10, 2), string=u"P", store=True, compute='_raschet')
	sahar = fields.Float(digits=(10, 2), string=u"Сахар", store=True, compute='_raschet')
	krahmal = fields.Float(digits=(10, 2), string=u"Крахмал", store=True, compute='_raschet')
	bev = fields.Float(digits=(10, 2), string=u"БЭВ", store=True, compute='_raschet')
	magniy = fields.Float(digits=(10, 2), string=u"Магний", store=True, compute='_raschet')
	natriy = fields.Float(digits=(10, 2), string=u"Натрий", store=True, compute='_raschet')
	kaliy = fields.Float(digits=(10, 2), string=u"Калий", store=True, compute='_raschet')
	hlor = fields.Float(digits=(10, 2), string=u"Хлор", store=True, compute='_raschet')
	sera = fields.Float(digits=(10, 2), string=u"Сера", store=True, compute='_raschet')
	udp = fields.Float(digits=(10, 2), string=u"UDP", store=True, compute='_raschet')
	me = fields.Float(digits=(10, 2), string=u"ME", store=True, compute='_raschet')
	xp = fields.Float(digits=(10, 2), string=u"XP", store=True, compute='_raschet')
	nrp = fields.Float(digits=(10, 2), string=u"НРП", store=True, compute='_raschet')
	rnb = fields.Float(digits=(10, 2), string=u"RNB", store=True, compute='_raschet')
	nrp_p = fields.Float(digits=(10, 2), string=u"%НРП", store=True, compute='_raschet')
	
	#Параметры питательности по норме:
	ov_min = fields.Float(digits=(10, 2), string=u"ОВ", compute='_norm')
	sv_min = fields.Float(digits=(10, 2), string=u"СВ", compute='_norm')
	oe_min = fields.Float(digits=(10, 2), string=u"ОЭ", compute='_norm')
	sp_min = fields.Float(digits=(10, 2), string=u"СП", compute='_norm')
	pp_min = fields.Float(digits=(10, 2), string=u"ПП", compute='_norm')
	sk_min = fields.Float(digits=(10, 2), string=u"СК", compute='_norm')
	sj_min = fields.Float(digits=(10, 2), string=u"СЖ", compute='_norm')
	ca_min = fields.Float(digits=(10, 2), string=u"Ca", compute='_norm')
	p_min = fields.Float(digits=(10, 2), string=u"P", compute='_norm')
	sahar_min = fields.Float(digits=(10, 2), string=u"Сахар", compute='_norm')
	krahmal_min = fields.Float(digits=(10, 2), string=u"Крахмал", compute='_norm')
	bev_min = fields.Float(digits=(10, 2), string=u"БЭВ", compute='_norm')
	magniy_min = fields.Float(digits=(10, 2), string=u"Магний", compute='_norm')
	natriy_min = fields.Float(digits=(10, 2), string=u"Натрий", compute='_norm')
	kaliy_min = fields.Float(digits=(10, 2), string=u"Калий", compute='_norm')
	hlor_min = fields.Float(digits=(10, 2), string=u"Хлор", compute='_norm')
	sera_min = fields.Float(digits=(10, 2), string=u"Сера", compute='_norm')
	udp_min = fields.Float(digits=(10, 2), string=u"UDP", compute='_norm')
	me_min = fields.Float(digits=(10, 2), string=u"ME", compute='_norm')
	xp_min = fields.Float(digits=(10, 2), string=u"XP", compute='_norm')
	nrp_min = fields.Float(digits=(10, 2), string=u"НРП", compute='_norm')
	rnb_min = fields.Float(digits=(10, 2), string=u"RNB", compute='_norm')
	nrp_p_min = fields.Float(digits=(10, 2), string=u"%НРП", compute='_norm')

	ov_max = fields.Float(digits=(10, 2), string=u"ОВ", compute='_norm')
	sv_max = fields.Float(digits=(10, 2), string=u"СВ", compute='_norm')
	oe_max = fields.Float(digits=(10, 2), string=u"ОЭ", compute='_norm')
	sp_max = fields.Float(digits=(10, 2), string=u"СП", compute='_norm')
	pp_max = fields.Float(digits=(10, 2), string=u"ПП", compute='_norm')
	sk_max = fields.Float(digits=(10, 2), string=u"СК", compute='_norm')
	sj_max = fields.Float(digits=(10, 2), string=u"СЖ", compute='_norm')
	ca_max = fields.Float(digits=(10, 2), string=u"Ca", compute='_norm')
	p_max = fields.Float(digits=(10, 2), string=u"P", compute='_norm')
	sahar_max = fields.Float(digits=(10, 2), string=u"Сахар", compute='_norm')
	krahmal_max = fields.Float(digits=(10, 2), string=u"Крахмал", compute='_norm')
	bev_max = fields.Float(digits=(10, 2), string=u"БЭВ", compute='_norm')
	magniy_max = fields.Float(digits=(10, 2), string=u"Магний", compute='_norm')
	natriy_max = fields.Float(digits=(10, 2), string=u"Натрий", compute='_norm')
	kaliy_max = fields.Float(digits=(10, 2), string=u"Калий", compute='_norm')
	hlor_max = fields.Float(digits=(10, 2), string=u"Хлор", compute='_norm')
	sera_max = fields.Float(digits=(10, 2), string=u"Сера", compute='_norm')
	udp_max = fields.Float(digits=(10, 2), string=u"UDP", compute='_norm')
	me_max = fields.Float(digits=(10, 2), string=u"ME", compute='_norm')
	xp_max = fields.Float(digits=(10, 2), string=u"XP", compute='_norm')
	nrp_max = fields.Float(digits=(10, 2), string=u"НРП", compute='_norm')
	rnb_max = fields.Float(digits=(10, 2), string=u"RNB", compute='_norm')
	nrp_p_max = fields.Float(digits=(10, 2), string=u"%НРП", compute='_norm')



class korm_racion_line(models.Model):
	_name = 'korm.racion_line'
	_description = u'Строка Рацион кормления'
	#_order = 'date desc, nomen_nomen_id'


	@api.one
	@api.depends('nomen_nomen_id')
	def return_name(self):
		self.name = self.nomen_nomen_id.name

	@api.one
	@api.depends('nomen_nomen_id')
	def _nomen(self):
		
		if self.nomen_nomen_id:
			analiz = self.env['korm.analiz_pit']
			analiz_id = analiz.search([('nomen_nomen_id', '=', self.nomen_nomen_id.id), ('date', '<=', self.korm_racion_id.date)], order="date desc",limit=1).id
			self.korm_analiz_pit_id = analiz_id

			obj_price = self.env['nomen.price_line']
			price = obj_price.search([('nomen_nomen_id', '=', self.nomen_nomen_id.id), ('date', '<=', self.korm_racion_id.date)], order="date desc",limit=1).price
			self.price = price

			self.amount = self.price * self.kol

	@api.one
	@api.depends('kol')
	def _amount(self):
		self.amount = self.price * self.kol           



	name = fields.Char(string=u"Наименование", compute='return_name')
	nomen_nomen_id = fields.Many2one('nomen.nomen', string=u'Наименование корма', required=True)
	korm_analiz_pit_id = fields.Many2one('korm.analiz_pit', string=u'Анализ корма', store=True, compute='_nomen')
	korm_racion_id = fields.Many2one('korm.racion', ondelete='cascade', string=u"Рацион кормления", required=True)
	ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", related='nomen_nomen_id.ed_izm_id', readonly=True,  store=True)
	kol = fields.Float(digits=(10, 3), string=u"Кол-во", required=True)
	price = fields.Float(digits=(10, 2), string=u"Цена", compute='_nomen',  store=True)
	amount = fields.Float(digits=(10, 2), string=u"Сумма", compute='_amount',  store=True)
   


class korm_korm(models.Model):
	_name = 'korm.korm'
	_description = u'Кормление'
	_order = 'date desc'

	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New' or vals.get('name', 'New') == None:
			vals['name'] = self.env['ir.sequence'].next_by_code('korm.korm') or 'New'

		result = super(korm_korm, self).create(vals)
		return result
	
	name = fields.Char(string='Номер', required=True, copy=False, readonly=True, index=True, default='New')
	date = fields.Date(string='Дата', required=True, copy=False, default=fields.Datetime.now)
	korm_korm_line = fields.One2many('korm.korm_line', 'korm_korm_id', string=u"Строка Кормление", copy=True)
	korm_korm_svod_line = fields.One2many('korm.korm_svod_line', 'korm_korm_id', string=u"Строка Свода Кормление")
	korm_korm_detail_line = fields.One2many('korm.korm_detail_line', 'korm_korm_id', string=u"Детальные строки Кормления")
	
	transport_id = fields.Many2one('milk.transport', string=u'Транспорт', required=True)   
	voditel_id = fields.Many2one('res.partner', string='Водитель', required=True)
	sostavil_id = fields.Many2one('res.partner', string='Составил')
	utverdil_id = fields.Many2one('res.partner', string='Утвердил')
	is_vremya_dnya = fields.Boolean(string=u"Разд-ть корм на Ут/Веч", default=False)
	vremya_dnya = fields.Selection([
		(u'Утро', "Утро"),
		(u'Вечер', "Вечер"),
	], default=u'Утро', string="Время дня")
	kol_golov = fields.Integer(string=u"Кол-во голов для расчета", store=True, readonly=True, copy=True)
	kol_golov_zagon = fields.Integer(string=u"Кол-во голов по загонам", readonly=True, store=True, copy=True)
	description = fields.Text(string=u"Коментарии")

		


	@api.one
	def action_raschet(self):
		svod_line = self.env['korm.korm_svod_line']
		del_line = svod_line.search([('korm_korm_id',	'=',	self.id)])
		del_line.unlink()

		detail_line = self.env['korm.korm_detail_line']
		del_line = detail_line.search([('korm_korm_id',	'=',	self.id)])
		del_line.unlink()

		sorted=''
		kol_golov=kol_golov_zagon=kol_korma=racion_id=self.kol_golov_zagon=self.kol_golov=0
		d = []
		for line in self.korm_korm_line:
			line.kol_golov = line.kol_golov_zagon * line.procent_dachi/100
			d.append([line.id, line.sorting, line.korm_racion_id, line.kol_golov, 
						line.kol_korma, line.procent_dachi, line.kol_golov_zagon, line.procent_raciona])
			#kol_golov_detail = line.kol_golov*line.procent_dachi/100  --- Получаем кол-во голов для расчета дачи корма Утром и Вечером
			self.kol_golov_zagon += line.kol_golov_zagon
			self.kol_golov += line.kol_golov

		print d
					
		from itertools import groupby
		for g in groupby( d,key=lambda x:x[1]):
			sorting = g[0]
			print g[0]
			kol_golov=kol_golov_zagon=kol_korma=kol_golov_detail=racion_id=sum_procent_raciona=0
			t = 0
			for i in g[1]:
				t +=1
				print ' - ',i
				kol_golov += i[3]
				kol_korma += i[4]
				kol_golov_zagon += i[6]
				sum_procent_raciona += i[7] 
				

				if racion_id !=0 and racion_id != i[2]:
					#print "111EEEEEEEEEEEEEEEEEERRRRRRRRRRRRRRRRRRRRRRRRRR"

					raise exceptions.ValidationError(_(u"Для Порядка кормления №%s не соответствуют рационы!" % (i[1])))
					#print "222EEEEEEEEEEEEEEEEEERRRRRRRRRRRRRRRRRRRRRRRRRR"
				racion_id = i[2]

			procent_raciona = sum_procent_raciona/t
			svod_line.create({'korm_korm_id':	self.id,
								'name':	racion_id.stado_fiz_group_id.name,
								'sorting':	sorting,
								'korm_racion_id':	racion_id.id,
								'kol_golov':	kol_golov,
								'kol_golov_zagon':	kol_golov_zagon,
								'kol_korma':	kol_korma,
								})
			#racion_line = self.env['korm.racion_line']
			#search_racion_line = racion_line.search([('korm_racion_id',	'=',	i[2])])
			for rl in racion_id.korm_racion_line:

				detail_line.create({'korm_korm_id':	self.id,
									'name':	rl.nomen_nomen_id.name,
									'sorting':	i[1],
									'nomen_nomen_id':	rl.nomen_nomen_id.id,
									'kol_norma':	rl.kol * kol_golov * procent_raciona/100,
									})






class korm_korm_line(models.Model):
	_name = 'korm.korm_line'
	_description = u'Строка Кормление'
	_order = 'sorting'


	@api.one
	@api.depends('stado_zagon_id')
	def return_name(self):
		self.name = self.stado_zagon_id.nomer

		self.stado_fiz_group_id = self.stado_zagon_id.stado_fiz_group_id
		racion = self.env['korm.racion']
		racion_id = racion.search([('stado_fiz_group_id', '=', self.stado_fiz_group_id.id), ('date', '<=', self.korm_korm_id.date)], order="date desc",limit=1).id
		self.korm_racion_id = racion_id
		if self.korm_korm_id.is_vremya_dnya == False:
			self.procent_dachi = 100
		else:
			if self.korm_korm_id.vremya_dnya == u'Утро':
				self.procent_dachi = self.stado_zagon_id.utro
			else:
				self.procent_dachi = self.stado_zagon_id.vecher
		
		self.kol_golov = self.kol_golov_zagon = 0

	@api.one
	@api.depends('kol_golov_zagon', 'procent_raciona')
	def _raschet(self):
		self.kol_korma=self.kol_zamesov=self.kol_korma_zames=0
		self.kol_golov = self.kol_golov_zagon * self.procent_dachi/100
		if self.kol_golov>0 and self.korm_racion_id!=False:
			self.kol_korma = self.korm_racion_id.kol * self.kol_golov * self.procent_raciona/100
			# max_value = self.korm_korm_id.transport_id.max_value
			# if self.kol_korma>max_value and max_value>0:
			# 	self.kol_zamesov = math.ceil(self.kol_korma / max_value)
			# 	self.kol_korma_zames = self.kol_korma / self.kol_zamesov
			# else:
			# 	self.kol_zamesov = 1
			# 	self.kol_korma_zames = self.kol_korma

	@api.one
	@api.depends('korm_korm_id.date')
	def return_date(self):
		self.date = self.korm_korm_id.date

	date = fields.Date(string='Дата', store=True, compute='return_date')

	name = fields.Char(string=u"Наименование", compute='return_name')
	korm_korm_id = fields.Many2one('korm.korm', ondelete='cascade', string=u"Кормление", required=True)
	
	sorting = fields.Integer(string=u"Порядок", required=True)
	stado_zagon_id = fields.Many2one('stado.zagon', string=u'Загон', required=True)
	stado_fiz_group_id = fields.Many2one('stado.fiz_group', string=u'Физиологическая группа', store=True, compute='return_name')
	korm_racion_id = fields.Many2one('korm.racion', string=u'Рацион кормления', store=True, compute='return_name')
	kol_golov = fields.Integer(string=u"Кол-во голов для расчета", compute='_raschet', store=True)
	kol_golov_zagon = fields.Integer(string=u"Кол-во голов в загоне", required=True, store=True)
	procent_dachi = fields.Integer(string=u"% дачи", store=True, compute='return_name')
	procent_raciona = fields.Integer(string=u"% дачи рациона", store=True, default=100)
	kol_korma = fields.Float(digits=(10, 3), string=u"Кол-во корма", copy=False, compute='_raschet')
	# kol_zamesov = fields.Integer( string=u"Кол-во замесов", copy=False, compute='_raschet')
	# kol_korma_zames = fields.Float(digits=(10, 3), string=u"Вес замеса", copy=False, compute='_raschet')
	# kol_ostatok = fields.Float(digits=(10, 3), string=u"Кол-во остаток корма", copy=False)
	date_obedkov = fields.Date(string='Дата объедков')
	
	description = fields.Text(string=u"Коментарии")
	

class korm_korm_svod_line(models.Model):
	_name = 'korm.korm_svod_line'
	_description = u'Строка Свода Кормление'
	_order = 'sorting'

	@api.multi
	def _raschet(self):
		for line in self:
			line.kol_zamesov=line.kol_korma_zames=0
			if line.kol_golov>0 and line.korm_racion_id!=False:
				max_value = line.korm_korm_id.transport_id.max_value
				if line.kol_korma>max_value and max_value>0:
					line.kol_zamesov = math.ceil(line.kol_korma / max_value)
					line.kol_korma_zames = line.kol_korma / line.kol_zamesov
					line.kol_golov_zames = line.kol_golov / line.kol_zamesov    
				else:
					line.kol_zamesov = 1
					line.kol_korma_zames = line.kol_korma	
					line.kol_golov_zames = line.kol_golov    

	@api.one
	@api.depends('korm_korm_id.date')
	def return_date(self):
		self.date = self.korm_korm_id.date


	name = fields.Char(string=u"Наименование", compute='return_name')
	korm_korm_id = fields.Many2one('korm.korm', ondelete='cascade', string=u"Кормление", required=True)
	
	date = fields.Date(string='Дата', store=True, compute='return_date')
	sorting = fields.Integer(string=u"Порядок", required=True, readonly=True)
	korm_racion_id = fields.Many2one('korm.racion', string=u'Рацион кормления', store=True, compute='return_name', readonly=True)
	kol_golov = fields.Integer(string=u"Кол-во голов для расчета", required=True, readonly=True)
	kol_golov_zagon = fields.Integer(string=u"Кол-во голов в загоне", required=True, readonly=True)
	kol_golov_zames = fields.Integer(string=u"Кол-во голов для 1-го замеса", required=True, compute='_raschet', readonly=True)
	kol_korma = fields.Float(digits=(10, 3), string=u"Кол-во корма", copy=False, readonly=True)
	kol_zamesov = fields.Integer( string=u"Кол-во замесов", copy=False, compute='_raschet', readonly=True)
	kol_korma_zames = fields.Float(digits=(10, 3), string=u"Вес замеса", copy=False, compute='_raschet', readonly=True)
	# kol_ostatok = fields.Float(digits=(10, 3), string=u"Кол-во остаток корма", copy=False)
	# date_obedkov = fields.Date(string='Дата объедков')
	
	description = fields.Text(string=u"Коментарии")



class korm_korm_detail_line(models.Model):
	_name = 'korm.korm_detail_line'
	_description = u'Детальные строки Кормления'
	#_order = 'date desc, nomen_nomen_id'


	@api.one
	@api.depends('nomen_nomen_id')
	def return_name(self):
		self.name = self.nomen_nomen_id.name

	@api.one
	@api.depends('nomen_nomen_id')
	def _nomen(self):
		
		if self.nomen_nomen_id:
			analiz = self.env['korm.analiz_pit']
			analiz_id = analiz.search([('nomen_nomen_id', '=', self.nomen_nomen_id.id), ('date', '<=', self.korm_racion_id.date)], order="date desc",limit=1).id
			self.korm_analiz_pit_id = analiz_id

			obj_price = self.env['nomen.price_line']
			price = obj_price.search([('nomen_nomen_id', '=', self.nomen_nomen_id.id), ('date', '<=', self.korm_racion_id.date)], order="date desc",limit=1).price
			self.price = price

			self.amount = self.price * self.kol

	@api.one
	@api.depends('kol')
	def _amount(self):
		self.amount = self.price * self.kol 

	
	def raschet_formuli(self, cr, uid, ids, formula, context=None):
		try:
			if formula==False:
				return False

			formula=formula.replace(',','.')

			zn = formula.split('+')
			ss=[]
			for l in zn:
				ss.append(float(l))

			total = sum(ss)
			res = {
					'value': {
							'kol_fakt': total
							}
				} 
			return res
		except Exception as exc:
			raise exceptions.ValidationError(_(u"Ошибка в формуле! Поле Формула должно быть вида: 25.56+45.589. Ошибка:%s" % (exc)))
	   


	raschet_formuli
	
	@api.one
	@api.depends('korm_korm_id.date')
	def return_date(self):
		self.date = self.korm_korm_id.date


	name = fields.Char(string=u"Наименование", compute='return_name')
	korm_korm_id = fields.Many2one('korm.korm', ondelete='cascade', string=u"Кормление", required=True)
	
	date = fields.Date(string='Дата', store=True, compute='return_date')
	sorting = fields.Integer(string=u"Порядок", required=True, readonly=True)
	nomen_nomen_id = fields.Many2one('nomen.nomen', string=u'Наименование корма', required=True, readonly=True)
	ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", related='nomen_nomen_id.ed_izm_id', readonly=True,  store=True)
	kol_norma = fields.Float(digits=(10, 3), string=u"Кол-во по норме", readonly=True)
	kol_fakt = fields.Float(digits=(10, 3), string=u"Кол-во по факту")
	formula = fields.Char(string=u"Формула сложения")
	description = fields.Text(string=u"Коментарии")






class korm_korm_ostatok(models.Model):
	_name = 'korm.korm_ostatok'
	_description = u'Остатки кормления'
	_order = 'date desc'

	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New' or vals.get('name', 'New') == None:
			vals['name'] = self.env['ir.sequence'].next_by_code('korm.korm_ostatok') or 'New'

		result = super(korm_korm_ostatok, self).create(vals)
		return result

	@api.one
	def action_raschet(self):
		line = self.env['korm.korm_ostatok_line']
		del_line = line.search([('korm_korm_ostatok_id', '=',    self.id)])
		del_line.unlink()

		# svod_line = self.env['korm.korm_ostatok_svod_line']
		# del_line = svod_line.search([('korm_korm_ostatok_id',   '=',    self.id)])
		# del_line.unlink()

		korm_korm = self.env['korm.korm']
		korm_korm_ids = korm_korm.search([('date', '=', self.date)],)
		from itertools import groupby #Преобразует список в иерархический по группировке сортинг
		d = []
		for korm_korm_id in korm_korm_ids:
			korm_korm_line = self.env['korm.korm_line']
			korm_korm_line_ids = korm_korm_line.search([('korm_korm_id', '=', korm_korm_id.id)],)
			for korm_line in korm_korm_line_ids:
				# line.create({'korm_korm_ostatok_id':   self.id,
				# 				'name': self.name,
				# 				'stado_zagon_id':  korm_line.stado_zagon_id.id,
				# 				'stado_fiz_group_id':   korm_line.stado_fiz_group_id.id,
				# 				})
				d.append([  korm_line.id, 
							korm_line.sorting, 
							korm_line.stado_fiz_group_id, 
							korm_line.stado_zagon_id.id, 
							korm_line.kol_golov_zagon,
							korm_line.stado_zagon_id.nomer,
							korm_korm_id.id,
							korm_line.kol_korma,
							korm_line.kol_golov,
							])

		#Заполняем по загонам
		d.sort(key=lambda nomer: nomer[5])
		for g in groupby( d,key=lambda zagon:zagon[3]):
			print "zzz",g[0]
			stado_zagon_id = g[0]
			kol_golov=kol_korma=racion_id=sum_kol_golov_zagon=kol_golov_zagon=0
			kol_korma_fakt=kol_korma_norma=0
			stado_zagon_ids = []
			k=0
			for i in g[1]:
				print "kol",i[4]
				k +=1
				sorting = i[1]
				korm_korm_id = i[6]
				stado_zagon_ids.append(i[3])
				stado_fiz_group_id = i[2]
				sum_kol_golov_zagon += i[4]
				kol_golov_zagon = i[4]
				kol_golov = i[8]
				kol_korma_norma += i[7]

				korm_korm_detail_line = self.env['korm.korm_detail_line']
				korm_korm_detail_line_ids = korm_korm_detail_line.search([('korm_korm_id', '=', korm_korm_id), 
																			('sorting', '=', sorting)],)
				sum_kol_korma_fakt=sum_kol_korma_norma=0
				
				for korm_detail_line in korm_korm_detail_line_ids:
					sum_kol_korma_fakt += korm_detail_line.kol_fakt
					#sum_kol_korma_norma += korm_detail_line.kol_norma
				print 'sum_kol_korma_fakt=',sum_kol_korma_fakt
				korm_korm_svod_line = self.env['korm.korm_svod_line']
				korm_korm_svod_line_id = korm_korm_svod_line.search([('korm_korm_id', '=', korm_korm_id), 
																			('sorting', '=', sorting)],limit=1)
				if korm_korm_svod_line_id.kol_golov>0:
					kol_korma_fakt += sum_kol_korma_fakt * kol_golov / korm_korm_svod_line_id.kol_golov
					#kol_korma_norma += korm_korm_svod_line_id.kol_korma * kol_golov_zagon / korm_korm_svod_line_id.kol_golov_zagon

			if k>0: sr_kol_golov_zagon = sum_kol_golov_zagon/k
			#print stado_zagon_ids

			#Находим предыдущий документ и смотрим какой там был остаток
			korm_ostatok = self.env['korm.korm_ostatok']
			prev_korm_ostatok_id = korm_ostatok.search([('date', '<', self.date)], order="date desc",limit=1).id

			procent_ostatkov_prev = line.search([('korm_korm_ostatok_id', '=', prev_korm_ostatok_id), 
													  ('stado_zagon_id', '=', stado_zagon_id)],limit=1).procent_ostatkov

			line.create({'korm_korm_ostatok_id':   self.id,
								'name': self.name,
								'stado_zagon_id':   stado_zagon_id,
								'stado_fiz_group_id':    stado_fiz_group_id.id,
								'kol_golov_zagon':    sr_kol_golov_zagon,
								'kol_korma_fakt':    kol_korma_fakt,
								'kol_korma_norma':    kol_korma_norma,
								'kol_korma_otk':    kol_korma_fakt-kol_korma_norma,
								'procent_ostatkov_prev':    procent_ostatkov_prev,
								})

		
		#Конец цикла по загонам

		for svod_line in self.korm_korm_ostatok_svod_line:
			kol_golov_zagon=0
			for stado_zagon_id in svod_line.stado_zagon_id:
				for line in self.korm_korm_ostatok_line:
					if stado_zagon_id == line.stado_zagon_id:
						kol_golov_zagon += line.kol_golov_zagon
						#print 'kol_golov_zagon=',line.kol_golov_zagon
			svod_line.kol_golov_zagon = kol_golov_zagon

		for svod_line in self.korm_korm_ostatok_svod_line:
			for stado_zagon_id in svod_line.stado_zagon_id:
				for line in self.korm_korm_ostatok_line:
					if stado_zagon_id == line.stado_zagon_id:
						if svod_line.kol_golov_zagon>0:
							line.kol_ostatok = svod_line.kol_ostatok * line.kol_golov_zagon / svod_line.kol_golov_zagon
						if line.kol_korma_fakt>0:
							line.procent_ostatkov = round(line.kol_ostatok / line.kol_korma_fakt, 3) * 100
							#print 'line.kol_ostatok=',line.kol_ostatok
							#print 'line.kol_korma_fakt=',line.kol_korma_fakt
							#print 'line.procent_ostatkov=',line.procent_ostatkov
			#Заполняем сводные данные
								  
			# for g in groupby( d,key=lambda x:x[1]):
			# 	sorting = g[0]
			# 	kol_golov=kol_korma=racion_id=0
			# 	stado_zagon_id = []
			# 	for i in g[1]:
			# 		stado_zagon_id.append(i[3])
			# 		stado_fiz_group_id = i[2]

			# 	print stado_zagon_id
			# 	svod_line.create({'korm_korm_ostatok_id':   self.id,
			# 						'name': self.name,
			# 						'stado_zagon_id':   [(6, 0, stado_zagon_id)],
			# 						'stado_fiz_group_id':    stado_fiz_group_id.id,
			# 						})

		

	name = fields.Char(string='Номер', required=True, copy=False, readonly=True, index=True, default='New')
	date = fields.Date(string='Дата', required=True, copy=False, default=fields.Datetime.now)
	korm_korm_ostatok_line = fields.One2many('korm.korm_ostatok_line', 'korm_korm_ostatok_id', string=u"Строка Остатки Кормления",copy=True)
	korm_korm_ostatok_svod_line = fields.One2many('korm.korm_ostatok_svod_line', 'korm_korm_ostatok_id', string=u"Строка Свода Остатки Кормлениея",copy=True)
	svodno = fields.Boolean(string=u"Остатки вводятся по группе загонов", default=True)
	description = fields.Text(string=u"Коментарии")

class korm_korm_ostatok_line(models.Model):
	_name = 'korm.korm_ostatok_line'
	_description = u'Строка Остатки Кормления'
	

	@api.one
	def return_name(self):
		self.name = self.stado_zagon_id.nomer

	#@api.multi
	@api.depends('korm_korm_ostatok_id.date')
	def return_date(self):
		for rec in self:
			rec.date = rec.korm_korm_ostatok_id.date
		


	name = fields.Char(string=u"Наименование", compute='return_name')
	korm_korm_ostatok_id = fields.Many2one('korm.korm_ostatok', ondelete='cascade', string=u"Остатки Кормления", required=True)
	
	date = fields.Date(string='Дата', store=True, compute='return_date')
	stado_zagon_id = fields.Many2one('stado.zagon', readonly=True, string=u'Загон', required=True)
	stado_fiz_group_id = fields.Many2one('stado.fiz_group', readonly=True, string=u'Физиологическая группа', store=True, compute='return_name')
	kol_golov_zagon = fields.Integer(string=u"Ср. кол-во голов в загоне", store=True, readonly=True)
	kol_korma_norma = fields.Float(digits=(10, 3), string=u"Дача корма по норме", store=True, readonly=True)
	kol_korma_fakt = fields.Float(digits=(10, 3), string=u"Дача корма по факту", store=True, readonly=True)
	kol_korma_otk = fields.Float(digits=(10, 3), string=u"Откл.", store=True, readonly=True)
	
	kol_ostatok = fields.Float(digits=(10, 3), string=u"Кол-во остаток корма", copy=False, readonly=True)
	procent_ostatkov = fields.Float(digits=(10, 1), string=u"% остатков", copy=False, readonly=True)
	procent_ostatkov_prev = fields.Float(digits=(10, 1), string=u"% ост. пред. день", copy=False, readonly=True)
   
	
	

class korm_korm_ostatok_svod_line(models.Model):
	_name = 'korm.korm_ostatok_svod_line'
	_description = u'Строка Свода Остатки Кормления'
	

	@api.one
	@api.depends('stado_zagon_id')
	def return_name(self):
		self.name = self.stado_zagon_id
		if self.stado_zagon_id:
			for line in self.stado_zagon_id:
				self.stado_fiz_group_id = line.stado_fiz_group_id

	name = fields.Char(string=u"Наименование", compute='return_name')
	korm_korm_ostatok_id = fields.Many2one('korm.korm_ostatok', ondelete='cascade', string=u"Остатки Кормления", required=True)
	
	stado_zagon_id = fields.Many2many('stado.zagon', string=u'Загоны', required=True)
	stado_fiz_group_id = fields.Many2one('stado.fiz_group', readonly=True, string=u'Физиологическая группа', store=True, compute='return_name')
	kol_golov_zagon = fields.Integer(string=u"Ср. кол-во голов в загоне", store=True, readonly=True)
	
	kol_ostatok = fields.Float(digits=(10, 3), string=u"Кол-во остаток корма", copy=False)




class korm_potrebnost(models.Model):
	_name = 'korm.potrebnost'
	_description = u'Потребность в кормах'
	_order = 'date desc'

	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New' or vals.get('name', 'New') == None:
			vals['name'] = self.env['ir.sequence'].next_by_code('korm.potrebnost') or 'New'

		result = super(korm_potrebnost, self).create(vals)
		return result

	@api.one
	@api.depends('date_start','date_end')
	def get_period_day(self):
		if self.date_start and self.date_end:
			d1 = datetime.strptime(self.date_start, "%Y-%m-%d")
			d2 = datetime.strptime(self.date_end, "%Y-%m-%d")
			self.period_day = (d2-d1).days + 1
			

	@api.one
	def action_zapolnit_zagoni(self):

		zagon_line = self.env['korm.potrebnost_zagon_line']
		del_line = zagon_line.search([('korm_potrebnost_id',	'=',	self.id)])
		del_line.unlink()


		ras_date_start = ras_date_end = 0
		
		date = datetime.strptime(self.date, "%Y-%m-%d")
		ras_date_end = date - timedelta(days=1)
		
		ras_date_start = ras_date_end - timedelta(days=self.kol_day)
		#print 'ddddddddddddddd=', (ras_date_start,ras_date_end )
		zapros = """SELECT  stado_zagon_id, 
							max(stado_fiz_group_id),
							max(korm_racion_id),
							avg(kol_golov_zagon)
					FROM korm_korm_line
					WHERE date>='%s' and date<='%s'	
					GROUP BY stado_zagon_id
					Order by stado_zagon_id
				""" %(ras_date_start.date(), ras_date_end.date())
		#print zapros
		self._cr.execute(zapros,)
		zagons = self._cr.fetchall()
		for z in zagons:
			zagon_line.create({
								'korm_potrebnost_id':	self.id,
								'stado_zagon_id':	z[0],
								'stado_fiz_group_id':	z[1],
								'korm_racion_id':	z[2],
								'kol_golov':	z[3],
								})

	
	@api.one
	def action_raschet(self):

		korma_line = self.env['korm.potrebnost_korm_line']
		del_line = korma_line.search([('korm_potrebnost_id',	'=',	self.id)])
		del_line.unlink()

		kombikorm_line = self.env['korm.potrebnost_kombikorm_line']
		del_line = kombikorm_line.search([('korm_potrebnost_id',	'=',	self.id)])
		del_line.unlink()

		zapros = """SELECT r.nomen_nomen_id,
						sum(r.kol*z.kol_golov) as kol_korma

					FROM korm_racion_line r
					left join korm_potrebnost_zagon_line z on z.korm_racion_id=r.korm_racion_id
					WHERE r.korm_racion_id IN ( SELECT korm_racion_id 
												FROM korm_potrebnost_zagon_line 
												WHERE korm_potrebnost_id=%s) 
					group by r.nomen_nomen_id
					Order by r.nomen_nomen_id
				""" %(self.id,)
		#print zapros
		self._cr.execute(zapros,)
		korms = self._cr.fetchall()
		for k in korms:
			receptura = self.env['korm.receptura']
			receptura_id = receptura.search([('nomen_nomen_id', '=',k[0]), ('date', '<=', self.date)], order="date desc",limit=1).id
	
			korma_line.create({
								'korm_potrebnost_id':	self.id,
								'nomen_nomen_id':	k[0],
								'korm_receptura_id':	receptura_id,
								'kol':	k[1],
								'kol_za_period': k[1] * self.period_day,
								})

		self.kol_golov = self.kol_korma = 0
		for line in self.korm_potrebnost_zagon_line:
			self.kol_golov += line.kol_golov
			self.kol_korma += line.kol_korma


		zapros = """SELECT r.nomen_nomen_id,
						sum(r.kol*z.kol/l.amount) as kol_korma

					FROM korm_receptura_line r
					left join korm_potrebnost_korm_line z on z.korm_receptura_id=r.korm_receptura_id
					left join korm_receptura l on l.id=r.korm_receptura_id
					WHERE r.korm_receptura_id IN ( SELECT korm_receptura_id 
												FROM korm_potrebnost_korm_line 
												WHERE korm_potrebnost_id=%s and korm_receptura_id>0) 
					group by r.nomen_nomen_id
					Order by r.nomen_nomen_id
				""" %(self.id,)
		#print zapros
		self._cr.execute(zapros,)
		kombikorms = self._cr.fetchall()
		for k in kombikorms:
			
			kombikorm_line.create({
								'korm_potrebnost_id':	self.id,
								'nomen_nomen_id':	k[0],
								'kol':	k[1],
								'kol_za_period': k[1] * self.period_day,
								})




	name = fields.Char(string='Номер', required=True, copy=False, readonly=True, index=True, default='New')
	date = fields.Date(string='Дата', required=True, copy=False, default=fields.Datetime.now)
	date_start = fields.Date(string='Дата начала', required=True, copy=False, default=fields.Datetime.now)
	date_end = fields.Date(string='Дата окончания', required=True, copy=False)
	
	kol_day = fields.Integer(string=u"Расчет поголовья за, дней назад", default=7, store=True, copy=True)
	period_day = fields.Integer(string=u"Кол-во дней в периоде", compute='get_period_day', store=True, copy=True)
	

	korm_potrebnost_zagon_line = fields.One2many('korm.potrebnost_zagon_line', 'korm_potrebnost_id', string=u"Структура стада", copy=True)
	korm_potrebnost_korm_line = fields.One2many('korm.potrebnost_korm_line', 'korm_potrebnost_id', string=u"Потребность в кормах")
	korm_potrebnost_kombikorm_line = fields.One2many('korm.potrebnost_kombikorm_line', 'korm_potrebnost_id', string=u"Расчет для комбикормов")
	
	
	sostavil_id = fields.Many2one('res.partner', string='Составил')
	utverdil_id = fields.Many2one('res.partner', string='Утвердил')
	
	kol_golov = fields.Integer(string=u"Кол-во голов", store=True, readonly=True, copy=True)
	kol_korma = fields.Integer(string=u"Кол-во корма", readonly=True, store=True, copy=True)
	description = fields.Text(string=u"Коментарии")

		


	

class korm_potrebnost_zagon_line(models.Model):
	_name = 'korm.potrebnost_zagon_line'
	_description = u'Структура стада'
	#_order = 'name'


	@api.one
	@api.depends('stado_zagon_id')
	def return_name(self):
		self.name = self.stado_zagon_id.nomer

		self.stado_fiz_group_id = self.stado_zagon_id.stado_fiz_group_id
		racion = self.env['korm.racion']
		racion_id = racion.search([('stado_fiz_group_id', '=', self.stado_fiz_group_id.id), ('date', '<=', self.korm_potrebnost_id.date)], order="date desc",limit=1).id
		self.korm_racion_id = racion_id
				
		self.kol_golov = 0

	@api.one
	@api.depends('kol_golov', 'procent_raciona')
	def _raschet(self):
		self.kol_korma=0
		if self.kol_golov>0 and self.korm_racion_id!=False:
			self.kol_korma = self.korm_racion_id.kol * self.kol_golov * self.procent_raciona/100
	



	name = fields.Char(string=u"Наименование", compute='return_name')
	korm_potrebnost_id = fields.Many2one('korm.potrebnost', ondelete='cascade', string=u"Потребность в кормах", required=True)
	
	stado_zagon_id = fields.Many2one('stado.zagon', string=u'Загон', required=True)
	stado_fiz_group_id = fields.Many2one('stado.fiz_group', string=u'Физиологическая группа', store=True, compute='return_name')
	korm_racion_id = fields.Many2one('korm.racion', string=u'Рацион кормления', store=True, compute='return_name')
	kol_golov = fields.Integer(string=u"Ср.поголовье в сутки", store=True)
	
	procent_raciona = fields.Integer(string=u"% дачи рациона", store=True, default=100)
	kol_korma = fields.Float(digits=(10, 3), string=u"Кол-во корма", copy=False, compute='_raschet')
	
	description = fields.Text(string=u"Коментарии")
	


class korm_potrebnost_korm_line(models.Model):
	_name = 'korm.potrebnost_korm_line'
	_description = u'Строки Потребность в кормах'
	_order = 'sorting_group, sorting_name'


	@api.one
	def return_name(self):
		if self.nomen_nomen_id:
			self.name = self.nomen_nomen_id.name
		#self.kol_za_period = self.kol * self.korm_potrebnost_id.period_day

	# @api.multi
	# def return_sorting(self):
	# 	for line in self:
	# 		line.sorting = line.nomen_group_id.name + ' ' + line.nomen_nomen_id.name
	# 		print 'ddddddddddddddddd=====', line.sorting

	name = fields.Char(string=u"Наименование", compute='return_name')
	korm_potrebnost_id = fields.Many2one('korm.potrebnost', ondelete='cascade', string=u"Потребность в кормах", required=True)
	
	nomen_nomen_id = fields.Many2one('nomen.nomen', string=u'Наименование корма', required=True, readonly=True)
	nomen_group_id = fields.Many2one('nomen.group', string=u'Группа', related='nomen_nomen_id.nomen_group_id', readonly=True,  store=True)
	ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", related='nomen_nomen_id.ed_izm_id', readonly=True,  store=True)
	korm_receptura_id = fields.Many2one('korm.receptura', string=u"Рецептура", readonly=True,  store=True)
	
	kol = fields.Float(digits=(10, 3), string=u"Кол-во в сутки", copy=False, readonly=True)
	kol_za_period = fields.Float(digits=(10, 3), string=u"Кол-во на период", copy=False, readonly=True, store=True)
	#поля для сортировки
	sorting_name = fields.Char(string=u"Наименование", related='nomen_nomen_id.name',  store=True)
	sorting_group = fields.Char(string=u"Группа", related='nomen_nomen_id.nomen_group_id.name',  store=True)
		
	
class korm_potrebnost_kombikorm_line(models.Model):
	_name = 'korm.potrebnost_kombikorm_line'
	_description = u'Строки Потребность для производства комбикормов'
	_order = 'sorting_group, sorting_name'


	@api.one
	def return_name(self):
		if self.nomen_nomen_id:
			self.name = self.nomen_nomen_id.name
		#self.kol_za_period = self.kol * self.korm_potrebnost_id.period_day

	# @api.multi
	# def return_sorting(self):
	# 	for line in self:
	# 		line.sorting = line.nomen_group_id.name + ' ' + line.nomen_nomen_id.name
	# 		print 'ddddddddddddddddd=====', line.sorting

	name = fields.Char(string=u"Наименование", compute='return_name')
	korm_potrebnost_id = fields.Many2one('korm.potrebnost', ondelete='cascade', string=u"Потребность в кормах", required=True)
	
	nomen_nomen_id = fields.Many2one('nomen.nomen', string=u'Наименование корма', required=True, readonly=True)
	nomen_group_id = fields.Many2one('nomen.group', string=u'Группа', related='nomen_nomen_id.nomen_group_id', readonly=True,  store=True)
	ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", related='nomen_nomen_id.ed_izm_id', readonly=True,  store=True)
	
	kol = fields.Float(digits=(10, 3), string=u"Кол-во в сутки", copy=False, readonly=True)
	kol_za_period = fields.Float(digits=(10, 3), string=u"Кол-во на период", copy=False, readonly=True, store=True)
	#поля для сортировки
	sorting_name = fields.Char(string=u"Наименование", related='nomen_nomen_id.name',  store=True)
	sorting_group = fields.Char(string=u"Группа", related='nomen_nomen_id.nomen_group_id.name',  store=True)