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