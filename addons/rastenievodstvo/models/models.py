# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError



class rast_polya(models.Model):
    _name = 'rast.polya'
    _description = u'Справочник Поля'
    _order = 'name'

    
    name = fields.Char(string=u"Номер", required=True, copy=False, index=True, default='')
    date = fields.Date(string='Дата принятия')
    ploshad = fields.Float(digits=(10, 1), string=u"Прощадь, га", required=True)

    #Имя поля например Чекчук
    #Кадастровый номер
    #В собственности, аренда у администрации или у пайщиков кол-во пайов (доля, например 0,250)
    #га в собственности

    #Физические св-ва поля (Саланец, Черназем и т.п) меняются из года в год



  
class rast_rashod(models.Model):
    _name = 'rast.rashod'
    _description = u'Расход'
    _order = 'name'

    
    name = fields.Char(string=u"Номер", copy=False, index=True, default='')
    date = fields.Date(string='Дата')
    voditel = fields.Many2one('res.partner', string='Водитель')    
    pole = fields.Many2one('rast.polya', string='Поле')   
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True) 
    kol = fields.Float(digits=(10, 3), string=u"Кол-во", required=True)
    

    
       
    