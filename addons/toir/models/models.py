# -*- coding: utf-8 -*-

from __future__ import division #при делении будет возвращаться float
from openerp import models, fields, api, exceptions, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError


#----------------------------------------------------------
# Активы предприятия
#----------------------------------------------------------


class aktiv_remont_service(models.Model):
    """Ремонтные службы"""
    _name = 'aktiv.remont_service'
    _description = u'Ремонтные службы'
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _order  = 'parent_left'
    _rec_name = 'complete_name'


    @api.one
    @api.depends('name', 'parent_id.complete_name')
    def _complete_name(self):
        """ Forms complete name of location from parent location to child location. """
        if self.parent_id.complete_name:
            self.complete_name = '%s/%s' % (self.parent_id.complete_name, self.name)
        else:
            self.complete_name = self.name

    @api.multi
    def name_get(self):
        ret_list = []
        for parent_id in self:
            orig_location = parent_id
            name = parent_id.name
            while parent_id.parent_id:
                parent_id = parent_id.parent_id
                if not name:
                    raise UserError(_('You have to set a name for this location.'))
                name = parent_id.name + "/" + name
            ret_list.append((orig_location.id, name))
        return ret_list

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """ search full name and barcode """
        if args is None:
            args = []
        recs = self.search(['|', ('name', operator, name), ('complete_name', operator, name)] + args, limit=limit)
        return recs.name_get()


    @api.model
    def create(self, vals):
        result = super(aktiv_remont_service, self).create(vals)
        return result


    name = fields.Char(string=u"Наименование", required=True) 
    complete_name = fields.Char(string=u"Наименование", compute='_complete_name', store=True) 
    parent_id = fields.Many2one('aktiv.remont_service', string=u'Родительский элемент', index=True, ondelete='cascade')
    child_ids = fields.One2many('aktiv.remont_service', 'parent_id', string=u'Подчиненные элементы')
    parent_left = fields.Integer('Left Parent', index=True)
    parent_right = fields.Integer('Right Parent', index=True)

    otvetstvenniy_id = fields.Many2one('res.partner', string='Ответственный')



class aktiv_categ(models.Model):
    """Категории  активов. используются для вывода иерархического вида справочника"""
    _name = 'aktiv.categ'
    _description = u'Категории активов'
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _order  = 'parent_left'
    _rec_name = 'complete_name'


    @api.one
    @api.depends('name', 'parent_id.complete_name')
    def _complete_name(self):
        """ Forms complete name of location from parent location to child location. """
        if self.parent_id.complete_name:
            self.complete_name = '%s/%s' % (self.parent_id.complete_name, self.name)
        else:
            self.complete_name = self.name


    def name_get(self):
        ret_list = []
        for parent_id in self:
            orig_location = parent_id
            name = parent_id.name
            while parent_id.parent_id:
                parent_id = parent_id.parent_id
                if not name:
                    raise UserError(_('You have to set a name for this location.'))
                name = parent_id.name + "/" + name
            ret_list.append((orig_location.id, name))
        return ret_list

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """ search full name and barcode """
        if args is None:
            args = []
        recs = self.search(['|', ('name', operator, name), ('complete_name', operator, name)] + args, limit=limit)
        return recs.name_get()


    @api.model
    def create(self, vals):
        result = super(aktiv_categ, self).create(vals)
        return result


    name = fields.Char(string=u"Наименование", required=True) 
    complete_name = fields.Char(string=u"Наименование", compute='_complete_name', store=True) 
    parent_id = fields.Many2one('aktiv.categ', string=u'Родительский элемент', index=True, ondelete='cascade')
    child_ids = fields.One2many('aktiv.categ', 'parent_id', string=u'Подчиненные элементы')
    parent_left = fields.Integer('Left Parent', index=True)
    parent_right = fields.Integer('Right Parent', index=True)






class aktiv_status(models.Model):
    """Статус активов (В работе, в ремонте и т.п"""
    _name = 'aktiv.status'
    _description = u'Статусы активов'
    _order  = 'name'
  
    name = fields.Char(string=u"Наименование", required=True) 

class aktiv_amortizaciya_group(models.Model):
    """Амортизационная группа (бух)"""
    _name = 'aktiv.amortizaciya_group'
    _description = u'Амортизационная группа (бух)'
    _order  = 'name'
  
    name = fields.Char(string=u"Наименование", required=True)

class aktiv_group_os(models.Model):
    """Группа ОС (бух)"""
    _name = 'aktiv.group_os'
    _description = u'Группа ОС (бух)'
    _order  = 'name'
  
    name = fields.Char(string=u"Наименование", required=True) 

class aktiv_group_uchet_os(models.Model):
    """Группа учета ОС (бух)"""
    _name = 'aktiv.group_uchet_os'
    _description = u'Группа учета ОС (бух)'
    _order  = 'name'
  
    name = fields.Char(string=u"Наименование", required=True) 



class aktiv_vid_rabot(models.Model):
    """Виды работ по ТОиР"""
    _name = 'aktiv.vid_rabot'
    _description = u'Виды работ'
    _order  = 'name'

 
    name = fields.Char(string=u"Наименование", required=True)
    description = fields.Text(string=u"Коментарии")

    aktiv_vid_rabot_price_line = fields.One2many('aktiv.vid_rabot_price_line', 'aktiv_vid_rabot_id', string=u"Строка Стоимость Виды работ", copy=True)


class aktiv_vid_rabot_price_line(models.Model):
    """Строка Стоимость работ"""
    _name = 'aktiv.vid_rabot_price_line'
    _description = u'Строка Стоимость работ'
    _order  = 'date desc'
    
    @api.one
    @api.depends('aktiv_vid_rabot_id.name')
    def return_name(self):
        self.name = self.aktiv_vid_rabot_id.name
    
    name = fields.Char(string=u"Наименование", compute='return_name', store=True)
    aktiv_vid_rabot_id = fields.Many2one('aktiv.vid_rabot', ondelete='cascade', string=u"Виды работ", required=True)

    date = fields.Date(string='Дата', required=True, index=True, copy=False)
    aktiv_type_id = fields.Many2one('aktiv.type', string='Тип актива', required=True)
    price = fields.Float(digits=(10, 2), string=u"Стоимость работ", required=True)
    currency_id = fields.Many2one('res.currency', string='Валюта', default=lambda self: self.env.user.company_id.currency_id.id)
    is_hozsposob = fields.Boolean(string=u"Хозспособ", default=True)
    is_podryad = fields.Boolean(string=u"Подрядный", default=False)
    partner_id = fields.Many2one('res.partner', string='Подрядчик')





