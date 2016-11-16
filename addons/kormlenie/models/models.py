# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError

parametrs = ['ov', 'sv', 'oe', 'sp', 'pp', 'sk', 'sj', 'ca', 'p', 
		'sahar', 'krahmal', 'bev', 'magniy', 'natriy', 'kaliy', 'hlor', 'sera', 
		'udp', 'me', 'xp', 'nrp', 'rnb', 'nrp_p']

class korm_pit_standart(models.Model):
    _name = 'korm.pit_standart'
    _description = 'Питательность кормов по стандарту'
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



    name = fields.Char(string="Наименование", compute='return_name')
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

    _sql_constraints = [
						    ('nomen_nomen_id_unique', 'unique(nomen_nomen_id)', u'Питательность для такого корма уже существует!')
						]

class stado_fiz_group(models.Model):
    _name = 'stado.fiz_group'
    _description = 'Физиологическая группа'
    _order = 'name'

    name = fields.Char(string="Наименование", required=True)
    _sql_constraints = [
						    ('name_unique', 'unique(name_id)', u'Такая физиологическая группа уже существует!')
						]
    


class stado_zagon(models.Model):
    _name = 'stado.zagon'
    _description = 'Загоны'
    _order = 'nomer'

    name = fields.Char(string="Наименование", required=True)
    nomer = fields.Integer(string="Номер", required=True)
    stado_fiz_group_id = fields.Many2one('stado.fiz_group', string='Физиологическая группа', required=True)


class korm_analiz_pit(models.Model):
    _name = 'korm.analiz_pit'
    _description = 'Анализ питательности кормов'
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


    name = fields.Char(string="Наименование", compute='return_name')
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Наименование корма', required=True)
    korm_receptura_id = fields.Many2one('korm.receptura', ondelete='cascade', string='Рецептура комбикорма')

    date = fields.Date(string='Дата', required=True, default=fields.Datetime.now)
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




    name = fields.Char(string="Наименование", compute='return_name')
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Наименование', required=True)
    date = fields.Date(string='Дата', required=True, default=fields.Datetime.now)
    #korm_analiz_pit_id = fields.One2many('korm.analiz_pit', 'korm_receptura_id', string="Анализ кормов")
    korm_receptura_line = fields.One2many('korm.receptura_line', 'korm_receptura_id', string="Строка Рецептура комбикормов")
    amount = fields.Float(digits=(10, 3), string="Всего Кол-во", store=True, compute='_raschet')

    ov = fields.Float(digits=(10, 2), string="ОВ", store=True, compute='_raschet')
    sv = fields.Float(digits=(10, 2), string="СВ", store=True, compute='_raschet')
    oe = fields.Float(digits=(10, 2), string="ОЭ", store=True, compute='_raschet')
    sp = fields.Float(digits=(10, 2), string="СП", store=True, compute='_raschet')
    pp = fields.Float(digits=(10, 2), string="ПП", store=True, compute='_raschet')
    sk = fields.Float(digits=(10, 2), string="СК", store=True, compute='_raschet')
    sj = fields.Float(digits=(10, 2), string="СЖ", store=True, compute='_raschet')
    ca = fields.Float(digits=(10, 2), string="Ca", store=True, compute='_raschet')
    p = fields.Float(digits=(10, 2), string="P", store=True, compute='_raschet')
    sahar = fields.Float(digits=(10, 2), string="Сахар", store=True, compute='_raschet')
    krahmal = fields.Float(digits=(10, 2), string="Крахмал", store=True, compute='_raschet')
    bev = fields.Float(digits=(10, 2), string="БЭВ", store=True, compute='_raschet')
    magniy = fields.Float(digits=(10, 2), string="Магний", store=True, compute='_raschet')
    natriy = fields.Float(digits=(10, 2), string="Натрий", store=True, compute='_raschet')
    kaliy = fields.Float(digits=(10, 2), string="Калий", store=True, compute='_raschet')
    hlor = fields.Float(digits=(10, 2), string="Хлор", store=True, compute='_raschet')
    sera = fields.Float(digits=(10, 2), string="Сера", store=True, compute='_raschet')
    udp = fields.Float(digits=(10, 2), string="UDP", store=True, compute='_raschet')
    me = fields.Float(digits=(10, 2), string="ME", store=True, compute='_raschet')
    xp = fields.Float(digits=(10, 2), string="XP", store=True, compute='_raschet')
    nrp = fields.Float(digits=(10, 2), string="НРП", store=True, compute='_raschet')
    rnb = fields.Float(digits=(10, 2), string="RNB", store=True, compute='_raschet')
    nrp_p = fields.Float(digits=(10, 2), string="%НРП", store=True, compute='_raschet')
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


