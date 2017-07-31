# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError

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

class nomen_nomen(models.Model):
    _name = 'nomen.nomen'
    _description = u'Номенклатура'
    _order = 'name'

    name = fields.Char(string=u"Наименование", required=True)
    nomen_categ_id = fields.Many2one('nomen.categ', string=u"Категория", default=None)
    nomen_group_id = fields.Many2one('nomen.group', string=u"Группа", default=None)
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", default=None)
    nalog_nds_id = fields.Many2one('nalog.nds', string=u"Ставка НДС %", default=None)
    id_1c = fields.Char(string=u"Номер в 1С")

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

#----------------------------------------------------------
# Регистры остатков и оборотов
#----------------------------------------------------------
class sklad_ostatok(models.Model):
    _name = 'sklad.ostatok'
    _description = u'Остатки номенклатуры'
  
    name = fields.Char(string=u"Регистратор", required=True)
    date = fields.Datetime(string='Дата последнего изменения')
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во")

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
  
    name = fields.Char(string=u"Номер", default='ostatok_period')
    period = fields.Datetime(string='Период', required=True)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во")


class sklad_oborot(models.Model):
    _name = 'sklad.oborot'
    _description = u'Остатки номенклатуры. Движение'
  
    name = fields.Char(string=u"Регистратор", required=True)
    obj = fields.Char(string=u"Регистратор", required=True)
    obj_id = fields.Integer(string=u"ID Регистратора", required=True)
    date = fields.Datetime(string='Дата', required=True)
    vid = fields.Char(string=u"Вид движения", required=True)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True)
    kol_oborot = fields.Float(digits=(10, 3), string=u"Кол-во оборот")
    kol_prihod = fields.Float(digits=(10, 3), string=u"Кол-во приход")
    kol_rashod = fields.Float(digits=(10, 3), string=u"Кол-во расход")



def reg_ostatok_move(obj,vals, vid_dvijeniya):
    """
        Ф-я осуществляет запись в таблицу остатков и оборотов товаров по складам
    """

    message = ''
    
    if len(vals) == 0:
        message = u"Нет данных для проведения документа. Не заполненна табличная часть"
        raise exceptions.ValidationError(_(u"Ошибка. Документ №%s Не проведен! %s" % (obj.name, message)))
        return False

    ost = obj.env['sklad.ostatok']
    for line in vals:
        ost_nomen = ost.search([
            ('sklad_sklad_id', '=', line['sklad_sklad_id']),
            ('nomen_nomen_id', '=', line['nomen_nomen_id']),
            ])
        line['err'] = False
        line['id'] = False
        line['obj'] = obj.__class__.__name__
        line['obj_id'] = obj.id
        line['date'] = obj.date
        line['vid'] = vid_dvijeniya
        if vid_dvijeniya == 'prihod':
            line['kol_prihod'] = line['kol']
            line['kol_oborot'] = line['kol']
        if vid_dvijeniya == 'rashod':
            line['kol_rashod'] = line['kol']
            line['kol_oborot'] = -1*line['kol']

        if line['kol']<=0:
            line['err'] = True
            message = u"Кол-во должно быть больше нуля"

        print line
        if len(ost_nomen)>0:
        
            line['id'] = ost_nomen[0].id
            kol_do = ost_nomen[0].kol
            if vid_dvijeniya == 'prihod' or vid_dvijeniya == 'rashod-draft':
                line['kol'] += kol_do
            if vid_dvijeniya == 'rashod' or vid_dvijeniya == 'prihod-draft':
                line['kol'] = kol_do - line['kol']
                

        if (vid_dvijeniya == 'rashod' or vid_dvijeniya == 'prihod-draft') and line['kol']<0:
                line['err'] = True
                message = u'Невозможно списать %s. Требуется %s, на остатке %s' % (line['kol'], line['kol_oborot'], kol_do)

        if line['err'] == True:
            raise exceptions.ValidationError(_(u"Ошибка. Документ №%s Не проведен! %s" % (obj.name, message)))
            return False


    for line in vals:
        if line['id'] == False:
            ost.create(line)
        else:
            ost.browse(line['id']).write(line)

    #Движения по Регистру остатки - обороты
    obr = obj.env['sklad.oborot']
    if vid_dvijeniya == 'prihod' or vid_dvijeniya == 'rashod':
        for line in vals:
            obr.create(line)
    else:

        ids_del = obr.search([  ('obj_id', '=', obj.id),
                                ('obj', '=', obj.__class__.__name__),
                                ])
        ids_del.unlink()

    

    return True


            


        
             