class aktiv_vid_remonta(models.Model):
    """Виды ремонтов и диагностирования"""
    _name = 'aktiv.vid_remonta'
    _description = u'Виды ремонтов и диагностирования'
    _order  = 'name'
  
    name = fields.Char(string=u"Наименование", required=True)
    


class aktiv_type(models.Model):
    """Типы активов (Оборудование, транспорт и т.п"""
    _name = 'aktiv.type'
    _description = u'Типы активов'
    _order  = 'name'
  
    name = fields.Char(string=u"Наименование", required=True) 
    aktiv_tr = fields.One2many('aktiv.tr', 'aktiv_type_id', string=u"Типовые ремонты", copy=True)



class aktiv_tr(models.Model):
    """Типовые ремонты"""
    _name = 'aktiv.tr'
    _description = u'Типовые ремонты'
    _order  = 'name'

    
    @api.one
    @api.depends(   'is_raschet_price',
                    'aktiv_tr_price_line',
                    'aktiv_tr_raboti_line', 
                    'aktiv_tr_raboti_line.aktiv_vid_rabot_id.aktiv_vid_rabot_price_line',
                    'aktiv_tr_nomen_line',
                    'aktiv_tr_nomen_line.nomen_nomen_id.nomen_nomen_price_line'
                    )
    def _get_price(self):
        
        self.price = self.price_raboti = self.price_nomen = 0
        if self.is_raschet_price == True:
            if self.aktiv_tr_price_line:
                self.price_raboti = self.aktiv_tr_price_line[0].price
        else:
            for line in self.aktiv_tr_raboti_line:
                self.price_raboti += line.price

        if self.aktiv_tr_nomen_line:
            for line in self.aktiv_tr_nomen_line:
                self.price_nomen += line.amount
        self.price = self.price_raboti + self.price_nomen

  
    name = fields.Char(string=u"Наименование ремонта", required=True)

    aktiv_type_id = fields.Many2one('aktiv.type', ondelete='cascade', string='Тип актива', required=True)
    aktiv_vid_remonta_id = fields.Many2one('aktiv.vid_remonta', string='Виды ремонтов и диагностирования')

    
    is_raschet_price = fields.Boolean(string=u"Стоимость работ задается в ручную", default=True)
    price_raboti = fields.Float(digits=(10, 2), string=u"Стоимость работ", compute='_get_price', store=True)
    price_nomen = fields.Float(digits=(10, 2), string=u"Стоимость ТМЦ", compute='_get_price', store=True)
    price = fields.Float(digits=(10, 2), string=u"Общая стоимость", compute='_get_price', store=True)
    currency_id = fields.Many2one('res.currency', string='Валюта', default=lambda self: self.env.user.company_id.currency_id)
    is_hozsposob = fields.Boolean(string=u"Хозспособ", default=True)
    is_podryad = fields.Boolean(string=u"Подрядный", default=False)
    partner_id = fields.Many2one('res.partner', string='Подрядчик')

    period1 = fields.Integer(string="Интервал 1")
    period1_edizm = fields.Selection([
        ('hours', "ч."),
        ('days', "дн."),
        ('months', "мес."),
        ('years', "г."),
        ('km', "км."),
    ], default='months', string="Ед.изм.")
    period2 = fields.Integer(string="Интервал 2")
    period2_edizm = fields.Selection([
        ('hours', "ч."),
        ('days', "дн."),
        ('months', "мес."),
        ('years', "г."),
        ('km', "км"),
    ], default='months', string="Ед.изм.")
    
    



    aktiv_tr_raboti_line = fields.One2many('aktiv.tr_raboti_line', 'aktiv_tr_id', string=u"Строка регламентных работ. Типовые ремонты", copy=True)
    aktiv_tr_nomen_line = fields.One2many('aktiv.tr_nomen_line', 'aktiv_tr_id', string=u"Строка материалы. Типовые ремонты", copy=True)
    aktiv_tr_price_line = fields.One2many('aktiv.tr_price_line', 'aktiv_tr_id', string=u"Строка Стоимость Типовые ремонты", copy=False)


class aktiv_tr_price_line(models.Model):
    """Строка Стоимость Типовые ремонты"""
    _name = 'aktiv.tr_price_line'
    _description = u'Строка Стоимость Типовые ремонты'
    _order  = 'date desc'
    
    @api.one
    @api.depends('date')
    def return_name(self):
        self.name = self.aktiv_tr_id.name
    
    name = fields.Char(string=u"Наименование", compute='return_name', store=True)
    aktiv_tr_id = fields.Many2one('aktiv.tr', ondelete='cascade', string=u"Типовые ремонты", required=True)

    date = fields.Date(string='Дата', required=True, index=True, copy=False)
    price = fields.Float(digits=(10, 2), string=u"Стоимость работ", required=True)
    currency_id = fields.Many2one('res.currency', string=u'Валюта', default=lambda self: self.env.user.company_id.currency_id)
    is_hozsposob = fields.Boolean(string=u"Хозспособ", default=True)
    is_podryad = fields.Boolean(string=u"Подрядный", default=False)
    partner_id = fields.Many2one('res.partner', string=u'Подрядчик')


