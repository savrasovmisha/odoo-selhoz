# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _
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
    _description = u'Остатки номенклатуры'
  
    name = fields.Char(string="Регистратор", required=True)
    date = fields.Datetime(string='Дата последнего изменения')
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True)
    kol = fields.Float(digits=(10, 3), string="Кол-во")

    # def zapis(self, vals, prihod, kol):
    #     """Если prihod=True тогда это поступление и будет прибавленно кол-во иначе вычтено"""
    #     if prihod == True:
    #         so = self.search([
    #             ('sklad_sklad_id', '=', self.sklad_sklad_id.id),
    #             ('nomen_nomen_id', '=', self.nomen_nomen_id.id),
    #             ])
    #         if len(so)>0:
    #             print 'kkkkkkkkkkkkkkkkkkkkkk'
    #             kol = so[0].kol


    #         else:
    #             print '=========================================='

    #             self.create(vals)

class sklad_ostatok_period(models.Model):
    _name = 'sklad.ostatok_period'
    _description = u'Остатки по периодам'
    """Регистр остатков по периодам, Если период равен 01.01.5000 то это тек. остатки."""
  
    name = fields.Char(string="Номер", default='ostatok_period')
    period = fields.Datetime(string='Период', required=True)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True)
    kol = fields.Float(digits=(10, 3), string="Кол-во")


class sklad_oborot(models.Model):
    _name = 'sklad.oborot'
    _description = u'Остатки номенклатуры. Движение'
  
    name = fields.Char(string="Регистратор", required=True)
    obj = fields.Char(string="Регистратор", required=True)
    obj_id = fields.Char(string="ID Регистратора", required=True)
    date = fields.Datetime(string='Дата')
    vid = fields.Float(digits=(1, 0), string="Вид движения")
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад')
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура')
    kol_oborot = fields.Float(digits=(10, 3), string="Кол-во оборот")
    kol_prihod = fields.Float(digits=(10, 3), string="Кол-во приход")
    kol_rashod = fields.Float(digits=(10, 3), string="Кол-во расход")