#----------------------------------------------------------
# Документы прихода/расхода
#----------------------------------------------------------
class nalog_nds(models.Model):
    _name = 'nalog.nds'
    _description = u'Ставки НДС'

    name = fields.Char(string=u"Наименование", required=True)
    nds = fields.Float(digits=(10, 2), string=u"% НДС", required=True)


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


    name = fields.Char(string=u"Номер", required=True, copy=False, index=True, default='New')
    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now)
    partner_id = fields.Many2one('res.partner', string='Контрагент', required=True)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', required=True)
    pokupka_pokupka_line = fields.One2many('pokupka.pokupka_line', 'pokupka_pokupka_id', string=u"Строка Поступление товаров")
    nds_price = fields.Boolean(string=u"Цена включает НДС")
    amount_bez_nds = fields.Float(digits=(10, 2), string=u"Сумма без НДС", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    amount_nds = fields.Float(digits=(10, 2), string=u"Сумма НДС", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    amount_total = fields.Float(digits=(10, 2), string=u"Всего", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    proveden = fields.Boolean(string=u"Проводен")
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
                
            if reg_ostatok_move(self, vals, 'prihod-draft')==True:
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

    name = fields.Char(string=u"Номер", required=True, compute='return_name')
    pokupka_pokupka_id = fields.Many2one('pokupka.pokupka', ondelete='cascade', string=u"Поступление", required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True)
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", compute='_nomen',  store=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во", required=True)
    price = fields.Float(digits=(10, 2), string=u"Цена", readonly=False, compute='_amount',  store=True)
    amount = fields.Float(digits=(10, 2), string=u"Сумма", readonly=False, store=True, group_operator="sum")
    nalog_nds_id = fields.Many2one('nalog.nds',string=u"%НДС", readonly=False, compute='_nomen',  store=True)
    amount_bez_nds = fields.Float(digits=(10, 2), string=u"Сумма без НДС", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    amount_nds = fields.Float(digits=(10, 2), string=u"Сумма НДС", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    amount_total = fields.Float(digits=(10, 2), string=u"Всего", readonly=True, compute='_amount_all',  store=True, group_operator="sum")

    

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


    name = fields.Char(string=u"Номер", required=True, copy=False, index=True, default='New')
    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now)
    
    sklad_otp_id = fields.Many2one('sklad.sklad', string='Склад отправитель', required=True)
    sklad_pol_id = fields.Many2one('sklad.sklad', string='Склад получатель', required=True)
    sklad_peremeshenie_line = fields.One2many('sklad.peremeshenie_line', 'sklad_peremeshenie_id', string=u"Строка Перемещение товаров")
    
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
    @api.depends('nomen_nomen_id')
    def _nomen(self):
        """
        Compute the total amounts.
        """
        print "---------------------**********************"  
        if self.nomen_nomen_id:
            # func_model = self.env['nomen.ed_izm']
            # function = func_model.search([('name', '=', self.nomen_nomen_id.ed_izm_id.name)]).id
            self.ed_izm_id = self.nomen_nomen_id.ed_izm_id
            #self.nalog_nds_id = self.nomen_nomen_id.nalog_nds_id

    @api.one
    @api.depends('nomen_nomen_id')
    def _nomen(self):
        """
        Compute the total amounts.
        """
          
        if self.nomen_nomen_id:
            self.ed_izm_id = self.nomen_nomen_id.ed_izm_id
            

    def return_name(self):
        self.name = self.sklad_peremeshenie_id.name

    name = fields.Char(string=u"Номер", required=True, compute='return_name')
    sklad_peremeshenie_id = fields.Many2one('sklad.peremeshenie', ondelete='cascade', string=u"Перемещение", required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True)
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", compute='_nomen',  store=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во", required=True)
 
   


class prodaja_prodaja(models.Model):
    _name = 'prodaja.prodaja'
    _description = u'Реализация товаров'
    _order = 'date desc, id desc'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New' or vals.get('name', 'New') == None:
            vals['name'] = self.env['ir.sequence'].next_by_code('prodaja.prodaja') or 'New'
            vals['state'] = 'draft'


        result = super(prodaja_prodaja, self).create(vals)
        return result

    @api.multi
    def unlink(self):
        
        print 'sssssssssssssssssssssssssssssssssssssssssssssss', self
        for pp in self:
            if pp.state != 'done':
                raise exceptions.ValidationError(_(u"Документ №%s Проведен и не может быть удален!" % (pp.name)))

        return super(prodaja_prodaja, self).unlink()


    name = fields.Char(string=u"Номер", required=True, copy=False, index=True, default='New')
    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now)
    partner_id = fields.Many2one('res.partner', string='Контрагент', required=True)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', required=True)
    prodaja_prodaja_line = fields.One2many('prodaja.prodaja_line', 'prodaja_prodaja_id', string=u"Строка Реализации товаров")
    nds_price = fields.Boolean(string=u"Цена включает НДС")
    amount_bez_nds = fields.Float(digits=(10, 2), string=u"Сумма без НДС", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    amount_nds = fields.Float(digits=(10, 2), string=u"Сумма НДС", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    amount_total = fields.Float(digits=(10, 2), string=u"Всего", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    proveden = fields.Boolean(string=u"Проводен")
    state = fields.Selection([
        ('create', "Создан"),
        ('draft', "Черновик"),
        ('confirmed', "Проведен"),
        ('done', "Отменен"),
        
    ], default='create')

    @api.one
    @api.depends('prodaja_prodaja_line.kol','prodaja_prodaja_line.price',
                 'prodaja_prodaja_line.amount','prodaja_prodaja_line.nalog_nds_id')
    def _amount_all(self):
        """
        Compute the total amounts.
        """
        self.amount_bez_nds=self.amount_nds = 0

        for line in self.prodaja_prodaja_line:
            self.amount_nds += line.amount_nds
            self.amount_total += line.amount_total
        self.amount_bez_nds = self.amount_total - self.amount_nds

   
    @api.multi
    def action_draft(self):
        for doc in self:
            vals = []
            for line in doc.prodaja_prodaja_line:
                vals.append({
                             'name': line.nomen_nomen_id.name, 
                             'sklad_sklad_id': doc.sklad_sklad_id.id, 
                             'nomen_nomen_id': line.nomen_nomen_id.id, 
                             'kol': line.kol, 
                            })

                print "++++++++++++++++++++++++++++++++++++++++++++", doc.sklad_sklad_id.id
                
            if reg_ostatok_move(self, vals, 'rashod-draft')==True:
                self.state = 'draft'

        
    

    @api.multi
    def action_confirm(self):
        #self.write({'state': 'confirmed'})
        
        for doc in self:
            vals = []
            for line in doc.prodaja_prodaja_line:
                vals.append({
                             'name': line.nomen_nomen_id.name, 
                             'sklad_sklad_id': doc.sklad_sklad_id.id, 
                             'nomen_nomen_id': line.nomen_nomen_id.id, 
                             'kol': line.kol, 
                            })

                print "++++++++++++++++++++++++++++++++++++++++++++", doc.sklad_sklad_id.id
                
            if reg_ostatok_move(self, vals, 'rashod')==True:
                self.state = 'confirmed'





    @api.multi
    def action_done(self):
        self.state = 'done'


class prodaja_prodaja_line(models.Model):
    _name = 'prodaja.prodaja_line'
    _description = u'Реализация товаров строки'

    
    @api.one
    @api.depends('nomen_nomen_id','kol','price','amount','nalog_nds_id')
    def _amount_all(self):
        """
        Compute the total amounts.
        """
        if self.nalog_nds_id and self.kol>0 and self.price>0:
            
            if self.prodaja_prodaja_id.nds_price == True:
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
        

    @api.one
    @api.depends('nomen_nomen_id')
    def _nomen(self):
        """
        Compute the total amounts.
        """
        print "---------------------**********************"  
        if self.nomen_nomen_id:
            # func_model = self.env['nomen.ed_izm']
            # function = func_model.search([('name', '=', self.nomen_nomen_id.ed_izm_id.name)]).id
            self.ed_izm_id = self.nomen_nomen_id.ed_izm_id
            self.nalog_nds_id = self.nomen_nomen_id.nalog_nds_id

    def return_name(self):
        self.name = self.prodaja_prodaja_id.name

    name = fields.Char(string=u"Номер", required=True, compute='return_name')
    prodaja_prodaja_id = fields.Many2one('prodaja.prodaja', ondelete='cascade', string=u"Реализация", required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True)
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", compute='_nomen',  store=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во", required=True)
    price = fields.Float(digits=(10, 2), string=u"Цена", readonly=False, compute='_amount',  store=True)
    amount = fields.Float(digits=(10, 2), string=u"Сумма", readonly=False, store=True, group_operator="sum")
    nalog_nds_id = fields.Many2one('nalog.nds',string=u"%НДС", readonly=False, compute='_nomen',  store=True)
    amount_bez_nds = fields.Float(digits=(10, 2), string=u"Сумма без НДС", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    amount_nds = fields.Float(digits=(10, 2), string=u"Сумма НДС", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    amount_total = fields.Float(digits=(10, 2), string=u"Всего", readonly=True, compute='_amount_all',  store=True, group_operator="sum")


class sklad_spisanie(models.Model):
    _name = 'sklad.spisanie'
    _description = u'Списание товаров'
    _order = 'date desc, id desc'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New' or vals.get('name', 'New') == None:
            vals['name'] = self.env['ir.sequence'].next_by_code('sklad.spisanie') or 'New'
            vals['state'] = 'draft'


        result = super(sklad_spisanie, self).create(vals)
        return result

    @api.multi
    def unlink(self):
        
        #print 'sssssssssssssssssssssssssssssssssssssssssssssss', self
        for pp in self:
            if pp.state != 'done':
                raise exceptions.ValidationError(_(u"Документ №%s Проведен и не может быть удален!" % (pp.name)))

        return super(sklad_spisanie, self).unlink()


    name = fields.Char(string=u"Номер", required=True, copy=False, index=True, default='New')
    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', required=True)
    sklad_spisanie_line = fields.One2many('sklad.spisanie_line', 'sklad_spisanie_id', string=u"Строка Списание товаров")
    proveden = fields.Boolean(string=u"Проводен")
    state = fields.Selection([
        ('create', "Создан"),
        ('draft', "Черновик"),
        ('confirmed', "Проведен"),
        ('done', "Отменен"),
        
    ], default='create')

       
    @api.multi
    def action_draft(self):
        for doc in self:
            vals = []
            for line in doc.sklad_spisanie_line:
                vals.append({
                             'name': line.nomen_nomen_id.name, 
                             'sklad_sklad_id': doc.sklad_sklad_id.id, 
                             'nomen_nomen_id': line.nomen_nomen_id.id, 
                             'kol': line.kol, 
                            })

                #print "++++++++++++++++++++++++++++++++++++++++++++", doc.sklad_sklad_id.id
                
            if reg_ostatok_move(self, vals, 'rashod-draft')==True:
                self.state = 'draft'

        
    

    @api.multi
    def action_confirm(self):
        #self.write({'state': 'confirmed'})
        
        for doc in self:
            vals = []
            for line in doc.sklad_spisanie_line:
                vals.append({
                             'name': line.nomen_nomen_id.name, 
                             'sklad_sklad_id': doc.sklad_sklad_id.id, 
                             'nomen_nomen_id': line.nomen_nomen_id.id, 
                             'kol': line.kol, 
                            })

                #print "++++++++++++++++++++++++++++++++++++++++++++", doc.sklad_sklad_id.id
                
            if reg_ostatok_move(self, vals, 'rashod')==True:
                self.state = 'confirmed'





    @api.multi
    def action_done(self):
        self.state = 'done'


class sklad_spisanie_line(models.Model):
    _name = 'sklad.spisanie_line'
    _description = u'Списание товаров строки'

    @api.one
    @api.depends('nomen_nomen_id')
    def _nomen(self):
        """
        Compute the total amounts.
        """

        print "---------------------**********************"  
        if self.nomen_nomen_id:
            # func_model = self.env['nomen.ed_izm']
            # function = func_model.search([('name', '=', self.nomen_nomen_id.ed_izm_id.name)]).id
            self.ed_izm_id = self.nomen_nomen_id.ed_izm_id
            self.nalog_nds_id = self.nomen_nomen_id.nalog_nds_id


    def return_name(self):
        self.name = self.sklad_spisanie_id.name

    name = fields.Char(string=u"Номер", required=True, compute='return_name')
    sklad_spisanie_id = fields.Many2one('sklad.spisanie', ondelete='cascade', string=u"Списание", required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True)
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", compute='_nomen',  store=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во", required=True)





class sklad_inventarizaciya(models.Model):
    _name = 'sklad.inventarizaciya'
    _description = u'Инвентаризация товаров'
    _order = 'date desc, id desc'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New' or vals.get('name', 'New') == None:
            vals['name'] = self.env['ir.sequence'].next_by_code('sklad.inventarizaciya') or 'New'
            vals['state'] = 'draft'


        result = super(sklad_inventarizaciya, self).create(vals)
        return result

    @api.multi
    def unlink(self):
        
        #print 'sssssssssssssssssssssssssssssssssssssssssssssss', self
        for pp in self:
            if pp.state != 'done':
                raise exceptions.ValidationError(_(u"Документ №%s Проведен и не может быть удален!" % (pp.name)))

        return super(sklad_inventarizaciya, self).unlink()


    name = fields.Char(string=u"Номер", required=True, copy=False, index=True, default='New')
    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', required=True)
    sklad_inventarizaciya_line = fields.One2many('sklad.inventarizaciya_line', 'sklad_inventarizaciya_id', string=u"Строка Инвентаризация товаров")
    proveden = fields.Boolean(string=u"Проводен")
    state = fields.Selection([
        ('create', "Создан"),
        ('draft', "Черновик"),
        ('confirmed', "Проведен"),
        ('done', "Отменен"),
        
    ], default='create')

       
    @api.multi
    def action_draft(self):
        for doc in self:
            vals_prihod = []
            vals_rashod = []
            for line in doc.sklad_inventarizaciya_line:
                if line.kol_otk>0:
                    vals_prihod.append({
                                 'name': line.nomen_nomen_id.name, 
                                 'sklad_sklad_id': doc.sklad_sklad_id.id, 
                                 'nomen_nomen_id': line.nomen_nomen_id.id, 
                                 'kol': line.kol_otk, 
                                })
                if line.kol_otk<0:
                    vals_rashod.append({
                                 'name': line.nomen_nomen_id.name, 
                                 'sklad_sklad_id': doc.sklad_sklad_id.id, 
                                 'nomen_nomen_id': line.nomen_nomen_id.id, 
                                 'kol': line.kol_otk, 
                                })
                      

                #print "++++++++++++++++++++++++++++++++++++++++++++", doc.sklad_sklad_id.id
                
            if ((len(vals_prihod)==0 or reg_ostatok_move(self, vals_prihod, 'prihod-draft')==True) and 
                (len(vals_rashod)==0 or reg_ostatok_move(self, vals_rashod, 'rashod-draft')==True)):
                self.state = 'draft'

        
    

    @api.multi
    def action_confirm(self):
        #self.write({'state': 'confirmed'})
        
        for doc in self:
            vals_prihod = []
            vals_rashod = []
            for line in doc.sklad_inventarizaciya_line:
                if line.kol_otk>0:
                    vals_prihod.append({
                                 'name': line.nomen_nomen_id.name, 
                                 'sklad_sklad_id': doc.sklad_sklad_id.id, 
                                 'nomen_nomen_id': line.nomen_nomen_id.id, 
                                 'kol': line.kol_otk, 
                                })
                if line.kol_otk<0:
                    vals_rashod.append({
                                 'name': line.nomen_nomen_id.name, 
                                 'sklad_sklad_id': doc.sklad_sklad_id.id, 
                                 'nomen_nomen_id': line.nomen_nomen_id.id, 
                                 'kol': line.kol_otk, 
                                })
                      

                #print "++++++++++++++++++++++++++++++++++++++++++++", doc.sklad_sklad_id.id
                
            if ((len(vals_prihod)==0 or reg_ostatok_move(self, vals_prihod, 'prihod')==True) and 
                (len(vals_rashod)==0 or reg_ostatok_move(self, vals_rashod, 'rashod')==True)):
                self.state = 'confirmed'





    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_zapolnit_ostatki(self):
        #print "ZZZZZZZZZZZZZZZZZZZZz"
        if self.state == 'confirmed':
            raise exceptions.ValidationError(_(u"Ошибка. Документ №%s проведен!" % (self.name,)))
        else:
            self.sklad_inventarizaciya_line.unlink()
            ost = self.env['sklad.ostatok']
            ost_nomen = ost.search([('sklad_sklad_id', '=', self.sklad_sklad_id.id)])
            for line in ost_nomen:
                vals={  'sklad_sklad_id': line.sklad_sklad_id.id,
                        'nomen_nomen_id': line.nomen_nomen_id.id,
                        'kol': line.kol,
                        'kol_fact': line.kol,
                        'sklad_inventarizaciya_id': self.id,
                        }
                print vals
                self.env['sklad.inventarizaciya_line'].create(vals)




class sklad_inventarizaciya_line(models.Model):
    _name = 'sklad.inventarizaciya_line'
    _description = u'Инвентаризация товаров строки'

    @api.one
    @api.depends('kol','kol_fact')
    def _amount(self):
        """
        Compute the total amounts.
        """
        if self.kol and self.kol_fact:
            self.kol_otk = self.kol_fact - self.kol
        

    @api.one
    @api.depends('nomen_nomen_id')
    def _nomen(self):
        """
        Compute the total amounts.
        """
        print "---------------------**********************"  
        if self.nomen_nomen_id:
            # func_model = self.env['nomen.ed_izm']
            # function = func_model.search([('name', '=', self.nomen_nomen_id.ed_izm_id.name)]).id
            self.ed_izm_id = self.nomen_nomen_id.ed_izm_id
            #self.nalog_nds_id = self.nomen_nomen_id.nalog_nds_id

    
    def return_name(self):
        self.name = self.sklad_inventarizaciya_id.name

    name = fields.Char(string=u"Номер", required=True, compute='return_name')
    sklad_inventarizaciya_id = fields.Many2one('sklad.inventarizaciya', ondelete='cascade', string=u"Инвентаризация", required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True)
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", compute='_nomen',  store=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во по учету", required=True)
    kol_fact = fields.Float(digits=(10, 3), string=u"Кол-во по факту", required=True)
    kol_otk = fields.Float(digits=(10, 3), string=u"Отклонение от факта", compute='_amount',  store=True)
 

class nomen_price(models.Model):
    _name = 'nomen.price'
    _description = u'Установка цен номенклатуры'
    _order = 'date desc'

    
    @api.model
    def create(self, vals):
        print "ssssssssssssssssssssssssssss", self.date
        if vals.get('name', 'New') == 'New' or vals.get('name', 'New') == None:
            vals['name'] = self.env['ir.sequence'].next_by_code('nomen.price') or 'New'
            
        result = super(nomen_price, self).create(vals)

        return result

    @api.multi
    def write(self, vals):
        result = super(nomen_price, self).write(vals)
        """Установка Даты в сроках""" 
        price_vals={}
        price_vals['date'] = self.date
        for line in self.nomen_price_line:
            price_line = self.env['nomen.price_line']
            price_line.browse(line.id).write(price_vals)

        return result




    name = fields.Char(string=u"Номер", required=True, copy=False, index=True, default='New')
    date = fields.Date(string='Дата', required=True, default=fields.Datetime.now)
    nomen_price_line = fields.One2many('nomen.price_line', 'nomen_price_id', string=u"Строка Установка цен номенклатуры")
    

class nomen_price_line(models.Model):
    _name = 'nomen.price_line'
    _description = u'Строка Установка цен номенклатуры'


    @api.model
    def create(self, vals):
        """Установка Даты в сроках""" 
        price = self.env['nomen.price']
        price_date = price.search([('id', '=', vals['nomen_price_id'])]).date      
        vals['date'] = price_date

        result = super(nomen_price_line, self).create(vals)

        
        return result
    
    @api.one
    @api.depends('nomen_nomen_id')
    def _nomen(self):
        if self.nomen_nomen_id:
            self.ed_izm_id = self.nomen_nomen_id.ed_izm_id


    def return_name(self):
        for line in self:
            line.name = line.nomen_price_id.name
            line.date = line.nomen_price_id.date


    name = fields.Char(string=u"Номер", required=True, compute='return_name')
    date = fields.Date(string='Дата',  store=True)
    nomen_price_id = fields.Many2one('nomen.price', ondelete='cascade', string=u"Установка цен номенклатуры", required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True)
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", compute='_nomen',  store=True)
    price = fields.Float(digits=(10, 2), string=u"Цена", required=True)
 