class aktiv_tr_raboti_line(models.Model):
    """Строка регламентных работ. Типовые ремонты"""
    _name = 'aktiv.tr_raboti_line'
    _description = u'Строка регламентных работ'
    _order  = 'name'


    @api.one
    @api.depends('aktiv_vid_rabot_id')
    def return_name(self):
        self.name = self.aktiv_vid_rabot_id.name


    @api.one
    @api.depends('aktiv_vid_rabot_id', 'aktiv_vid_rabot_id.aktiv_vid_rabot_price_line')
    def _get_price(self):
      
        vr_price = self.aktiv_vid_rabot_id.aktiv_vid_rabot_price_line.search([
                                                                                ('aktiv_type_id', '=', self.aktiv_tr_id.aktiv_type_id.id),
                                                                                ('aktiv_vid_rabot_id', '=', self.aktiv_vid_rabot_id.id),

                                                                            ],order="date desc", limit=1)
        if vr_price:
            self.price = vr_price[0].price
            self.currency_id = vr_price[0].currency_id
  

    name = fields.Char(string=u"Наименование", compute='return_name', store=True)
    aktiv_tr_id = fields.Many2one('aktiv.tr', ondelete='cascade', string=u"Типовые ремонты", required=True)

    aktiv_vid_rabot_id = fields.Many2one('aktiv.vid_rabot', string='Виды работ')
    

    is_hozsposob = fields.Boolean(string=u"Хозспособ", default=True)
    is_podryad = fields.Boolean(string=u"Подрядный", default=False)
    partner_id = fields.Many2one('res.partner', string='Подрядчик')
    price = fields.Float(digits=(10, 2), string=u"Стоимость", compute='_get_price', store=True)
    currency_id = fields.Many2one('res.currency', string='Валюта', compute='_get_price', store=True)

    aktiv_type_id = fields.Many2one('aktiv.type', string='Тип актива', related='aktiv_tr_id.aktiv_type_id', readonly=True,  store=True)
    aktiv_vid_remonta_id = fields.Many2one('aktiv.vid_remonta', string='Виды ремонтов и диагностирования', related='aktiv_tr_id.aktiv_vid_remonta_id', readonly=True,  store=True)


class aktiv_tr_nomen_line(models.Model):
    """Строка материалы. Типовые ремонты"""
    _name = 'aktiv.tr_nomen_line'
    _description = u'Строка материалы'
    _order  = 'name'

    @api.one
    @api.depends('nomen_nomen_id')
    def return_name(self):
        self.name = self.nomen_nomen_id.name


    @api.one
    @api.depends('nomen_nomen_id', 'nomen_nomen_id.nomen_nomen_price_line', 'kol')
    def _get_price(self):
        self.price = self.nomen_nomen_id.price
        self.currency_id = self.nomen_nomen_id.currency_id.id
        self.amount = self.price * self.kol
  
    name = fields.Char(string=u"Наименование", compute='return_name', store=True)
    aktiv_tr_id = fields.Many2one('aktiv.tr', ondelete='cascade', string=u"Типовые ремонты", required=True)

    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Материалы', required=True)
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", related='nomen_nomen_id.ed_izm_id', readonly=True,  store=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во", required=True)
    price = fields.Float(digits=(10, 2), string=u"Цена", compute='_get_price', store=True)
    currency_id = fields.Many2one('res.currency', string='Валюта', compute='_get_price', store=True)
    amount = fields.Float(digits=(10, 2), string=u"Стоимость", compute='_get_price', store=True)

    aktiv_type_id = fields.Many2one('aktiv.type', string='Тип актива', related='aktiv_tr_id.aktiv_type_id', readonly=True,  store=True)
    aktiv_vid_remonta_id = fields.Many2one('aktiv.vid_remonta', string='Виды ремонтов и диагностирования', related='aktiv_tr_id.aktiv_vid_remonta_id', readonly=True,  store=True)




