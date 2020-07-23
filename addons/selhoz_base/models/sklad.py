# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError




#----------------------------------------------------------
# Единицы измерения
#----------------------------------------------------------

class ed_izm_categ(models.Model):
    _name = 'nomen.ed_izm_categ'
    _description = u'Категории Единицы Измерения Номенклатуры'
    name = fields.Char(string=u"Наименование", required=True)


class ed_izm(models.Model):
    _name = 'nomen.ed_izm'
    _description = u'Единицы Измерения'
   
    name = fields.Char(string=u"Наименование", required=True)
    ed_izm_categ_id = fields.Many2one('nomen.ed_izm_categ', string=u"Категория ед.изм.", default=None)

#----------------------------------------------------------
# Номенклатура
#----------------------------------------------------------
class nomen_categ(models.Model):
    """Категории используются для вывода иерархического вида справочника"""
    _name = 'nomen.categ'
    _description = u'Категории номенклатуры'
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
        result = super(nomen_categ, self).create(vals)
        self.env['nomen.categ']._parent_store_compute()   
        self.env.cr.commit()
        return result


    name = fields.Char(string=u"Наименование", required=True) 
    complete_name = fields.Char(string=u"Наименование", compute='_complete_name', store=True) 
    parent_id = fields.Many2one('nomen.categ', string=u'Родительский элемент', index=True, ondelete='cascade')
    child_ids = fields.One2many('nomen.categ', 'parent_id', string=u'Подчиненные элементы')
    parent_left = fields.Integer('Left Parent', index=True)
    parent_right = fields.Integer('Right Parent', index=True)

class nomen_group(models.Model):
    _name = 'nomen.group'
    _description = u'Группы номенклатуры'
    """Группы используются для отнесения номенклатуры к типу номенклатуры"""
   
    name = fields.Char(string=u"Наименование", required=True) 
    sorting = fields.Integer(string=u"Порядок", required=True, default=100) 

class nomen_nomen(models.Model):
    _name = 'nomen.nomen'
    _description = u'Номенклатура'
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _order  = 'parent_left'

    @api.one
    def _get_ostatok(self):
        reg = self.env['sklad.ostatok_price']
        result = reg.search([ 
                                ('nomen_nomen_id', '=', self.id)                              
                            ], limit=1)
        if len(result)>0:
            self.ostatok = result.kol
            self.ostatok_amount = result.amount

    @api.one
    @api.depends('nomen_nomen_price_line')
    def _get_price(self):
        
        self.price = 0
        if self.nomen_nomen_price_line:
            self.price = self.nomen_nomen_price_line[0].price
            self.currency_id = self.nomen_nomen_price_line[0].currency_id
            self.partner_id = self.nomen_nomen_price_line[0].partner_id
        else:
            self.currency_id=self.env.user.company_id.currency_id

        
    name = fields.Char(string=u"Наименование", required=True)
    is_group = fields.Boolean(string=u"Это группа", default=False)
    nomen_categ_id = fields.Many2one('nomen.categ', string=u"Категория", default=None)
    nomen_group_id = fields.Many2one('nomen.group', string=u"Группа", default=None)
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", required=True)
    nalog_nds_id = fields.Many2one('nalog.nds', string=u"Ставка НДС %", default=None)
    buh_nomen_group_id = fields.Many2one('buh.nomen_group', string='Номенклатурная группа (бух)')
    buh_stati_zatrat_id = fields.Many2one('buh.stati_zatrat', string='Статьи затрат')
    id_1c = fields.Char(string=u"Номер в 1С")
    active = fields.Boolean(string=u"Используется", default=True)
    ostatok = fields.Float(digits=(10, 3), string=u"Кол-во", store=False, compute="_get_ostatok")
    ostatok_amount = fields.Float(digits=(10, 2), string=u"Стоимость остатков", store=False, compute="_get_ostatok")
    model = fields.Char(string=u"Модель")
    kod = fields.Char(string=u"Код")
    zavod_name = fields.Char(string=u"Завод производитель")
    country_id = fields.Many2one('res.country', string=u"Страна производитель")
    srok_slujbi = fields.Integer(string=u"Срок службы, лет")
    teh_har = fields.Text(string=u"Технические характеристики")
    price = fields.Float(digits=(10, 2), string=u"Цена с НДС", compute='_get_price', store=True)
    is_pokupaem = fields.Boolean(string=u"Покупаем", default=False)
    is_proizvodim = fields.Boolean(string=u"Производим", default=False)
    is_prodaem = fields.Boolean(string=u"Продаем", default=False)
    is_usluga = fields.Boolean(string=u"Это услуга", default=False)
    
    partner_id = fields.Many2one('res.partner', string='Поставщик', compute='_get_price', store=True)
    currency_id = fields.Many2one('res.currency', string='Валюта', compute='_get_price', store=True)
    description = fields.Text(string=u"Коментарии")

    parent_id = fields.Many2one('nomen.nomen', string=u'Родительский элемент', index=True, ondelete='cascade')
    child_ids = fields.One2many('nomen.nomen', 'parent_id', string=u'Подчиненные элементы')
    parent_left = fields.Integer('Left Parent', index=True)
    parent_right = fields.Integer('Right Parent', index=True)


    nomen_nomen_price_line = fields.One2many('nomen.nomen_price_line', 'nomen_nomen_id', string=u"Строка Закупочная стоимость Номенклатуры", copy=False)
    nomen_nomen_sklad_line = fields.One2many('nomen.nomen_sklad_line', 'nomen_nomen_id', string=u"Строка Основные места хранения Номенклатуры", copy=False)