class korm_receptura_line(models.Model):
    _name = 'korm.receptura_line'
    _description = 'Строка Рецептура комбикормов'
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
            self.ed_izm_id = self.nomen_nomen_id.ed_izm_id
            analiz = self.env['korm.analiz_pit']
            analiz_id = analiz.search([('nomen_nomen_id', '=', self.nomen_nomen_id.id)], order="date desc",limit=1).id
            self.korm_analiz_pit_id = analiz_id

            


    name = fields.Char(string="Наименование", compute='return_name')
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Наименование корма', required=True)
    korm_analiz_pit_id = fields.Many2one('korm.analiz_pit', string='Анализ корма', store=True, compute='_nomen')
    korm_receptura_id = fields.Many2one('korm.receptura', ondelete='cascade', string="Рецептура комбикормов", required=True)
    ed_izm_id = fields.Many2one('nomen.ed_izm', string="Ед.изм.", compute='_nomen',  store=True)
    kol = fields.Float(digits=(10, 3), string="Кол-во", required=True)
   



class korm_norm(models.Model):
    _name = 'korm.norm'
    _description = 'Нормы кормления'
    _order = 'date desc'



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

    


    name = fields.Char(string="Наименование", compute='return_name')
    stado_fiz_group_id = fields.Many2one('stado.fiz_group', string='Физиологическая группа', required=True)
    date = fields.Date(string='Дата', required=True, default=fields.Datetime.now)
    
    ov_min = fields.Float(digits=(10, 2), string="ОВ")
    sv_min = fields.Float(digits=(10, 2), string="СВ")
    oe_min = fields.Float(digits=(10, 2), string="ОЭ")
    sp_min = fields.Float(digits=(10, 2), string="СП")
    pp_min = fields.Float(digits=(10, 2), string="ПП")
    sk_min = fields.Float(digits=(10, 2), string="СК")
    sj_min = fields.Float(digits=(10, 2), string="СЖ")
    ca_min = fields.Float(digits=(10, 2), string="Ca")
    p_min = fields.Float(digits=(10, 2), string="P")
    sahar_min = fields.Float(digits=(10, 2), string="Сахар")
    krahmal_min = fields.Float(digits=(10, 2), string="Крахмал")
    bev_min = fields.Float(digits=(10, 2), string="БЭВ")
    magniy_min = fields.Float(digits=(10, 2), string="Магний")
    natriy_min = fields.Float(digits=(10, 2), string="Натрий")
    kaliy_min = fields.Float(digits=(10, 2), string="Калий")
    hlor_min = fields.Float(digits=(10, 2), string="Хлор")
    sera_min = fields.Float(digits=(10, 2), string="Сера")
    udp_min = fields.Float(digits=(10, 2), string="UDP", store=True, compute='_raschet')
    me_min = fields.Float(digits=(10, 2), string="ME", store=True, compute='_raschet')
    xp_min = fields.Float(digits=(10, 2), string="XP", store=True, compute='_raschet')
    nrp_min = fields.Float(digits=(10, 2), string="НРП", store=True, compute='_raschet')
    rnb_min = fields.Float(digits=(10, 2), string="RNB", store=True, compute='_raschet')
    nrp_p_min = fields.Float(digits=(10, 2), string="%НРП")
    

    ov_max = fields.Float(digits=(10, 2), string="ОВ")
    sv_max = fields.Float(digits=(10, 2), string="СВ")
    oe_max = fields.Float(digits=(10, 2), string="ОЭ")
    sp_max = fields.Float(digits=(10, 2), string="СП")
    pp_max = fields.Float(digits=(10, 2), string="ПП")
    sk_max = fields.Float(digits=(10, 2), string="СК")
    sj_max = fields.Float(digits=(10, 2), string="СЖ")
    ca_max = fields.Float(digits=(10, 2), string="Ca")
    p_max = fields.Float(digits=(10, 2), string="P")
    sahar_max = fields.Float(digits=(10, 2), string="Сахар")
    krahmal_max = fields.Float(digits=(10, 2), string="Крахмал")
    bev_max = fields.Float(digits=(10, 2), string="БЭВ")
    magniy_max = fields.Float(digits=(10, 2), string="Магний")
    natriy_max = fields.Float(digits=(10, 2), string="Натрий")
    kaliy_max = fields.Float(digits=(10, 2), string="Калий")
    hlor_max = fields.Float(digits=(10, 2), string="Хлор")
    sera_max = fields.Float(digits=(10, 2), string="Сера")
    udp_max = fields.Float(digits=(10, 2), string="UDP", store=True, compute='_raschet')
    me_max = fields.Float(digits=(10, 2), string="ME", store=True, compute='_raschet')
    xp_max = fields.Float(digits=(10, 2), string="XP", store=True, compute='_raschet')
    nrp_max = fields.Float(digits=(10, 2), string="НРП", store=True, compute='_raschet')
    rnb_max = fields.Float(digits=(10, 2), string="RNB", store=True, compute='_raschet')
    nrp_p_max = fields.Float(digits=(10, 2), string="%НРП")