class aktiv_aktiv(models.Model):
    """Активы предприятия. ОС и оборудования."""
    _name = 'aktiv.aktiv'
    _description = u'Активы (оборудование)'
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _order  = 'parent_left'
    _rec_name = 'complete_name'


    @api.one
    @api.depends('name', 'parent_id.complete_name', 'inv_nomer')
    def _complete_name(self):
        """ Forms complete name of location from parent location to child location. """

        if self.parent_id.complete_name:
            if self.inv_nomer:
                self.complete_name = '%s/%s [%s]' % (self.parent_id.complete_name, self.name, self.inv_nomer)
            else:
                self.complete_name = '%s/%s' % (self.parent_id.complete_name, self.name)
        else:
            if self.inv_nomer:
                self.complete_name = '%s [%s]' % (self.name, self.inv_nomer)
            else:
                self.complete_name = '%s' % (self.name)


    @api.multi
    def name_get(self):
        ret_list = []
        for parent_id in self:
            orig_location = parent_id
            name = parent_id.name
            while parent_id.parent_id:
                parent_id = parent_id.parent_id
                if not name:
                    raise UserError(_('You have to set a name for this location.'))
                name = parent_id.name + "/" + name
            ret_list.append((orig_location.id, name))
        return ret_list

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """ search full name and barcode """
        if args is None:
            args = []
        recs = self.search(['|', ('name', operator, name), ('complete_name', operator, name)] + args, limit=limit)
        return recs.name_get()


    @api.model
    def create(self, vals):
        result = super(aktiv_aktiv, self).create(vals)
        return result


    @api.one
    @api.depends('srok_slujbi_ot_vvoda', 'srok_slujbi', 'date_vipuska', 'date_vvoda')
    def _srok_slujbi(self):
        """ Forms complete name of location from parent location to child location. """
        if self.srok_slujbi:
            
            if self.srok_slujbi_ot_vvoda==True and self.date_vvoda:
                self.date_start = self.date_vvoda
            
            if self.srok_slujbi_ot_vvoda==False and self.date_vipuska:
                self.date_start = self.date_vipuska

            if self.date_start:
                date_end = fields.Date.from_string(self.date_start)# + timedelta(days=self.srok_slujbi*365)
                self.date_end = fields.Date.to_string(date_end.replace(year=date_end.year+self.srok_slujbi))
   
    @api.one
    @api.onchange('on_year')
    def _onchange_on_year(self):
        if self.on_year:
            for m in range(1, 13):
                self['m'+str(m)] = True


    name = fields.Char(string=u"Наименование", required=True)
    name_buh = fields.Char(string=u"Полное наименование (бух)")
    complete_name = fields.Char(string=u"Представление", compute='_complete_name', store=True) 
    parent_id = fields.Many2one('aktiv.aktiv', string=u'Входит в состав', index=True, ondelete='cascade')
    child_ids = fields.One2many('aktiv.aktiv', 'parent_id', string=u'Составные части')
    parent_left = fields.Integer('Left Parent', index=True)
    parent_right = fields.Integer('Right Parent', index=True)
    
    aktiv_categ_id = fields.Many2one('aktiv.categ', string=u"Категория", default=None)
    id_1c = fields.Char(string=u"Номер в 1С")
    active = fields.Boolean(string=u"Используется", default=True)
    is_uzel = fields.Boolean(string=u"Узел объекта", default=False)
    is_group = fields.Boolean(string=u"Это группа", default=False)

    is_nedvijimost = fields.Boolean(string=u"Это недвижимое имущество", default=False)
    buh_podrazdeleniya_id = fields.Many2one('buh.podrazdeleniya', string='Подразделение')
    aktiv_group_os_id = fields.Many2one('aktiv.group_os', string='Группа ОС (бух)')
    aktiv_group_uchet_os_id = fields.Many2one('aktiv.group_uchet_os', string='Группа учета ОС (бух)')
    location_location_id = fields.Many2one('location.location', string='Местонахождение')

    model = fields.Char(string=u"Модель")
    kod = fields.Char(string=u"Код")
    
    inv_nomer = fields.Char(string=u"Инвентарный номер")
    serial_nomer = fields.Char(string=u"Серийный номер")
    reg_nomer = fields.Char(string=u"Регистрационный номер")
    
    zavod_nomer = fields.Char(string=u"Заводской номер")
    zavod_name = fields.Char(string=u"Завод производитель")
    country_id = fields.Many2one('res.country', string=u"Страна производитель")

    postavshik_id = fields.Many2one('res.partner', string='Поставщик')
    aktiv_remont_service_id = fields.Many2one('aktiv.remont_service', string=u"Ремонтная служба")
    otvetstvenniy_id = fields.Many2one('res.partner', string='Ответственный', related='aktiv_remont_service_id.otvetstvenniy_id')
    aktiv_type_id = fields.Many2one('aktiv.type', string='Тип')



    date_vipuska = fields.Date(string='Дата выпуска')
    date_postupleniya = fields.Date(string='Дата поступления')
    date_vvoda = fields.Date(string='Дата ввода в экспл.')
    date_spisaniya = fields.Date(string='Дата списания')

    aktiv_status_id = fields.Many2one('aktiv.status', string='Статус')

    price_pokupki = fields.Float(digits=(10, 2), string=u"Первоначальная стоимость")
    price_period = fields.Float(digits=(10, 2), string=u"Стоимость на начало периода")
    amortizaciya = fields.Float(digits=(10, 2), string=u"Амортизация")
    price = fields.Float(digits=(10, 2), string=u"Текущая стоимость")
    
    
    
    aktiv_amortizaciya_group_id = fields.Many2one('aktiv.amortizaciya_group', string='Амортизационная группа')
    srok_slujbi = fields.Integer(string=u"Срок службы, лет")
    srok_slujbi_mtch = fields.Integer(string=u"Срок службы, моточасов")
    srok_slujbi_ot_vvoda = fields.Boolean(string=u"Срок службы от ввода в эксплуатацию", default=True)
    date_start = fields.Date(string='Срок службы, Дата начала', compute='_srok_slujbi', store=True)
    date_end = fields.Date(string='Срок службы, Дата окончания', compute='_srok_slujbi', store=True)

    teh_har = fields.Text(string=u"Технические характеристики")
    
    on_year = fields.Boolean(string=u"Круглогодично", default=True)
    m1 = fields.Boolean(string=u"1", default=True)
    m2 = fields.Boolean(string=u"2", default=True)
    m3 = fields.Boolean(string=u"3", default=True)
    m4 = fields.Boolean(string=u"4", default=True)
    m5 = fields.Boolean(string=u"5", default=True)
    m6 = fields.Boolean(string=u"6", default=True)
    m7 = fields.Boolean(string=u"7", default=True)
    m8 = fields.Boolean(string=u"8", default=True)
    m9 = fields.Boolean(string=u"9", default=True)
    m10 = fields.Boolean(string=u"10", default=True)
    m11 = fields.Boolean(string=u"11", default=True)
    m12 = fields.Boolean(string=u"12", default=True)
    

    aktiv_remont_ids = fields.One2many('aktiv.remont', 'aktiv_aktiv_id', copy=False, readonly=True)


    description = fields.Text(string=u"Коментарии")
    
    attachment_ids = fields.Many2many(
        'ir.attachment', 'aktiv_aktiv_ir_attachments_rel',
        'aktiv_aktiv_id', 'attachment_id', string='Вложения')



class aktiv_gr(models.Model):
    """График ремонтов"""
    _name = 'aktiv.gr'
    _description = u'График ремонтов'
    _order  = 'date_start'

    
    @api.one
    def _get_aktiv_tr(self, aktiv_aktiv_id, nomer):
        """Добавляет типовые работы"""

        n = 1
        for line in aktiv_aktiv_id.aktiv_type_id.aktiv_tr:
            nomer_txt = nomer + '.' + str(n)
            n += 1
            self.aktiv_gr_line.create({

                    "aktiv_gr_id": self.id,
                    "nomer": nomer_txt,
                    "aktiv_aktiv_id": aktiv_aktiv_id.id,
                    "aktiv_tr_id": line.id,

                })
            


    @api.one
    def _get_child_aktiv(self, paren_aktiv_id, nomer):
        """Возвращает потомков актива"""

        res = []
        n = 1
        for line in paren_aktiv_id.child_ids:
            nomer_txt = nomer + '.' + str(n)
            n += 1
            self.aktiv_gr_line.create({

                    "aktiv_gr_id": self.id,
                    "nomer": nomer_txt,
                    "aktiv_aktiv_id": line.id,
                    
                })
            self._get_aktiv_tr(line, nomer_txt)
            self._get_child_aktiv(line, nomer_txt)




    @api.one
    def action_zapolnit(self):
        """Действие при нажати на кнопку Заполнить"""
        nomer = 1
        self.aktiv_gr_line.unlink()
        self._get_aktiv_tr(self.aktiv_aktiv_id, str(nomer)) #Работы по основному объекту
        if self.aktiv_gr_line:
            self.aktiv_gr_line.create({

                    "aktiv_gr_id": self.id,
                    "nomer": str(nomer),
                    "aktiv_aktiv_id": self.aktiv_aktiv_id.id,
                   

                })
            nomer += 1
        for line in self.aktiv_aktiv_id.child_ids:
            nomer_txt = str(nomer)
                
            self.aktiv_gr_line.create({

                    "aktiv_gr_id": self.id,
                    "nomer": nomer_txt,
                    "aktiv_aktiv_id": line.id,
                   

                })
            self._get_aktiv_tr(line, str(nomer))
            self._get_child_aktiv(line, str(nomer))
            nomer += 1

        for line in self.aktiv_gr_line:
            line.return_name()

    @api.one
    def action_raschet(self):
        """Расчитать график"""
        for line in self.aktiv_gr_line:
            line.raschet()
      
    
    
    name = fields.Char(string=u"Наименование ремонта", required=True)
    year = fields.Integer(string=u"Год планирования", required=True)

    aktiv_aktiv_id = fields.Many2one('aktiv.aktiv', string='Актив')
    #is_view_price = fields.Boolean(string=u"Показать стоимость", default=False)

    date_start = fields.Date(string='Дата начала')
    date_end = fields.Date(string='Дата окончания')

    aktiv_gr_line = fields.One2many('aktiv.gr_line', 'aktiv_gr_id', string=u"Строка График ремонтов", copy=False)
    aktiv_gr_price_line = fields.One2many('aktiv.gr_line', 'aktiv_gr_id', copy=False)


