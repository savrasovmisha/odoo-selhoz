# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError

#----------------------------------------------------------
# Единицы измерения
#----------------------------------------------------------

class ed_izm_categ(models.Model):
    _name = 'nomen.ed_izm_categ'
    _description = 'Категории Единицы Измерения Номенклатуры'
    name = fields.Char(string="Наименование", required=True)


class ed_izm(models.Model):
    _name = 'nomen.ed_izm'
    _description = 'Единицы Измерения'
   
    name = fields.Char(string="Наименование", required=True)
    ed_izm_categ_id = fields.Many2one('nomen.ed_izm_categ', string="Категория ед.изм.", default=None)

#----------------------------------------------------------
# Номенклатура
#----------------------------------------------------------
class nomen_categ(models.Model):
    _name = 'nomen.categ'
    _description = 'Категории номенклатуры'
    """Категории используются для вывода иерархического вида справочника"""
   
    name = fields.Char(string="Наименование", required=True)

class nomen_group(models.Model):
    _name = 'nomen.group'
    _description = 'Группы номенклатуры'
    """Группы используются для отнесения номенклатуры к типу номенклатуры"""
   
    name = fields.Char(string="Наименование", required=True)  

class nomen_nomen(models.Model):
    _name = 'nomen.nomen'
    _description = 'Номенклатура'

    name = fields.Char(string="Наименование", required=True)
    nomen_categ_id = fields.Many2one('nomen.categ', string="Категория", default=None)
    nomen_group_id = fields.Many2one('nomen.group', string="Группа", default=None)
    ed_izm_id = fields.Many2one('nomen.ed_izm', string="Ед.изм.", default=None)
    id_1c = fields.Char(string="Номер в 1С")

#----------------------------------------------------------
# Склад
#----------------------------------------------------------

class sklad_sklad(models.Model):
    _name = 'sklad.sklad'
    _description = 'Склады'
  
    name = fields.Char(string="Наименование", required=True) 
    partner_id = fields.Many2one('res.partner', string='Ответственный')
    id_1c = fields.Char(string="Номер в 1С")


#----------------------------------------------------------
# Договора
#----------------------------------------------------------
class dogovor(models.Model):
    _name = 'dogovor'
    _description = 'Договора'
  
    name = fields.Char(string="Номер", required=True) 
    partner_id = fields.Many2one('res.partner', string='Ответственный')
    date_start = fields.Date(string='Дата начала', required=True)
    date_end = fields.Date(string='Дата окончания', required=True)
    predmet = fields.Text(string="Предмет договора")
    amount = fields.Float(digits=(10, 2), string="Сумма договора") 
    id_1c = fields.Char(string="Номер в 1С")

#----------------------------------------------------------
# Регистры остатков и оборотов
#----------------------------------------------------------
class sklad_ostatok(models.Model):
    _name = 'sklad.ostatok'
    _description = 'Договора'
  
    name = fields.Char(string="Номер", required=True)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад')
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура')
    kol = fields.Float(digits=(10, 3), string="Кол-во")

class sklad_oborot(models.Model):
    _name = 'sklad.oborot'
    _description = 'Договора'
  
    name = fields.Char(string="Номер", required=True)
    date = fields.Date(string='Дата', required=True)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад')
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура')
    kol = fields.Float(digits=(10, 3), string="Кол-во")