def reg_ostatok_move(obj,vals, vid_dvijeniya):


    print 'kkkkkkkkkkkkkkkkkkkkkk'
    ost = obj.env['sklad.ostatok']
    for line in vals:
        ost_nomen = ost.search([
            ('sklad_sklad_id', '=', line['sklad_sklad_id']),
            ('nomen_nomen_id', '=', line['nomen_nomen_id']),
            ])
        line['err'] = False
        line['id'] = False

        if len(ost_nomen)>0:
        
            line['id'] = ost_nomen[0].id
            kol_do = ost_nomen[0].kol
            if vid_dvijeniya == 'prihod' or vid_dvijeniya == 'rashod-draft':
                line['kol'] += kol_do
            if vid_dvijeniya == 'rashod' or vid_dvijeniya == 'prihod-draft':
                line['kol'] = kol_do - line['kol']
                if line['kol']<0:
                    line['err'] = True

        else:
            if (vid_dvijeniya == 'rashod' or vid_dvijeniya == 'prihod-draft') and line['kol']<0:
                line['err'] = True

        if line['err'] == True:
            raise exceptions.ValidationError(_(u"Ошибка. Документ №%s Не проведен!" % (obj.name)))
            return False


    for line in vals:
        if line['id'] == False:
            ost.create(line)
        else:
            ost.browse(line['id']).write(line)

    return True


            


        
             





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
            vals['state'] = 'draft'


        result = super(pokupka_pokupka, self).create(vals)
        return result

    @api.multi
    def unlink(self):
        
        print 'sssssssssssssssssssssssssssssssssssssssssssssss', self
        for pp in self:
            if pp.state != 'done':
                raise exceptions.ValidationError(_(u"Документ №%s Проведен и не может быть удален!" % (pp.name)))

        return super(pokupka_pokupka, self).unlink()


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
        ('create', "Создан"),
        ('draft', "Черновик"),
        ('confirmed', "Проведен"),
        ('done', "Отменен"),
        
    ], default='create')

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
        for doc in self:
            vals = []
            for line in doc.pokupka_pokupka_line:
                vals.append({
                             'name': line.nomen_nomen_id.name, 
                             'sklad_sklad_id': doc.sklad_sklad_id.id, 
                             'nomen_nomen_id': line.nomen_nomen_id.id, 
                             'kol': line.kol, 
                            })

                print "++++++++++++++++++++++++++++++++++++++++++++", doc.sklad_sklad_id.id
                
            if reg_ostatok_move(self, vals, 'rashod')==True:
                self.state = 'draft'

        
    

    @api.multi
    def action_confirm(self):
        #self.write({'state': 'confirmed'})
        
        for doc in self:
            vals = []
            for line in doc.pokupka_pokupka_line:
                vals.append({
                             'name': line.nomen_nomen_id.name, 
                             'sklad_sklad_id': doc.sklad_sklad_id.id, 
                             'nomen_nomen_id': line.nomen_nomen_id.id, 
                             'kol': line.kol, 
                            })

                print "++++++++++++++++++++++++++++++++++++++++++++", doc.sklad_sklad_id.id
                
            if reg_ostatok_move(self, vals, 'prihod')==True:
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
        if self.amount and self.kol>0:
            self.price = self.amount / self.kol
        else:
            raise exceptions.ValidationError(_(u"Количество должно быть больше нуля"))


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
    kol = fields.Float(digits=(10, 3), string="Кол-во", required=True)
    price = fields.Float(digits=(10, 2), string="Цена", readonly=False, compute='_amount',  store=True)
    amount = fields.Float(digits=(10, 2), string="Сумма", readonly=False, store=True, group_operator="sum")
    nalog_nds_id = fields.Many2one('nalog.nds',string="%НДС", readonly=False, compute='_nomen',  store=True)
    amount_bez_nds = fields.Float(digits=(10, 2), string="Сумма без НДС", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    amount_nds = fields.Float(digits=(10, 2), string="Сумма НДС", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    amount_total = fields.Float(digits=(10, 2), string="Всего", readonly=True, compute='_amount_all',  store=True, group_operator="sum")

    

class sklad_peremeshenie(models.Model):
    _name = 'sklad.peremeshenie'
    _description = u'Перемещение товаров'
    _order = 'date desc, id desc'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New' or vals.get('name', 'New') == None:
            vals['name'] = self.env['ir.sequence'].next_by_code('sklad.peremeshenie') or 'New'
            vals['state'] = 'draft'


        result = super(sklad_peremeshenie, self).create(vals)
        return result

    @api.multi
    def unlink(self):
        
        for sp in self:
            if sp.state != 'done':
                raise exceptions.ValidationError(_(u"Документ №%s Проведен и не может быть удален!" % (sp.name)))

        return super(sklad_peremeshenie, self).unlink()


    name = fields.Char(string="Номер", required=True, copy=False, index=True, default='New')
    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now)
    
    sklad_otp_id = fields.Many2one('sklad.sklad', string='Склад отправитель', required=True)
    sklad_pol_id = fields.Many2one('sklad.sklad', string='Склад получатель', required=True)
    sklad_peremeshenie_line = fields.One2many('sklad.peremeshenie_line', 'sklad_peremeshenie_id', string="Строка Перемещение товаров")
    
    state = fields.Selection([
        ('create', "Создан"),
        ('draft', "Черновик"),
        ('confirmed', "Проведен"),
        ('done', "Отменен"),
        
    ], default='create')

    
   
    @api.multi
    def action_draft(self):
        for doc in self:
            vals_otp = []
            vals_pol = []
            for line in doc.sklad_peremeshenie_line:
                vals_otp.append({
                             'name': line.nomen_nomen_id.name, 
                             'sklad_sklad_id': doc.sklad_otp_id.id, 
                             'nomen_nomen_id': line.nomen_nomen_id.id, 
                             'kol': line.kol, 
                            })
                vals_pol.append({
                             'name': line.nomen_nomen_id.name, 
                             'sklad_sklad_id': doc.sklad_pol_id.id, 
                             'nomen_nomen_id': line.nomen_nomen_id.id, 
                             'kol': line.kol, 
                            })

            if reg_ostatok_move(self, vals_otp, 'rashod-draft')==True and reg_ostatok_move(self, vals_pol, 'prihod-draft')==True:
                self.state = 'draft'

        
    

    @api.multi
    def action_confirm(self):
        #self.write({'state': 'confirmed'})
        
        for doc in self:
            vals_otp = []
            vals_pol = []
            for line in doc.sklad_peremeshenie_line:
                vals_otp.append({
                             'name': line.nomen_nomen_id.name, 
                             'sklad_sklad_id': doc.sklad_otp_id.id, 
                             'nomen_nomen_id': line.nomen_nomen_id.id, 
                             'kol': line.kol, 
                            })
                vals_pol.append({
                             'name': line.nomen_nomen_id.name, 
                             'sklad_sklad_id': doc.sklad_pol_id.id, 
                             'nomen_nomen_id': line.nomen_nomen_id.id, 
                             'kol': line.kol, 
                            })

            if reg_ostatok_move(self, vals_otp, 'rashod')==True and reg_ostatok_move(self, vals_pol, 'prihod')==True:
                self.state = 'confirmed'





    @api.multi
    def action_done(self):
        self.state = 'done'


class sklad_peremeshenie_line(models.Model):
    _name = 'sklad.peremeshenie_line'
    _description = u'Перемещение товаров строки'

    @api.one
    @api.depends('kol')
    def _amount(self):
        """
        Compute the total amounts.
        """
        if self.kol==0:
            raise exceptions.ValidationError(_(u"Количество должно быть больше нуля"))


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


    def return_name(self):
        self.name = self.sklad_peremeshenie_id.name

    name = fields.Char(string="Номер", required=True, compute='return_name')
    sklad_peremeshenie_id = fields.Many2one('sklad.peremeshenie', ondelete='cascade', string="Перемещение", required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True)
    ed_izm_id = fields.Many2one('nomen.ed_izm', string="Ед.изм.", required=True,  store=True)
    kol = fields.Float(digits=(10, 3), string="Кол-во", required=True)
   