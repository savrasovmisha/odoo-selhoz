# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError



class rast_polya(models.Model):
    _name = 'rast.polya'
    _description = u'Справочник Поля'
    _order = 'name'



    @api.multi
    def write(self, vals):
        result = super(rast_polya, self).write(vals)

        #Если поле в собственности удаляем пайщиков
        if vals['is_sobst'] == True:
            self.rast_polya_pay_line.unlink()
        return result
    
    name = fields.Char(string=u"Номер", required=True, copy=False, index=True, default='')
    psevdonim = fields.Char(string=u"Псевдоним", copy=False, default='')
    date_start = fields.Date(string='Дата начала')
    date_end = fields.Date(string='Дата окончания')
    ploshad = fields.Float(digits=(10, 1), string=u"Прощадь, га", required=True)
    kad_nomer = fields.Char(string=u"Кадастровый номер", copy=False)
    is_sobst = fields.Boolean(string=u"В собственности", default=True)
    active = fields.Boolean(string=u"Используется", default=True)

    rast_polya_pay_line = fields.One2many('rast.polya_pay_line', 'rast_polya_id', string=u"Строка таблицы пайщиков")
    
    #Имя поля например Чекчук
    #Кадастровый номер
    #В собственности, аренда у администрации или у пайщиков кол-во пайов (доля, например 0,250)
    #га в собственности

    #Физические св-ва поля (Саланец, Черназем и т.п) меняются из года в год


class rast_polya_pay_line(models.Model):
    _name = 'rast.polya_pay_line'
    _description = u'Справочник Поля - пайщики'
    

    @api.one
    @api.depends('rast_polya_id.name')
    def return_name(self):
        self.name = self.rast_polya_id.name
    
    name = fields.Char(string=u"Номер", compute='return_name', index=True)
    date_start = fields.Date(string='Дата начала')
    date_end = fields.Date(string='Дата окончания')
    partner_id = fields.Many2one('res.partner', string='Пайщик', required=True)    
    dolya = fields.Float(digits=(10, 3), string=u"Доля, га", required=True)
    sequence = fields.Integer(string=u"Сорт.", help="Сортировка")
    rast_polya_id = fields.Many2one('rast.polya', ondelete='cascade', string=u"Справочник Поля", required=True)
    

  
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
    

    
       
    