class aktiv_gr_line(models.Model):
    """Строка График ремонтов"""
    _name = 'aktiv.gr_line'
    _description = u'Строка График ремонтов'
    _order  = 'nomer'

    @api.one
    def _get_price(self):
        self.amount = self.kol = 0
        self.currency_id = self.aktiv_tr_id.currency_id
        for m in range(1,13):
            self.amount += self['p'+str(m)]
            if self['m'+str(m)] == True:
                self.kol += 1


    @api.one
    def return_name(self):
        if self.aktiv_tr_id:
            self.name = self.aktiv_tr_id.name
        else:
            self.name = self.aktiv_aktiv_id.name

    @api.one
    def raschet(self):
        """Расчет графика ремонта для текущего типового ремонта"""
        if self.aktiv_tr_id:
            for m in range(1,13):
                self['m'+str(m)] = False
                self['p'+str(m)] = 0

            period = self.aktiv_tr_id.period1
            if self.aktiv_tr_id.period1_edizm == "months" and period > 0:
                #Если дата последнего ремонта определена то определяем месяц следующего ремонта
                #иначе планируем ремонт на первый месяц
                if self.date_last:
                    date_last = datetime.strptime(self.date_last, "%Y-%m-%d").date()
                    m_last = date_last.month
                    y_last = date_last.year
                    m_next = m_last
                    y_next = y_last
                    y_today = self.aktiv_gr_id.year
                    if y_last < y_today:
                        while (m_next<=12 and y_next<y_today):
                            m_next += period
                            if m_next>12:
                                y_next += 1
                                m_next = m_next - 12

                else:
                    m_next = 1

                while m_next<=12:
                    self['m'+str(m_next)] = True
                    self['p'+str(m_next)] = self.aktiv_tr_id.price
                    m_next += period
            self._get_price()

    # @api.one
    # @api.depends('aktiv_gr_id.is_view_price')
    # def _get_view_price(self):
    #     self.is_view_price = self.aktiv_gr_id.is_view_price
    
    name = fields.Char(string=u"Наименование ремонта", compute='return_name', store=True)
    year = fields.Integer(string=u"Год планирования", related='aktiv_gr_id.year', stote=True)
    nomer = fields.Char(string=u"№")
    aktiv_gr_id = fields.Many2one('aktiv.gr', ondelete='cascade', string=u"График ремонтов", required=True)

    # is_view_price = fields.Boolean(string=u"Показать стоимость", compute='_get_view_price')
    aktiv_aktiv_id = fields.Many2one('aktiv.aktiv', string='Актив')
    location_location_id = fields.Many2one('location.location', string='Место нахождение', related='aktiv_aktiv_id.location_location_id', stote=True)
    aktiv_remont_service_id = fields.Many2one('aktiv.remont_service', string='Ремонтная служба', related='aktiv_aktiv_id.aktiv_remont_service_id', stote=True)
    
    is_group = fields.Boolean(string=u"Это группа", related='aktiv_aktiv_id.is_group', stote=True)
    
    aktiv_tr_id = fields.Many2one('aktiv.tr', string='Типовые ремонты')
    
    date_last = fields.Date(string='Дата последнего ремонта')

    m1 = fields.Boolean(string=u"1", default=False)
    p1 = fields.Float(digits=(10, 2), string=u"1", compute='_get_price', store=True)

    m2 = fields.Boolean(string=u"2", default=False)
    p2 = fields.Float(digits=(10, 2), string=u"2", compute='_get_price', store=True)

    m3 = fields.Boolean(string=u"3", default=False)
    p3 = fields.Float(digits=(10, 2), string=u"3", compute='_get_price', store=True)

    m4 = fields.Boolean(string=u"4", default=False)
    p4 = fields.Float(digits=(10, 2), string=u"4", compute='_get_price', store=True)

    m5 = fields.Boolean(string=u"5", default=False)
    p5 = fields.Float(digits=(10, 2), string=u"5", compute='_get_price', store=True)

    m6 = fields.Boolean(string=u"6", default=False)
    p6 = fields.Float(digits=(10, 2), string=u"6", compute='_get_price', store=True)

    m7 = fields.Boolean(string=u"7", default=False)
    p7 = fields.Float(digits=(10, 2), string=u"7", compute='_get_price', store=True)

    m8 = fields.Boolean(string=u"8", default=False)
    p8 = fields.Float(digits=(10, 2), string=u"8", compute='_get_price', store=True)

    m9 = fields.Boolean(string=u"9", default=False)
    p9 = fields.Float(digits=(10, 2), string=u"9", compute='_get_price', store=True)

    m10 = fields.Boolean(string=u"10", default=False)
    p10 = fields.Float(digits=(10, 2), string=u"10", compute='_get_price', store=True)

    m11 = fields.Boolean(string=u"11", default=False)
    p11 = fields.Float(digits=(10, 2), string=u"11", compute='_get_price', store=True)
    
    m12 = fields.Boolean(string=u"12", default=False)
    p12 = fields.Float(digits=(10, 2), string=u"12", compute='_get_price', store=True)

    kol = fields.Float(digits=(10, 2), string=u"Кол-во", compute='_get_price', store=True)
    price = fields.Float(digits=(10, 2), string=u"Цена", compute='_get_price', store=True)
    currency_id = fields.Many2one('res.currency', string='Валюта', compute='_get_price', store=True)
    #currency_id = fields.Many2one('res.currency', string='Валюта', default=lambda self: self.env.user.company_id.currency_id.id)
    amount = fields.Float(digits=(10, 2), string=u"Стоимость", compute='_get_price', store=True)



