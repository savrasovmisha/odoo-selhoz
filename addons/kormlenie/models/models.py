# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError


class korm_pit_standart(models.Model):
    _name = 'korm.pit_standart'
    _description = 'Питательность кормов по стандарту'
    _order = 'name'

    @api.one
    @api.depends('nomen_nomen_id')
    def return_name(self):
        self.name = self.nomen_nomen_id.name


    name = fields.Char(string="Наименование", required=True, compute='return_name', store=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Наименование корма', required=True)
    ov = fields.Float(digits=(10, 2), string="ОВ")
    sv = fields.Float(digits=(10, 2), string="СВ")
    oe = fields.Float(digits=(10, 2), string="ОЭ")
    sp = fields.Float(digits=(10, 2), string="СП")
    pp = fields.Float(digits=(10, 2), string="ПП")
    sk = fields.Float(digits=(10, 2), string="СК")
    sj = fields.Float(digits=(10, 2), string="СЖ")
    ca = fields.Float(digits=(10, 2), string="Ca")
    p = fields.Float(digits=(10, 2), string="P")
    sahar = fields.Float(digits=(10, 2), string="Сахар")
    krahmal = fields.Float(digits=(10, 2), string="Крахмал")
    bev = fields.Float(digits=(10, 2), string="БЭВ")
    magniy = fields.Float(digits=(10, 2), string="Магний")
    natriy = fields.Float(digits=(10, 2), string="Натрий")
    kaliy = fields.Float(digits=(10, 2), string="Калий")
    hlor = fields.Float(digits=(10, 2), string="Хлор")
    sera = fields.Float(digits=(10, 2), string="Сера")
    udp = fields.Float(digits=(10, 2), string="UDP")
    me = fields.Float(digits=(10, 2), string="ME")
    xp = fields.Float(digits=(10, 2), string="XP")
    nrp = fields.Float(digits=(10, 2), string="НРП")
    rnb = fields.Float(digits=(10, 2), string="RNB")
    nrp_p = fields.Float(digits=(10, 2), string="%НРП")


class stado_zagon(models.Model):
    _name = 'stado.zagon'
    _description = 'Загоны'
    _order = 'nomer'

    name = fields.Char(string="Наименование", required=True)
    nomer = fields.Integer(string="Номер", required=True)

