# -*- coding: utf-8 -*-

from __future__ import division #при делении будет возвращаться float
from openerp import models, fields, api, exceptions, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError

#----------------------------------------------------------
# Договора
#----------------------------------------------------------
class dogovor(models.Model):
    _name = 'dogovor'
    _order  = 'date'
    _description = u'Договора'
  
    name = fields.Char(string=u"Рег. номер", required=True) 
    nomer_partner = fields.Char(string=u"Рег. № контрагента") 
    partner_id = fields.Many2one('res.partner', string='Контрагент', required=True)
    otvetstvenniy_id = fields.Many2one('res.partner', string='Ответственный')
    date = fields.Date(string='Дата', required=True)
    date_start = fields.Date(string='Дата начала', required=True)
    date_end = fields.Date(string='Дата окончания')
    dogovor_vid_id = fields.Many2one('dogovor.vid', string='Вид договора', required=True)
    predmet = fields.Char(string=u"Предмет договора")
    amount = fields.Float(digits=(10, 2), string=u"Сумма договора") 
    currency_id = fields.Many2one('res.currency', string='Валюта', default=lambda self: self.env.user.company_id.currency_id)
    id_1c = fields.Char(string=u"Номер в 1С")
    attachment_ids = fields.Many2many(
        'ir.attachment', 'dogovor_ir_attachments_rel',
        'dogovor_id', 'attachment_id', string='Вложения')
    description = fields.Text(string=u"Коментарии")


class dogovor_vid(models.Model):
    _name = 'dogovor.vid'
    _order  = 'name'
    _description = u'Вид договора'
  
    name = fields.Char(string=u"Наименование", required=True) 