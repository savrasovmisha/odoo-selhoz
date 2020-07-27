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

class nalog_nds(models.Model):
    _name = 'nalog.nds'
    _description = u'Ставки НДС'

    name = fields.Char(string=u"Наименование", required=True)
    nds = fields.Float(digits=(10, 2), string=u"% НДС", required=True)
    id_1c = fields.Char(string=u"Номер в 1С")


class buh_podrazdeleniya(models.Model):
    _name = 'buh.podrazdeleniya'
    _description = u'Подразделения (бух)'
    name = fields.Char(string=u"Наименование", required=True)
    sorting = fields.Char(string=u"Сортировка")
    id_1c = fields.Char(string=u"Номер в 1С")