class aktiv_remont(models.Model):
    """Ремонты"""
    _name = 'aktiv.remont'
    _description = u'Ремонты'
    _order  = 'date desc'

    @api.one
    @api.depends('aktiv_tr_id')
    def return_name(self):
        if self.is_graph:
            self.name = self.aktiv_tr_id.name
            self.aktiv_vid_remonta_id = self.aktiv_tr_id.aktiv_vid_remonta_id
        else:
            self.name = self.name_remonta

    @api.one
    def action_zapolnit(self):
        """Действие при нажати на кнопку Заполнить"""

        self.aktiv_remont_raboti_line.unlink()
        for line in self.aktiv_tr_id.aktiv_tr_raboti_line:
            self.aktiv_remont_raboti_line.create({
                        'aktiv_remont_id' : self.id,
                        'aktiv_vid_rabot_id' : line.aktiv_vid_rabot_id.id,
                        'price' : line.price,
                        'currency_id' : line.currency_id.id,
                        
                })
        
        self.aktiv_remont_nomen_line.unlink()
        for line in self.aktiv_tr_id.aktiv_tr_nomen_line:
            self.aktiv_remont_nomen_line.create({
                        'aktiv_remont_id' : self.id,
                        'nomen_nomen_id' : line.nomen_nomen_id.id,
                        'kol' : line.kol,
                        'price' : line.price,
                        'currency_id' : line.currency_id.id,
                        
                })


    @api.one
    @api.depends(   'is_raschet_price',
                    'price_raboti_r',
                    'aktiv_remont_raboti_line', 
                    'aktiv_remont_nomen_line',
                    )
    def _get_price(self):
        
        self.price = self.price_raboti = self.price_nomen = 0
        if self.is_raschet_price == True:
            self.price_raboti = self.price_raboti_r #Введенная в ручную
        else:
            for line in self.aktiv_remont_raboti_line:
                self.price_raboti += line.price

        if self.aktiv_remont_nomen_line:
            for line in self.aktiv_remont_nomen_line:
                self.price_nomen += line.amount
        self.price = self.price_raboti + self.price_nomen

    @api.one
    @api.depends(   'aktiv_tr_id',
                    'aktiv_vid_remonta_id_r',
                    'is_graph', 
                    )
    def _get_aktiv_vid_remonta(self):
        if self.is_graph:
            if self.aktiv_tr_id:
                self.aktiv_vid_remonta_id = self.aktiv_tr_id.aktiv_vid_remonta_id
        else:
            self.aktiv_vid_remonta_id = self.aktiv_vid_remonta_id_r

    @api.multi
    def action_draft(self):
        for doc in self:
            sklad_ostatok = self.env['sklad.ostatok']
            if (sklad_ostatok.reg_move_draft(doc)==True and 
                self.env['reg.rashod_kormov'].move(self, [], 'unlink')==True):
                self.state = 'draft'
        
               

        
    

    @api.multi
    def action_confirm(self):
                
        for doc in self:
            vals_sklad = []
            for line in doc.aktiv_remont_nomen_line:
                
                vals_sklad.append({
                                     'name': line.nomen_nomen_id.name, 
                                     'sklad_sklad_id': doc.sklad_sklad_id.id, 
                                     'nomen_nomen_id': line.nomen_nomen_id.id, 
                                     'kol': line.kol, 
                                    })

            sklad_ostatok = self.env['sklad.ostatok']
            if sklad_ostatok.reg_move(doc, vals_sklad, 'rashod')==True:
                doc.state = 'confirmed' 
            else:
                err = u'Ошибка при проведении'
                raise exceptions.ValidationError(_(u"Ошибка. Документ №%s Не проведен! %s" % (doc.name, err)))
                           

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.one
    def _get_name_obj(self):
        if self.obj_osnovaniya!='':
            obj = self.env[self.obj_osnovaniya].browse(self.obj_osnovaniya_id)
            self.obj_name = obj[0].name + u' от ' + obj[0].date
        else:
            self.obj_name = ''


    name = fields.Char(string=u"Наименование", compute='return_name', store=True)
    is_graph = fields.Boolean(string=u"По графику", default=False)
    name_remonta = fields.Char(string=u"Наименование ремонта")
    
    date = fields.Date(string='Дата ремонта', required=True)

    aktiv_aktiv_id = fields.Many2one('aktiv.aktiv', string='Актив', required=True)
    aktiv_type_id = fields.Many2one('aktiv.type', string='Тип актива', related='aktiv_aktiv_id.aktiv_type_id', store=True)
    aktiv_vid_remonta_id_r = fields.Many2one('aktiv.vid_remonta', string='Вид ремона и диагностирования') #Ручной ввод
    aktiv_vid_remonta_id = fields.Many2one('aktiv.vid_remonta', compute="_get_aktiv_vid_remonta", string='Вид ремона и диагностирования')
    probeg = fields.Integer(string="Пробег, км/ч или моточасов")

    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад материалов', required=False)
    

    otvetstvenniy_id = fields.Many2one('res.partner', string='Ответственный')
    ispolnitel_id = fields.Many2one('res.partner', string='Исполнитель')
    company_id = fields.Many2one('res.partner', string='Компания', default=lambda self: self.env.user.company_id.id)
    
    date_start = fields.Date(string='Дата начала')
    date_end = fields.Date(string='Дата окончания')

    aktiv_tr_id = fields.Many2one('aktiv.tr', string='Типовой ремонт')

    is_raschet_price = fields.Boolean(string=u"Стоимость работ задается в ручную", default=True)
    price_raboti_r = fields.Float(digits=(10, 2), string=u"Стоимость работ")
    price_raboti = fields.Float(digits=(10, 2), string=u"Стоимость работ", compute='_get_price', store=True)
    price_nomen = fields.Float(digits=(10, 2), string=u"Стоимость ТМЦ", compute='_get_price', store=True)
    price = fields.Float(digits=(10, 2), string=u"Общая стоимость", compute='_get_price', store=True)
    currency_id = fields.Many2one('res.currency', string='Валюта', default=lambda self: self.env.user.company_id.currency_id)
    is_hozsposob = fields.Boolean(string=u"Хозспособ", default=True)
    is_podryad = fields.Boolean(string=u"Подрядный", default=False)
    partner_id = fields.Many2one('res.partner', string='Подрядчик')

    period = fields.Integer(string="Время выполнения ремонта")
    period_edizm = fields.Selection([
        ('hours', "ч."),
        ('days', "дн."),
        
    ], default='hours', string="Ед.изм.")
    description = fields.Text(string=u"Коментарии")
    state = fields.Selection([
        ('create', "Создан"),
        ('draft', "Запланирован"),
        ('confirmed', "Выполнен"),
        ('done', "Отменен"),
        
    ], default='draft')

    obj_osnovaniya = fields.Char(string=u"Введен на основании объекта", copy=False, default='')
    obj_osnovaniya_id = fields.Integer(string=u"Id объекта основания", copy=False, default=0)
    obj_name = fields.Char(store=False, copy=False, compute='_get_name_obj')
    

    aktiv_remont_raboti_line = fields.One2many('aktiv.remont_raboti_line', 'aktiv_remont_id', string=u"Строка регламентных работ. Ремонты", copy=True)
    aktiv_remont_nomen_line = fields.One2many('aktiv.remont_nomen_line', 'aktiv_remont_id', string=u"Строка материалы. Ремонты", copy=True)
    



