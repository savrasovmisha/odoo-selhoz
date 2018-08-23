# -*- coding: utf-8 -*-

from __future__ import division #при делении будет возвращаться float
from openerp import models, fields, api, exceptions, _
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError


#----------------------------------------------------------
# Активы предприятия
#----------------------------------------------------------
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




class aktiv_type(models.Model):
    """Типы активов (Оборудование, транспорт и т.п"""
    _name = 'aktiv.type'
    _description = u'Типы активов'
    _order  = 'name'
  
    name = fields.Char(string=u"Наименование", required=True) 


class aktiv_status(models.Model):
    """Статус активов (В работе, в ремонте и т.п"""
    _name = 'aktiv.status'
    _description = u'Статусы активов'
    _order  = 'name'
  
    name = fields.Char(string=u"Наименование", required=True) 





class aktiv_aktiv(models.Model):
    """Активы предприятия. ОС."""
    _name = 'aktiv.aktiv'
    _description = u'Активы (оборудование)'
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
   

        

    name = fields.Char(string=u"Наименование", required=True)
    complete_name = fields.Char(string=u"Наименование", compute='_complete_name', store=True) 
    parent_id = fields.Many2one('aktiv.aktiv', string=u'Родительский элемент', index=True, ondelete='cascade')
    child_ids = fields.One2many('aktiv.aktiv', 'parent_id', string=u'Подчиненные элементы')
    parent_left = fields.Integer('Left Parent', index=True)
    parent_right = fields.Integer('Right Parent', index=True)
    
    aktiv_categ_id = fields.Many2one('aktiv.categ', string=u"Категория", default=None)
    id_1c = fields.Char(string=u"Номер в 1С")
    active = fields.Boolean(string=u"Используется", default=True)
    is_uzel = fields.Boolean(string=u"Узел объекта", default=True)

    model = fields.Char(string=u"Модель")
    kod = fields.Char(string=u"Код")
    
    inv_nomer = fields.Char(string=u"Инвентарный номер")
    serial_nomer = fields.Char(string=u"Серийный номер")
    reg_nomer = fields.Char(string=u"Регистрационный номер")
    
    zavod_nomer = fields.Char(string=u"Заводской номер")
    zavod_name = fields.Char(string=u"Завод производитель")
    country_id = fields.Many2one('res.country', string=u"Страна производитель")

    postavshik_id = fields.Many2one('res.partner', string='Поставщик')
    otvetstvenniy_id = fields.Many2one('res.partner', string='Ответственный')
    aktiv_type_id = fields.Many2one('aktiv.type', string='Тип')



    date_vipuska = fields.Date(string='Дата выпуска')
    date_postupleniya = fields.Date(string='Дата поступления')
    date_vvoda = fields.Date(string='Дата ввода в экспл.')
    date_spisaniya = fields.Date(string='Дата списания')

    aktiv_status_id = fields.Many2one('aktiv.status', string='Статус')

    price = fields.Integer(string=u"Стоимость")
    srok_slujbi = fields.Integer(string=u"Срок службы, лет")
    srok_slujbi_ot_vvoda = fields.Boolean(string=u"Срок службы от ввода в эксплуатацию", default=True)
    date_start = fields.Date(string='Срок службы, Дата начала', compute='_srok_slujbi', store=True)
    date_end = fields.Date(string='Срок службы, Дата окончания', compute='_srok_slujbi', store=True)

    teh_har = fields.Text(string=u"Технические характеристики")

    description = fields.Text(string=u"Коментарии")
    
