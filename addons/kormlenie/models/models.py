# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError


class korm_pit_standart(models.Model):
    _name = 'korm.pit_standart'
    _description = 'Питательность кормов по стандарту'
    _order = 'name'


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



    name = fields.Char(string="Наименование", required=True, compute='return_name', store=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Наименование корма', required=True)
    ov = fields.Float(digits=(10, 2), string="ОВ")
    sv = fields.Float(digits=(10, 2), string="СВ")
    oe = fields.Float(digits=(10, 2), string="ОЭ")
    sp = fields.Float(digits=(10, 2), string="СП")
    pp = fields.Float(digits=(10, 2), string="ПП")
    sk = fields.Float(digits=(10, 2), string="СК")
    sj = fields.Float(digits=(10, 2), string="СЖ")
    ca = fields.Float(digits=(10, 2), string="Ca")
    p = fields.Float(digits=(10, 2), string="P")
    sahar = fields.Float(digits=(10, 2), string="Сахар")
    krahmal = fields.Float(digits=(10, 2), string="Крахмал")
    bev = fields.Float(digits=(10, 2), string="БЭВ")
    magniy = fields.Float(digits=(10, 2), string="Магний")
    natriy = fields.Float(digits=(10, 2), string="Натрий")
    kaliy = fields.Float(digits=(10, 2), string="Калий")
    hlor = fields.Float(digits=(10, 2), string="Хлор")
    sera = fields.Float(digits=(10, 2), string="Сера")
    udp = fields.Float(digits=(10, 2), string="UDP", store=True, compute='_raschet')
    me = fields.Float(digits=(10, 2), string="ME", store=True, compute='_raschet')
    xp = fields.Float(digits=(10, 2), string="XP", store=True, compute='_raschet')
    nrp = fields.Float(digits=(10, 2), string="НРП", store=True, compute='_raschet')
    rnb = fields.Float(digits=(10, 2), string="RNB", store=True, compute='_raschet')
    nrp_p = fields.Float(digits=(10, 2), string="%НРП")


class stado_zagon(models.Model):
    _name = 'stado.zagon'
    _description = 'Загоны'
    _order = 'nomer'

    name = fields.Char(string="Наименование", required=True)
    nomer = fields.Integer(string="Номер", required=True)


class korm_analiz_pit(models.Model):
    _name = 'korm.analiz_pit'
    _description = 'Анализ питательности кормов'
    _order = 'date desc, nomen_nomen_id'


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


    name = fields.Char(string="Наименование", compute='return_name')
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Наименование корма', required=True)
    korm_receptura_id = fields.Many2one('korm.receptura', ondelete='cascade', string='Рецептура комбикорма')

    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now)
    ov = fields.Float(digits=(10, 2), string="ОВ")
    sv = fields.Float(digits=(10, 2), string="СВ")
    oe = fields.Float(digits=(10, 2), string="ОЭ")
    sp = fields.Float(digits=(10, 2), string="СП")
    pp = fields.Float(digits=(10, 2), string="ПП")
    sk = fields.Float(digits=(10, 2), string="СК")
    sj = fields.Float(digits=(10, 2), string="СЖ")
    ca = fields.Float(digits=(10, 2), string="Ca")
    p = fields.Float(digits=(10, 2), string="P")
    sahar = fields.Float(digits=(10, 2), string="Сахар")
    krahmal = fields.Float(digits=(10, 2), string="Крахмал")
    bev = fields.Float(digits=(10, 2), string="БЭВ")
    magniy = fields.Float(digits=(10, 2), string="Магний")
    natriy = fields.Float(digits=(10, 2), string="Натрий")
    kaliy = fields.Float(digits=(10, 2), string="Калий")
    hlor = fields.Float(digits=(10, 2), string="Хлор")
    sera = fields.Float(digits=(10, 2), string="Сера")
    udp = fields.Float(digits=(10, 2), string="UDP", store=True, compute='_raschet')
    me = fields.Float(digits=(10, 2), string="ME", store=True, compute='_raschet')
    xp = fields.Float(digits=(10, 2), string="XP", store=True, compute='_raschet')
    nrp = fields.Float(digits=(10, 2), string="НРП", store=True, compute='_raschet')
    rnb = fields.Float(digits=(10, 2), string="RNB", store=True, compute='_raschet')
    nrp_p = fields.Float(digits=(10, 2), string="%НРП")
    #Параметры питательности по стандарту:
    ov_s = fields.Float(digits=(10, 2), string="ОВ", compute='_standart')
    sv_s = fields.Float(digits=(10, 2), string="СВ", compute='_standart')
    oe_s = fields.Float(digits=(10, 2), string="ОЭ", compute='_standart')
    sp_s = fields.Float(digits=(10, 2), string="СП", compute='_standart')
    pp_s = fields.Float(digits=(10, 2), string="ПП", compute='_standart')
    sk_s = fields.Float(digits=(10, 2), string="СК", compute='_standart')
    sj_s = fields.Float(digits=(10, 2), string="СЖ", compute='_standart')
    ca_s = fields.Float(digits=(10, 2), string="Ca", compute='_standart')
    p_s = fields.Float(digits=(10, 2), string="P", compute='_standart')
    sahar_s = fields.Float(digits=(10, 2), string="Сахар", compute='_standart')
    krahmal_s = fields.Float(digits=(10, 2), string="Крахмал", compute='_standart')
    bev_s = fields.Float(digits=(10, 2), string="БЭВ", compute='_standart')
    magniy_s = fields.Float(digits=(10, 2), string="Магний", compute='_standart')
    natriy_s = fields.Float(digits=(10, 2), string="Натрий", compute='_standart')
    kaliy_s = fields.Float(digits=(10, 2), string="Калий", compute='_standart')
    hlor_s = fields.Float(digits=(10, 2), string="Хлор", compute='_standart')
    sera_s = fields.Float(digits=(10, 2), string="Сера", compute='_standart')
    udp_s = fields.Float(digits=(10, 2), string="UDP", compute='_standart')
    me_s = fields.Float(digits=(10, 2), string="ME", compute='_standart')
    xp_s = fields.Float(digits=(10, 2), string="XP", compute='_standart')
    nrp_s = fields.Float(digits=(10, 2), string="НРП", compute='_standart')
    rnb_s = fields.Float(digits=(10, 2), string="RNB", compute='_standart')
    nrp_p_s = fields.Float(digits=(10, 2), string="%НРП", compute='_standart')