class aktiv_remont_raboti_line(models.Model):
    """Строка регламентных работ. Типовые ремонты"""
    _name = 'aktiv.remont_raboti_line'
    _description = u'Строка регламентных работ'
    _order  = 'name'


    @api.one
    @api.depends('aktiv_vid_rabot_id')
    def return_name(self):
        self.name = self.aktiv_vid_rabot_id.name


    name = fields.Char(string=u"Наименование", compute='return_name', store=True)
    aktiv_remont_id = fields.Many2one('aktiv.remont', ondelete='cascade', string=u"Ремонты", required=True)

    aktiv_vid_rabot_id = fields.Many2one('aktiv.vid_rabot', string='Виды работ', required=True)
 
    price = fields.Float(digits=(10, 2), string=u"Стоимость")
    currency_id = fields.Many2one('res.currency', string='Валюта', default=lambda self: self.env.user.company_id.currency_id)

    

class aktiv_remont_nomen_line(models.Model):
    """Строка материалы. Ремонты"""
    _name = 'aktiv.remont_nomen_line'
    _description = u'Строка материалы'
    _order  = 'name'

    @api.one
    @api.depends('nomen_nomen_id')
    def return_name(self):
        self.name = self.nomen_nomen_id.name


    @api.one
    @api.depends('nomen_nomen_id', 'kol')
    def _get_price(self):
        ost_price = self.env['sklad.ostatok_price']
        self.price = ost_price.get_price(self.nomen_nomen_id.id)
        self.amount = self.price * self.kol
  
    name = fields.Char(string=u"Наименование", compute='return_name', store=True)
    aktiv_remont_id = fields.Many2one('aktiv.remont', ondelete='cascade', string=u"Ремонты", required=True)

    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Материалы', required=True)
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", related='nomen_nomen_id.ed_izm_id', readonly=True,  store=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во", required=True)
    price = fields.Float(digits=(10, 2), string=u"Цена без НДС", compute='_get_price', store=True)
    currency_id = fields.Many2one('res.currency', string='Валюта', default=lambda self: self.nomen_nomen_id.currency_id)
    amount = fields.Float(digits=(10, 2), string=u"Стоимость", compute='_get_price', store=True)

    # aktiv_type_id = fields.Many2one('aktiv.type', string='Тип актива', related='aktiv_tr_id.aktiv_type_id', readonly=True,  store=True)
    # aktiv_vid_remonta_id = fields.Many2one('aktiv.vid_remonta', string='Виды ремонтов и диагностирования', related='aktiv_tr_id.aktiv_vid_remonta_id', readonly=True,  store=True)





