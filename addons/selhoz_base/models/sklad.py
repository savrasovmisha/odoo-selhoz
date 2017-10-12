# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError

#----------------------------------------------------------
# Бухгалтерия
#----------------------------------------------------------

class buh_nomen_group(models.Model):
    _name = 'buh.nomen_group'
    _description = u'Номенклатурные группы (бух)'
    name = fields.Char(string=u"Наименование", required=True)
    id_1c = fields.Char(string=u"Номер в 1С")

class buh_stati_zatrat(models.Model):
    _name = 'buh.stati_zatrat'
    _description = u'Статьи затрат (бух)'
    name = fields.Char(string=u"Наименование", required=True)
    sorting = fields.Char(string=u"Сортировка")
    id_1c = fields.Char(string=u"Номер в 1С")





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
    _name = 'nomen.categ'
    _description = u'Категории номенклатуры'
    """Категории используются для вывода иерархического вида справочника"""
   
    name = fields.Char(string=u"Наименование", required=True)

class nomen_group(models.Model):
    _name = 'nomen.group'
    _description = u'Группы номенклатуры'
    """Группы используются для отнесения номенклатуры к типу номенклатуры"""
   
    name = fields.Char(string=u"Наименование", required=True) 
    sorting = fields.Integer(string=u"Порядок", required=True, default=100) 

class nomen_nomen(models.Model):
    _name = 'nomen.nomen'
    _description = u'Номенклатура'
    _order = 'name'

    name = fields.Char(string=u"Наименование", required=True)
    nomen_categ_id = fields.Many2one('nomen.categ', string=u"Категория", default=None)
    nomen_group_id = fields.Many2one('nomen.group', string=u"Группа", default=None)
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", default=None)
    nalog_nds_id = fields.Many2one('nalog.nds', string=u"Ставка НДС %", default=None)
    buh_nomen_group_id = fields.Many2one('buh.nomen_group', string='Номенклатурная группа (бух)')
    buh_stati_zatrat_id = fields.Many2one('buh.stati_zatrat', string='Статьи затрат')
    id_1c = fields.Char(string=u"Номер в 1С")
    active = fields.Boolean(string=u"Используется", default=True)

#----------------------------------------------------------
# Склад
#----------------------------------------------------------

class sklad_sklad(models.Model):
    _name = 'sklad.sklad'
    _description = u'Склады'
  
    name = fields.Char(string=u"Наименование", required=True) 
    partner_id = fields.Many2one('res.partner', string='Ответственный')
    id_1c = fields.Char(string=u"Номер в 1С")

    

#----------------------------------------------------------
# Договора
#----------------------------------------------------------
class dogovor(models.Model):
    _name = 'dogovor'
    _description = u'Договора'
  
    name = fields.Char(string=u"Номер", required=True) 
    partner_id = fields.Many2one('res.partner', string='Ответственный')
    date_start = fields.Date(string='Дата начала', required=True)
    date_end = fields.Date(string='Дата окончания', required=True)
    predmet = fields.Text(string=u"Предмет договора")
    amount = fields.Float(digits=(10, 2), string=u"Сумма договора") 
    id_1c = fields.Char(string=u"Номер в 1С")





class nalog_nds(models.Model):
    _name = 'nalog.nds'
    _description = u'Ставки НДС'

    name = fields.Char(string=u"Наименование", required=True)
    nds = fields.Float(digits=(10, 2), string=u"% НДС", required=True)