class nomen_nomen_price_line(models.Model):
    """Строка Закупочная стоимость Номенклатуры"""
    _name = 'nomen.nomen_price_line'
    _description = u'Строка Закупочная стоимость Номенклатуры'
    _order  = 'date desc'
    
    @api.one
    @api.depends('date')
    def return_name(self):
        self.name = self.nomen_nomen_id.name
    
    name = fields.Char(string=u"Наименование", compute='return_name', store=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', ondelete='cascade', string=u"Номенклатура", required=True)

    date = fields.Date(string='Дата', required=True, index=True, copy=False)
    price = fields.Float(digits=(10, 2), string=u"Цена с НДС", required=True)
    currency_id = fields.Many2one('res.currency', string='Валюта', default=lambda self: self.env.user.company_id.currency_id.id)
    partner_id = fields.Many2one('res.partner', string='Поставщик', domain="[('company_type','=','company')]")


class nomen_nomen_sklad_line(models.Model):
    """Строка Основные места хранения Номенклатуры и минимальный остаток"""
    _name = 'nomen.nomen_sklad_line'
    _description = u'Строка Основные места хранения Номенклатуры'
    _order  = 'name desc'
    
    @api.one
    def return_name(self):
        self.name = self.sklad_sklad_id.name
        
    
    name = fields.Char(string=u"Наименование", compute='return_name', store=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', ondelete='cascade', string=u"Номенклатура", required=True)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', required=True)
    kol_min = fields.Float(digits=(10, 3), string=u"Мин. остаток", help=u"Минимальный остаток при достижении которого необходимо сделать заказ")
    


#----------------------------------------------------------
# Маста нахождения
#----------------------------------------------------------

class location_location(models.Model):
    _name = 'location.location'
    _description = u'Места нахождения'
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
        result = super(location_location, self).create(vals)
        return result


    name = fields.Char(string=u"Наименование", required=True) 
    complete_name = fields.Char(string=u"Наименование", compute='_complete_name', store=True) 
    
    parent_id = fields.Many2one('location.location', string=u'Родительский элемент', index=True, ondelete='cascade')
    child_ids = fields.One2many('location.location', 'parent_id', string=u'Подчиненные элементы')
    parent_left = fields.Integer('Left Parent', index=True)
    parent_right = fields.Integer('Right Parent', index=True)



#----------------------------------------------------------
# Склад
#----------------------------------------------------------

class sklad_sklad(models.Model):
    _name = 'sklad.sklad'
    _description = u'Склады'
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
        result = super(sklad_sklad, self).create(vals)
        self.env['sklad.sklad']._parent_store_compute()   
        self.env.cr.commit()
        return result


    name = fields.Char(string=u"Наименование", required=True) 
    complete_name = fields.Char(string=u"Наименование", compute='_complete_name', store=True) 
    partner_id = fields.Many2one('res.partner', string='Ответственный')
    id_1c = fields.Char(string=u"Номер в 1С")
    location_location_id = fields.Many2one('location.location', string='Местонахождение')
    parent_id = fields.Many2one('sklad.sklad', string=u'Родительский элемент', index=True, ondelete='cascade')
    child_ids = fields.One2many('sklad.sklad', 'parent_id', string=u'Подчиненные элементы')
    parent_left = fields.Integer('Left Parent', index=True)
    parent_right = fields.Integer('Right Parent', index=True)
    