class aktiv_plan_remont(models.Model):
    """План ремонтов"""
    _name = 'aktiv.plan_remont'
    _description = u'План ремонтов'
    _order  = 'year desc, month desc'

    @api.one
    @api.depends('month', 'year')
    def return_name(self):
        self.name = str(self.year) + '-'+str(self.month)
        self.date = datetime.strptime(self.year+'-'+self.month+'-01', "%Y-%m-%d").date()


    @api.one
    def action_zapolnit(self):
        """Заполнить строки плана в зависимости от выбранных параметров"""
        self.aktiv_plan_remont_line.unlink()
        month = int(self.month)

        if self.sel_zapolnit == 'service' and self.aktiv_remont_service_id:
            aktiv_gr_lines = self.aktiv_gr_id.aktiv_gr_line.search([
                ('aktiv_remont_service_id', 'child_of', self.aktiv_remont_service_id.id),
                ('m'+str(month), '=', True)
                ])

        
        if self.sel_zapolnit == 'aktiv' and self.aktiv_aktiv_id:
            aktiv_gr_lines = self.aktiv_gr_id.aktiv_gr_line.search([
                ('aktiv_aktiv_id', 'child_of', self.aktiv_aktiv_id.id),
                ('m'+str(month), '=', True)
                ])

        if self.sel_zapolnit == 'location' and self.location_location_id:
            aktiv_gr_lines = self.aktiv_gr_id.aktiv_gr_line.search([
                ('location_location_id', 'child_of', self.location_location_id.id),
                ('m'+str(month), '=', True)
                ])

        if self.sel_zapolnit == 'gr' and self.aktiv_gr_id:
            aktiv_gr_lines = self.aktiv_gr_id.aktiv_gr_line.search([
                ('aktiv_gr_id', '=', self.aktiv_gr_id.id),
                ('m'+str(month), '=', True)
                ])

        if aktiv_gr_lines:
            for aktiv_gr_line in aktiv_gr_lines:
                self.aktiv_plan_remont_line.create({
                        'aktiv_plan_remont_id' : self.id,
                        'aktiv_aktiv_id' : aktiv_gr_line.aktiv_aktiv_id.id,
                        'aktiv_tr_id' : aktiv_gr_line.aktiv_tr_id.id,
                        
                    })

    @api.one
    def action_raschet(self):
        for line in self.aktiv_plan_remont_line:
            line._get_date()


    @api.multi
    def action_draft(self):
        for doc in self:
            doc._unlink_remont()
        self.state = 'draft'
            

        
    

    @api.multi
    def action_confirm(self):
                
        for doc in self:
            for line in doc.aktiv_plan_remont_line:
                aktiv_remont_id = line.aktiv_remont_id.create({
                    'is_graph' : True,
                    'date' : line.date,
                    'aktiv_aktiv_id' : line.aktiv_aktiv_id.id,
                    'aktiv_tr_id' : line.aktiv_tr_id.id,
                    'obj_osnovaniya' : self.__class__.__name__,
                    'obj_osnovaniya_id' : doc.id,



                    })
                aktiv_remont_id.action_zapolnit()
                aktiv_remont_id.action_draft()
                line.aktiv_remont_id = aktiv_remont_id.id
                          
            self.state = 'confirmed'
            # else:
            #     err = u'Ошибка при проведении'
            #     raise exceptions.ValidationError(_(u"Ошибка. Документ №%s Не проведен! %s" % (doc.name, err)))
                        

    @api.multi
    def action_done(self):
        for doc in self:
            doc._unlink_remont()
        self.state = 'done'


    @api.one
    def _unlink_remont(self):
        for line in self.aktiv_plan_remont_line:
            line.aktiv_remont_id.unlink()

        

    name = fields.Char(string=u"Наименование", compute='return_name', store=True)

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
    ], default='', required=False, string=u"Месяц")

    year = fields.Char(string=u"Год", required=False, default=str(datetime.today().year))
    date = fields.Date(string='Дата', compute='return_name', store=True)

    sel_zapolnit = fields.Selection([
        ('service', u"Ремонтной службе"),
        ('aktiv', u"Активу"),
        ('location', u"Месторасположению"),
        ('gr', u"Графику ремонтов")
    ], default='service', string=u"Заполнить по")
    

    aktiv_remont_service_id = fields.Many2one('aktiv.remont_service', string=u"Ремонтная служба")

    aktiv_aktiv_id = fields.Many2one('aktiv.aktiv', string='Актив')
    aktiv_gr_id = fields.Many2one('aktiv.gr', string='График ремонтов')
    location_location_id = fields.Many2one('location.location', string='Местонахождение')
    
    description = fields.Text(string=u"Коментарии")
    state = fields.Selection([
        ('create', "Создан"),
        ('draft', "Черновик"),
        ('confirmed', "Запланировано"),
        ('done', "Отменен"),
        
    ], default='draft')

    aktiv_plan_remont_line = fields.One2many('aktiv.plan_remont_line', 'aktiv_plan_remont_id', string=u"Строка План ремонтов", copy=False)


class aktiv_plan_remont_line(models.Model):
    """Строка План ремонтов"""
    _name = 'aktiv.plan_remont_line'
    _description = u'Строка План ремонтов'
    _order  = 'name'
    

    @api.one
    @api.depends('aktiv_tr_id')
    def return_name(self):
        self.name = self.aktiv_tr_id.name

    @api.one
    @api.depends('aktiv_tr_id', 'aktiv_aktiv_id')
    def _get_date_last(self):
        if self.aktiv_tr_id and self.aktiv_aktiv_id:
            akriv_remont_last = self.env['aktiv.remont'].search([
                    ('aktiv_aktiv_id', '=', self.aktiv_aktiv_id.id),
                    ('aktiv_tr_id', '=', self.aktiv_tr_id.id),
                    ('date', '<=', self.aktiv_plan_remont_id.date),
                 ], order="date desc", limit=1)
            if akriv_remont_last:
                self.date_last = akriv_remont_last.date

    @api.one
    @api.onchange('aktiv_tr_id', 'aktiv_aktiv_id')
    def _get_date(self):
        if self.aktiv_tr_id and self.aktiv_aktiv_id:
            if self.date_last:
                if self.aktiv_tr_id.period1_edizm == 'months':
                    self.date = (datetime.strptime(self.date_last,'%Y-%m-%d') + relativedelta(months=int(self.aktiv_tr_id.period1))).strftime('%Y-%m-%d') 

    name = fields.Char(string=u"Наименование", compute='return_name', store=True)
    aktiv_plan_remont_id = fields.Many2one('aktiv.plan_remont', ondelete='cascade', string=u"План ремонтов", required=True)


    aktiv_aktiv_id = fields.Many2one('aktiv.aktiv', string='Актив', required=True)
    aktiv_type_id = fields.Many2one('aktiv.type', string='Тип актива', related='aktiv_aktiv_id.aktiv_type_id', store=True)
    aktiv_remont_id = fields.Many2one('aktiv.remont', string='Ремонт')
    
    aktiv_tr_id = fields.Many2one('aktiv.tr', string='Типовой ремонт')
    date_last = fields.Date(string='Дата предыдущего ремонта', compute='_get_date_last', store=True)
    date = fields.Date(string='Планируемая дата ремонта')

    price = fields.Float(digits=(10, 2), string=u"Общая стоимость", related='aktiv_tr_id.price', store=True)
    currency_id = fields.Many2one('res.currency', string='Валюта', related='aktiv_tr_id.currency_id', store=True)
    is_hozsposob = fields.Boolean(string=u"Хозспособ", related='aktiv_tr_id.is_hozsposob', store=True)
    is_podryad = fields.Boolean(string=u"Подрядный", related='aktiv_tr_id.is_podryad', store=True)
    partner_id = fields.Many2one('res.partner', string='Подрядчик', related='aktiv_tr_id.partner_id', store=True)
