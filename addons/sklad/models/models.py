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
    nalog_nds_id = fields.Many2one('nalog.nds', string="Ставка НДС %", default=None)
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
    _description = u'Договора'
  
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
    _description = u'Договора'
  
    name = fields.Char(string="Номер", required=True)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад')
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура')
    kol = fields.Float(digits=(10, 3), string="Кол-во")

    def zapis(self, doc):
        self.sklad_sklad_id = doc.sklad_sklad_id

class sklad_oborot(models.Model):
    _name = 'sklad.oborot'
    _description = u'Договора'
  
    name = fields.Char(string="Регистратор", required=True)
    obj = fields.Char(string="Объект", required=True)
    obj_id = fields.Integer(string="ID Объекта", required=True)
    date = fields.Date(string='Дата', required=True)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад')
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура')
    kol = fields.Float(digits=(10, 3), string="Кол-во")

#----------------------------------------------------------
# Документы прихода/расхода
#----------------------------------------------------------
class nalog_nds(models.Model):
    _name = 'nalog.nds'
    _description = u'Ставки НДС'

    name = fields.Char(string="Наименование", required=True)
    nds = fields.Float(digits=(10, 2), string="% НДС", required=True)

class pokupka_pokupka(models.Model):
    _name = 'pokupka.pokupka'
    _description = u'Поступление товаров'
    _order = 'date desc, id desc'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New' or vals.get('name', 'New') == None:
            vals['name'] = self.env['ir.sequence'].next_by_code('pokupka.pokupka') or 'New'

        result = super(pokupka_pokupka, self).create(vals)
        return result

    # @api.model
    # def write(self, vals, context=None):
    #     print 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
    #     return True

    name = fields.Char(string="Номер", required=True, copy=False, index=True, default='New')
    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now)
    partner_id = fields.Many2one('res.partner', string='Контрагент', required=True)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', required=True)
    pokupka_pokupka_line = fields.One2many('pokupka.pokupka_line', 'pokupka_pokupka_id', string="Строка Поступление товаров")
    nds_price = fields.Boolean(string="Цена включает НДС")
    amount_bez_nds = fields.Float(digits=(10, 2), string="Сумма без НДС", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    amount_nds = fields.Float(digits=(10, 2), string="Сумма НДС", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    amount_total = fields.Float(digits=(10, 2), string="Всего", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    proveden = fields.Boolean(string="Проводен")
    state = fields.Selection([
        ('draft', "Создан"),
        ('confirmed', "Проведен"),
        
    ], default='draft')

    @api.one
    @api.depends('pokupka_pokupka_line.kol','pokupka_pokupka_line.price',
                 'pokupka_pokupka_line.amount','pokupka_pokupka_line.nalog_nds_id')
    def _amount_all(self):
        """
        Compute the total amounts.
        """
        self.amount_bez_nds=self.amount_nds = 0

        for line in self.pokupka_pokupka_line:
            self.amount_nds += line.amount_nds
            self.amount_total += line.amount_total
        self.amount_bez_nds = self.amount_total - self.amount_nds

    @api.multi
    def action_draft(self):
        self.state = 'draft'
        print 'rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr'
    

    @api.multi
    def action_confirm(self):
        print 'rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr'
        self.write({'state': 'confirmed'})
        self.state = 'confirmed'


    @api.multi
    def action_done(self):
        self.state = 'done'


class pokupka_pokupka_line(models.Model):
    _name = 'pokupka.pokupka_line'
    _description = u'Поступление товаров строки'


    @api.one
    @api.depends('nomen_nomen_id','kol','price','amount','nalog_nds_id')
    def _amount_all(self):
        """
        Compute the total amounts.
        """
        if self.nalog_nds_id and self.kol>0 and self.price>0:
            
            if self.pokupka_pokupka_id.nds_price == True:
                self.amount_nds = self.amount * self.nalog_nds_id.nds/(100 + self.nalog_nds_id.nds)
                self.amount_total = self.amount
            else:
                self.amount_nds = self.amount * self.nalog_nds_id.nds/100
                self.amount_total = self.amount + self.amount_nds
            self.amount_bez_nds = self.amount_total - self.amount_nds


    @api.one
    @api.depends('kol','price','amount','nalog_nds_id')
    def _amount(self):
        """
        Compute the total amounts.
        """
        if self.amount or self.kol:
            self.price = self.amount / self.kol

    @api.one
    @api.depends('nomen_nomen_id')
    def _nomen(self):
        """
        Compute the total amounts.
        """
          
        if self.nomen_nomen_id:
            # func_model = self.env['nomen.ed_izm']
            # function = func_model.search([('name', '=', self.nomen_nomen_id.ed_izm_id.name)]).id
            self.ed_izm_id = self.nomen_nomen_id.ed_izm_id
            self.nalog_nds_id = self.nomen_nomen_id.nalog_nds_id

    def return_name(self):
        self.name = self.pokupka_pokupka_id.name

    name = fields.Char(string="Номер", required=True, compute='return_name')
    pokupka_pokupka_id = fields.Many2one('pokupka.pokupka', ondelete='cascade', string="Поступление", required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True)
    ed_izm_id = fields.Many2one('nomen.ed_izm', string="Ед.изм.", required=True,  store=True)
    kol = fields.Float(digits=(10, 3), string="Кол-во")
    price = fields.Float(digits=(10, 2), string="Цена", readonly=False, compute='_amount',  store=True)
    amount = fields.Float(digits=(10, 2), string="Сумма", readonly=False, store=True, group_operator="sum")
    nalog_nds_id = fields.Many2one('nalog.nds',string="%НДС", readonly=False, compute='_nomen',  store=True)
    amount_bez_nds = fields.Float(digits=(10, 2), string="Сумма без НДС", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    amount_nds = fields.Float(digits=(10, 2), string="Сумма НДС", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    amount_total = fields.Float(digits=(10, 2), string="Всего", readonly=True, compute='_amount_all',  store=True, group_operator="sum")

    