class korm_receptura(models.Model):
    _name = 'korm.receptura'
    _description = 'Рецептура комбикормов'
    _order = 'date desc, nomen_nomen_id'


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

    @api.model
    def create(self, vals):
        result = super(korm_receptura, self).create(vals)
        print "rrrrrrrrrrrrrrrrrrrr==========", result.id
        vals['korm_receptura_id'] = result.id
        self.env['korm.analiz_pit'].create(vals)
        return result

    # @api.multi
    # def unlink(self):
        
    #     #print 'sssssssssssssssssssssssssssssssssssssssssssssss', self
    #     for pp in self:
    #         if pp.state != 'done':
    #             raise exceptions.ValidationError(_(u"Документ №%s Проведен и не может быть удален!" % (pp.name)))

    #     return super(sklad_inventarizaciya, self).unlink()

    name = fields.Char(string="Наименование", compute='return_name')
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Наименование корма', required=True)
    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now)
    korm_analiz_pit_id = fields.One2many('korm.analiz_pit', 'korm_receptura_id', string="Анализ кормов")

    ov = fields.Float(digits=(10, 2), string="ОВ")
    sv = fields.Float(digits=(10, 2), string="СВ")
    oe = fields.Float(digits=(10, 2), string="ОЭ")
    sp = fields.Float(digits=(10, 2), string="СП")
    pp = fields.Float(digits=(10, 2), string="ПП")
    sk = fields.Float(digits=(10, 2), string="СК")
    sj = fields.Float(digits=(10, 2), string="СЖ")
    ca = fields.Float(digits=(10, 2), string="Ca")
    p = fields.Float(digits=(10, 2), string="P")
    sahar = fields.Float(digits=(10, 2), string="Сахар")
    krahmal = fields.Float(digits=(10, 2), string="Крахмал")
    bev = fields.Float(digits=(10, 2), string="БЭВ")
    magniy = fields.Float(digits=(10, 2), string="Магний")
    natriy = fields.Float(digits=(10, 2), string="Натрий")
    kaliy = fields.Float(digits=(10, 2), string="Калий")
    hlor = fields.Float(digits=(10, 2), string="Хлор")
    sera = fields.Float(digits=(10, 2), string="Сера")
    udp = fields.Float(digits=(10, 2), string="UDP", store=True, compute='_raschet')
    me = fields.Float(digits=(10, 2), string="ME", store=True, compute='_raschet')
    xp = fields.Float(digits=(10, 2), string="XP", store=True, compute='_raschet')
    nrp = fields.Float(digits=(10, 2), string="НРП", store=True, compute='_raschet')
    rnb = fields.Float(digits=(10, 2), string="RNB", store=True, compute='_raschet')
    nrp_p = fields.Float(digits=(10, 2), string="%НРП")