# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError

# #----------------------------------------------------------
# # Бухгалтерия
# #----------------------------------------------------------

# class buh_nomen_group(models.Model):
#     _name = 'buh.nomen_group'
#     _description = u'Номенклатурные группы (бух)'
#     name = fields.Char(string=u"Наименование", required=True)
#     id_1c = fields.Char(string=u"Номер в 1С")

# class buh_stati_zatrat(models.Model):
#     _name = 'buh.stati_zatrat'
#     _description = u'Статьи затрат (бух)'
#     name = fields.Char(string=u"Наименование", required=True)
#     sorting = fields.Char(string=u"Сортировка")
#     id_1c = fields.Char(string=u"Номер в 1С")





# #----------------------------------------------------------
# # Единицы измерения
# #----------------------------------------------------------

# class ed_izm_categ(models.Model):
#     _name = 'nomen.ed_izm_categ'
#     _description = u'Категории Единицы Измерения Номенклатуры'
#     name = fields.Char(string=u"Наименование", required=True)


# class ed_izm(models.Model):
#     _name = 'nomen.ed_izm'
#     _description = u'Единицы Измерения'
   
#     name = fields.Char(string=u"Наименование", required=True)
#     ed_izm_categ_id = fields.Many2one('nomen.ed_izm_categ', string=u"Категория ед.изм.", default=None)

# #----------------------------------------------------------
# # Номенклатура
# #----------------------------------------------------------
# class nomen_categ(models.Model):
#     _name = 'nomen.categ'
#     _description = u'Категории номенклатуры'
#     """Категории используются для вывода иерархического вида справочника"""
   
#     name = fields.Char(string=u"Наименование", required=True)

# class nomen_group(models.Model):
#     _name = 'nomen.group'
#     _description = u'Группы номенклатуры'
#     """Группы используются для отнесения номенклатуры к типу номенклатуры"""
   
#     name = fields.Char(string=u"Наименование", required=True) 
#     sorting = fields.Integer(string=u"Порядок", required=True, default=100) 

# class nomen_nomen(models.Model):
#     _name = 'nomen.nomen'
#     _description = u'Номенклатура'
#     _order = 'name'

#     name = fields.Char(string=u"Наименование", required=True)
#     nomen_categ_id = fields.Many2one('nomen.categ', string=u"Категория", default=None)
#     nomen_group_id = fields.Many2one('nomen.group', string=u"Группа", default=None)
#     ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", default=None)
#     nalog_nds_id = fields.Many2one('nalog.nds', string=u"Ставка НДС %", default=None)
#     buh_nomen_group_id = fields.Many2one('buh.nomen_group', string='Номенклатурная группа (бух)')
#     buh_stati_zatrat_id = fields.Many2one('buh.stati_zatrat', string='Статьи затрат')
#     id_1c = fields.Char(string=u"Номер в 1С")
#     active = fields.Boolean(string=u"Используется", default=True)

# #----------------------------------------------------------
# # Склад
# #----------------------------------------------------------

# class sklad_sklad(models.Model):
#     _name = 'sklad.sklad'
#     _description = u'Склады'
  
#     name = fields.Char(string=u"Наименование", required=True) 
#     partner_id = fields.Many2one('res.partner', string='Ответственный')
#     id_1c = fields.Char(string=u"Номер в 1С")


# #----------------------------------------------------------
# # Договора
# #----------------------------------------------------------
# class dogovor(models.Model):
#     _name = 'dogovor'
#     _description = u'Договора'
  
#     name = fields.Char(string=u"Номер", required=True) 
#     partner_id = fields.Many2one('res.partner', string='Ответственный')
#     date_start = fields.Date(string='Дата начала', required=True)
#     date_end = fields.Date(string='Дата окончания', required=True)
#     predmet = fields.Text(string=u"Предмет договора")
#     amount = fields.Float(digits=(10, 2), string=u"Сумма договора") 
#     id_1c = fields.Char(string=u"Номер в 1С")

#----------------------------------------------------------
# Регистры остатков и оборотов
#----------------------------------------------------------

class sklad_ostatok_price(models.Model):
    _name = 'sklad.ostatok_price'
    _description = u'Стоимость Остатки номенклатуры'
  

    name = fields.Char(string=u"Наименование", compute='_get_price', store=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во")
    price = fields.Float(digits=(10, 2), string=u"Цена", compute='_get_price', store=True)
    amount = fields.Float(digits=(10, 2), string=u"Сумма")


    def get_price(self, nomen_nomen_id):
        return self.search([
                      ('nomen_nomen_id', '=', nomen_nomen_id),
                    ], limit=1).price or 0


    @api.one
    @api.depends('kol', 'amount')
    def _get_price(self):
        if self.kol!=0 and self.amount:
            self.price = self.amount/self.kol
        if self.nomen_nomen_id:
            self.name = self.nomen_nomen_id.name

    def reg_update(self, nomen_nomen_id):
        zapros = """SELECT  sum(s.amount_oborot), sum(s.kol_oborot)
                    FROM sklad_oborot s
                    WHERE s.nomen_nomen_id=%s
                """ %(nomen_nomen_id)
        #print zapros
        self._cr.execute(zapros,)
        result = self._cr.fetchone()
        if len(result)>0:
            
            vals = {
                         'nomen_nomen_id': nomen_nomen_id, 
                         'kol': result[1],
                         'amount': result[0], 
                        }
            
            ost = self.search([
                              ('nomen_nomen_id', '=', nomen_nomen_id),
                            ])
            if len(ost)>0:
                ost.browse(ost[0].id).write(vals)
            else:
                ost.create(vals)
                

    # def reg_move(self, vals, vid_dvijeniya):
    #     print vals

    #     ost = self.search([
    #               ('nomen_nomen_id', '=', vals['nomen_nomen_id']),
    #             ])
    #     if len(ost)>0:
    #         vals['id'] = ost[0].id
    #         kol_do = ost[0].kol
    #         amount_do = ost[0].amount
            
    #     else:
    #         vals['id'] = False    
    #         kol_do = 0
    #         amount_do = 0

    #     if vid_dvijeniya == 'prihod' or vid_dvijeniya == 'rashod-draft':
    #             vals['kol'] += kol_do
    #             vals['amount'] += amount_do

                
    #     if vid_dvijeniya == 'rashod' or vid_dvijeniya == 'prihod-draft':
    #         vals['kol'] = kol_do - vals['kol']
    #         vals['amount'] = amount_do - vals['amount']


    #     if vals['id'] == False:
    #         ost.create(vals)
    #     else:
    #         ost.browse(vals['id']).write(vals)




class sklad_ostatok(models.Model):
    _name = 'sklad.ostatok'
    _description = u'Остатки номенклатуры'
  
    
    name = fields.Char(string=u"Наименование", compute='_get_name', store=True)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во")
    
    @api.one
    @api.depends('kol')
    def _get_name(self):
        if self.nomen_nomen_id:
            self.name = self.nomen_nomen_id.name


    def reg_update(self, sklad_sklad_id, nomen_nomen_id):
        
        zapros = """SELECT  sum(s.kol_oborot)
                    FROM sklad_oborot s
                    WHERE s.sklad_sklad_id=%s and s.nomen_nomen_id=%s
                """ %(sklad_sklad_id, nomen_nomen_id)
        
        self._cr.execute(zapros,)
        result = self._cr.fetchone()
        if len(result)>0:
            kol_ostatok = result[0]
            
        vals = {
                     'sklad_sklad_id': sklad_sklad_id,
                     'nomen_nomen_id': nomen_nomen_id, 
                     'kol': kol_ostatok or 0,
                }
        
        ost = self.search([
                          ('sklad_sklad_id', '=', sklad_sklad_id),
                          ('nomen_nomen_id', '=', nomen_nomen_id),
                        ])
        if len(ost)>0:
            ost.browse(ost[0].id).write(vals)
        else:
            ost.create(vals)


    #@api.one
    def reg_move(self, obj, vals, vid_dvijeniya):
        #"""
        #    Ф-я осуществляет запись в таблицу остатков и оборотов товаров по складам
        #"""
        #print u"Начало проведение документа"
        #print vals
        message = u''
        



        if len(vals) == 0:
            message = u"Нет данных для проведения документа. Не заполненна табличная часть"
            raise exceptions.ValidationError(_(u"Ошибка. Документ №%s Не проведен! %s" % (obj.name, message)))
            return False

        ost = obj.env['sklad.ostatok']
        ost_price = obj.env['sklad.ostatok_price']
        for line in vals:
            err = False
            line['id'] = False
            line['obj'] = obj.__class__.__name__
            line['obj_id'] = obj.id
            line['date'] = obj.date
            line['vid_dvijeniya'] = vid_dvijeniya
            if vid_dvijeniya == 'prihod':
                line['kol_prihod'] = line['kol']
                line['kol_oborot'] = line['kol']
            if vid_dvijeniya == 'rashod':
                line['kol_rashod'] = line['kol']
                line['kol_oborot'] = -1*line['kol']

            #Проверка на ошибки
            if vid_dvijeniya != 'rashod' and vid_dvijeniya != 'prihod':
                err = True
                message = u"Не верно указан вид движения"
            if line['kol']<=0:
                err = True
                message = u"Кол-во должно быть больше нуля"
            if line['sklad_sklad_id']==False or line['sklad_sklad_id']==None:
                err = True
                message = u"Не указан склад"
            if line['nomen_nomen_id']==False or line['nomen_nomen_id']==None:
                err = True
                message = u"Не указана номенклатура"
            #-------------------------------------------------------------------------------
            #---------Контроль отрицательных остатков---------------------------------------
            #-------------------------------------------------------------------------------
            # if (vid_dvijeniya == 'rashod' or vid_dvijeniya == 'prihod-draft') and line['kol']<0:
            #         err = True
            #         message = u'Невозможно списать %s %s. Требуется %s, на остатке %s' % (line['name'], line['kol'], line['kol_oborot'], kol_do)
            #-------------------------------------------------------------------------------
            #---------Контроль отрицательных остатков---------------------------------------
            #-------------------------------------------------------------------------------


            # ost_nomen = ost.search([
            #     ('sklad_sklad_id', '=', line['sklad_sklad_id']),
            #     ('nomen_nomen_id', '=', line['nomen_nomen_id']),
            #     ])
            
            # if len(ost_nomen)>0:
            #     line['id'] = ost_nomen[0].id
            #     kol_do = ost_nomen[0].kol
                
            # else:
            #     kol_do = 0
                


            if 'amount' not in line:
                line['is_raschet'] = True #Признак что необходимо расчитать стоимость
                price = ost_price.get_price(line['nomen_nomen_id'])
                line['amount'] = price * line['kol']
            else:
                line['is_raschet'] = False

            if vid_dvijeniya == 'prihod':
                line['amount_oborot'] = line['amount']
                line['amount_prihod'] = line['amount']
            if vid_dvijeniya == 'rashod':
                line['amount_oborot'] = -1 * line['amount']
                line['amount_rashod'] = line['amount']

                           

            if err == True:
                print line
                raise exceptions.ValidationError(_(u"Ошибка. Документ №%s Не проведен! %s" % (obj.name, message)))
                return False
            
        #Если нет ошибок приступаем к записям в регистры   
        obr = obj.env['sklad.oborot']
        for line in vals:    
            print line
            #Движения по Регистру остатки - обороты
            line.pop('kol', None)  #Удаляем ключ kol т.к его нет в структуре sklad_oborot
            obr.create(line)

            ost.reg_update(line['sklad_sklad_id'], line['nomen_nomen_id'])
            ost_price.reg_update(line['nomen_nomen_id'])


        

        return True


    def reg_move_draft(self, obj):

        obr = obj.env['sklad.oborot']
        ids_del = obr.search([  ('obj_id', '=', obj.id),
                                ('obj', '=', obj.__class__.__name__),
                            ])
        vals = []
        for line in ids_del:
            vid_dvijeniya = line['vid_dvijeniya']+'-draft'
            vals.append({
                         'sklad_sklad_id': line.sklad_sklad_id.id, 
                         'nomen_nomen_id': line.nomen_nomen_id.id, 
                        })
                        
            line.na_udalenie = True #Пометка на удаление, если что пойдет не так, можно увидеть что не удалено

        ids_del.unlink()  #Удаляем записи

        #Пересчитываем итоги
        if len(vals)>0:
            ost = obj.env['sklad.ostatok']
            ost_price = obj.env['sklad.ostatok_price']
            for line in vals:
                ost.reg_update(line['sklad_sklad_id'], line['nomen_nomen_id'])
                ost_price.reg_update(line['nomen_nomen_id'])

        
        return True
    


        # #Группируем спиcок по видам движения, преобразуем в формат:
        # RESULT = [{vid: vid_dvijeniya, data: [{name,sklad_sklad_id,nomen_nomen_id,kol}]}]

        # import itertools
        # import operator
        # def groupid_drop(d):
        #     del d['vid']
        #     return d
        # RESULT=[{'vid': i, 'data': map(groupid_drop, grp)} for i, grp in itertools.groupby(vals, operator.itemgetter('vid'))]
        # #print RESULT

        # for line in RESULT:
        #     vid_dvijeniya = line['vid']+'-draft'
        #     sklad_ostatok = self.env['sklad.ostatok']    
        #     if sklad_ostatok.reg_move(doc, line['data'], 'prihod-draft')==True:
        #         self.state = 'draft'


    

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

    @api.one
    @api.depends('kol_oborot', 'amount_oborot')
    def _get_price(self):
        if self.kol_oborot!=0 and self.amount_oborot:
            self.price = self.amount_oborot/self.kol_oborot
        if self.nomen_nomen_id:
            self.name = self.nomen_nomen_id.name
  
    name = fields.Char(string=u"_Наименование", compute='_get_price', store=True)
    obj = fields.Char(string=u"Регистратор", required=True)
    obj_id = fields.Integer(string=u"ID Регистратора", required=True)
    date = fields.Datetime(string='Дата', required=True)
    vid_dvijeniya = fields.Char(string=u"Вид движения", required=True, oldname='vid')
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True)
    kol_oborot = fields.Float(digits=(10, 3), string=u"Кол-во оборот", default=0)
    kol_prihod = fields.Float(digits=(10, 3), string=u"Кол-во приход", default=0)
    kol_rashod = fields.Float(digits=(10, 3), string=u"Кол-во расход", default=0)
    price = fields.Float(digits=(10, 2), string=u"Цена", compute='_get_price', store=True, default=0)
    amount_oborot = fields.Float(digits=(10, 2), string=u"Сумма оборот", default=0)
    amount_prihod = fields.Float(digits=(10, 2), string=u"Сумма приход", default=0)
    amount_rashod = fields.Float(digits=(10, 2), string=u"Сумма расход", default=0)
    na_udalenie = fields.Boolean(string=u"На удаление?", default=False)
    is_raschet = fields.Boolean(string=u"Расчитывать сумму?", default=False, help=u"Если истина то суммы нужно расчитать например для док-та перемещении товаров")
    

# def reg_ostatok_move(obj,vals, vid_dvijeniya):
#     """
#         Ф-я осуществляет запись в таблицу остатков и оборотов товаров по складам
#     """


#     message = ''
    
#     if len(vals) == 0:
#         message = u"Нет данных для проведения документа. Не заполненна табличная часть"
#         raise exceptions.ValidationError(_(u"Ошибка. Документ №%s Не проведен! %s" % (obj.name, message)))
#         return False

#     ost = obj.env['sklad.ostatok']
#     for line in vals:
#         ost_nomen = ost.search([
#             ('sklad_sklad_id', '=', line['sklad_sklad_id']),
#             ('nomen_nomen_id', '=', line['nomen_nomen_id']),
#             ])
#         line['err'] = False
#         line['id'] = False
#         line['obj'] = obj.__class__.__name__
#         line['obj_id'] = obj.id
#         line['date'] = obj.date
#         line['vid'] = vid_dvijeniya
#         if vid_dvijeniya == 'prihod':
#             line['kol_prihod'] = line['kol']
#             line['kol_oborot'] = line['kol']
#         if vid_dvijeniya == 'rashod':
#             line['kol_rashod'] = line['kol']
#             line['kol_oborot'] = -1*line['kol']

#         if line['kol']<=0:
#             line['err'] = True
#             message = u"Кол-во должно быть больше нуля"

#         print line
#         if len(ost_nomen)>0:
        
#             line['id'] = ost_nomen[0].id
#             kol_do = ost_nomen[0].kol
#             if vid_dvijeniya == 'prihod' or vid_dvijeniya == 'rashod-draft':
#                 line['kol'] += kol_do
#             if vid_dvijeniya == 'rashod' or vid_dvijeniya == 'prihod-draft':
#                 line['kol'] = kol_do - line['kol']
                

#         if (vid_dvijeniya == 'rashod' or vid_dvijeniya == 'prihod-draft') and line['kol']<0:
#                 line['err'] = True
#                 message = u'Невозможно списать %s. Требуется %s, на остатке %s' % (line['kol'], line['kol_oborot'], kol_do)

#         if line['err'] == True:
#             raise exceptions.ValidationError(_(u"Ошибка. Документ №%s Не проведен! %s" % (obj.name, message)))
#             return False


#     for line in vals:
#         if line['id'] == False:
#             ost.create(line)
#         else:
#             ost.browse(line['id']).write(line)

#     #Движения по Регистру остатки - обороты
#     obr = obj.env['sklad.oborot']
#     if vid_dvijeniya == 'prihod' or vid_dvijeniya == 'rashod':
#         for line in vals:
#             obr.create(line)
#     else:

#         ids_del = obr.search([  ('obj_id', '=', obj.id),
#                                 ('obj', '=', obj.__class__.__name__),
#                                 ])
#         ids_del.unlink()

    

#     return True


            


        
             





#----------------------------------------------------------
# Документы прихода/расхода
#----------------------------------------------------------
# class nalog_nds(models.Model):
#     _name = 'nalog.nds'
#     _description = u'Ставки НДС'

#     name = fields.Char(string=u"Наименование", required=True)
#     nds = fields.Float(digits=(10, 2), string=u"% НДС", required=True)


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
        
        #print 'sssssssssssssssssssssssssssssssssssssssssssssss', self
        for pp in self:
            if pp.state == 'confirmed':
                raise exceptions.ValidationError(_(u"Документ №%s Проведен и не может быть удален!" % (pp.name)))

        return super(pokupka_pokupka, self).unlink()


    name = fields.Char(string=u"Номер", required=True, copy=False, index=True, default='New')
    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now)
    partner_id = fields.Many2one('res.partner', string='Контрагент', required=True)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', required=True)
    sklad_razmeshenie_id = fields.Many2one('sklad.razmeshenie', string='Размещение', copy=False)
    pokupka_pokupka_line = fields.One2many('pokupka.pokupka_line', 'pokupka_pokupka_id', string=u"Строка товаров Поступление товаров", copy=True)
    pokupka_pokupka_uslugi_line = fields.One2many('pokupka.pokupka_uslugi_line', 'pokupka_pokupka_id', string=u"Строка услуг Поступление товаров", copy=True)
    nds_price = fields.Boolean(string=u"Цена включает НДС")
    amount_bez_nds = fields.Float(digits=(10, 2), string=u"Сумма без НДС", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    amount_nds = fields.Float(digits=(10, 2), string=u"Сумма НДС", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    amount_total = fields.Float(digits=(10, 2), string=u"Всего", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    proveden = fields.Boolean(string=u"Проводен")
    metod_raspredeleniya = fields.Selection([
        ('neraspredelyat', "Нераспределяеть"),
        ('po_stoimosti', "По стоимости"),
        ('po_kolichestvu', "По количеству")        
    ], default='po_stoimosti', string=u"Метод распределения услуг")
    
    state = fields.Selection([
        ('create', "Создан"),
        ('draft', "Черновик"),
        ('confirmed', "Проведен"),
        ('done', "Отменен"),
        
    ], default='create')

    @api.one
    @api.depends('pokupka_pokupka_line.kol','pokupka_pokupka_line.price',
                 'pokupka_pokupka_line.amount','pokupka_pokupka_line.nalog_nds_id',
                 'pokupka_pokupka_uslugi_line.kol','pokupka_pokupka_uslugi_line.price',
                 'pokupka_pokupka_uslugi_line.amount','pokupka_pokupka_uslugi_line.nalog_nds_id')
    def _amount_all(self):
        """
        Compute the total amounts.
        """
        self.amount_bez_nds=self.amount_nds = 0

        for line in self.pokupka_pokupka_line:
            self.amount_nds += line.amount_nds
            self.amount_total += line.amount_total
        
        for line in self.pokupka_pokupka_uslugi_line:
            self.amount_nds += line.amount_nds
            self.amount_total += line.amount_total
        
        self.amount_bez_nds = self.amount_total - self.amount_nds

   
    @api.multi
    def action_draft(self):
        for doc in self:
            # vals = []
            # for line in doc.pokupka_pokupka_line:
            #     vals.append({
            #                  'name': line.nomen_nomen_id.name, 
            #                  'sklad_sklad_id': doc.sklad_sklad_id.id, 
            #                  'nomen_nomen_id': line.nomen_nomen_id.id, 
            #                  'kol': line.kol, 
            #                 })

            #     #print "++++++++++++++++++++++++++++++++++++++++++++", doc.sklad_sklad_id.id
            # sklad_ostatok = self.env['sklad.ostatok']    
            # if sklad_ostatok.reg_move(doc, vals, 'prihod-draft')==True:
            #     self.state = 'draft'

            sklad_ostatok = self.env['sklad.ostatok']    
            if sklad_ostatok.reg_move_draft(doc)==True:
                self.state = 'draft'
    

    @api.multi
    def action_confirm(self):
        #self.write({'state': 'confirmed'})
        
        for doc in self:
            if len(doc.pokupka_pokupka_uslugi_line)>0 and doc.metod_raspredeleniya!='neraspredelyat':
                
                amount_uslugi_bez_nds = sum(line.amount_bez_nds for line in doc.pokupka_pokupka_uslugi_line)
                
                sum_kol = sum(line.kol for line in doc.pokupka_pokupka_line)
                
                if sum_kol>0:
                    if doc.metod_raspredeleniya == 'po_kolichestvu':
                        for line in doc.pokupka_pokupka_line:
                            line.amount_uslugi = line.kol/sum_kol * amount_uslugi_bez_nds

                    if doc.metod_raspredeleniya == 'po_stoimosti':
                        sum_amount = sum(line.amount_bez_nds for line in doc.pokupka_pokupka_line)
                        for line in doc.pokupka_pokupka_line:
                            line.amount_uslugi = line.amount_bez_nds/sum_amount * amount_uslugi_bez_nds

                    #Проверка погрешности распределения
                    sum_amount_uslugi = sum(line.amount_uslugi for line in doc.pokupka_pokupka_line)
                    if sum_amount_uslugi != amount_uslugi_bez_nds:
                        line = doc.pokupka_pokupka_line[0] #берем первую строку и прибавляем погрешность
                        line.amount_uslugi += amount_uslugi_bez_nds - sum_amount_uslugi

            vals = []
            for line in doc.pokupka_pokupka_line:
                vals.append({
                             'name': line.nomen_nomen_id.name, 
                             'sklad_sklad_id': doc.sklad_sklad_id.id, 
                             'nomen_nomen_id': line.nomen_nomen_id.id, 
                             'kol': line.kol, 
                             'amount': line.amount_bez_nds + line.amount_uslugi, 
                            })

                # print "++++++++++++++++++++++++++++++++++++++++++++", vals
                # print "++++++++++++++++++++++++++++++++++++++++++++", line.amount_bez_nds
                


            sklad_ostatok = self.env['sklad.ostatok']
            if sklad_ostatok.reg_move(doc, vals, 'prihod')==True:
                doc.state = 'confirmed'
            else:
                print u"Ошибка при проведении документа"





    @api.multi
    def action_done(self):
        self.state = 'done'


    @api.multi
    def action_razmeshenie(self):
        
        
        if not self.sklad_razmeshenie_id:
            razmeshenie = self.env['sklad.razmeshenie'].create({
                'sklad_otp_id': self.sklad_sklad_id.id,
                'obj_id': self.id,
                'obj': self.__class__.__name__  
                
            })

            self.sklad_razmeshenie_id = razmeshenie.id
            
            vals = []
            for line in self.pokupka_pokupka_line:
                vals.append({
                                 'name': line.nomen_nomen_id.name, 
                                 'nomen_nomen_id': line.nomen_nomen_id.id, 
                                 'kol': line.kol, 
                               
                                })

            razmeshenie.zapolnit(vals)


        return {
            'name': ('Assignment Sub'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sklad.razmeshenie',
            'res_id': self.sklad_razmeshenie_id.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target':'self'
        }
        # view_id = self.env.ref('sklad.sklad_razmeshenie_form_view').id
        # context = self._context.copy()
        # return {
        #     'name':'sklad_razmeshenie.form',
        #     'view_type':'form',
        #     'view_mode':'form',
        #     'views' : [(view_id,'form')],
        #     'res_model':'sklad.razmeshenie',
        #     'view_id':view_id,
        #     'type':'ir.actions.act_window',
        #     'res_id':self.id,
        #     'target':'new',
        #     'context':context,
        # }


class pokupka_pokupka_line(models.Model):
    _name = 'pokupka.pokupka_line'
    _description = u'Поступление товаров строки'
    _order = 'sequence'


    @api.model
    def create(self, vals):
        print vals
        if vals.get('nalog_nds_id') == False:
            raise exceptions.ValidationError(_(u"Не заполнено поле НДС"))

        result = super(pokupka_pokupka_line, self).create(vals)
        return result

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
        
        if self.nomen_nomen_id:
            # func_model = self.env['nomen.ed_izm']
            # function = func_model.search([('name', '=', self.nomen_nomen_id.ed_izm_id.name)]).id
            self.ed_izm_id = self.nomen_nomen_id.ed_izm_id
            if self.nomen_nomen_id.nalog_nds_id:
                self.nalog_nds_id = self.nomen_nomen_id.nalog_nds_id

    def return_name(self):
        self.name = self.pokupka_pokupka_id.name

    #@api.one
    def _set_nds(self):
        for record in self:
            if not record.nalog_nds_id: continue

    name = fields.Char(string=u"Номер", required=True, compute='return_name')
    pokupka_pokupka_id = fields.Many2one('pokupka.pokupka', ondelete='cascade', string=u"Поступление", required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True, domain=[('is_usluga', '=', False)])
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", compute='_nomen',  store=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во", required=True)
    price = fields.Float(digits=(10, 2), string=u"Цена", readonly=False, compute='_amount',  store=True)
    amount = fields.Float(digits=(10, 2), string=u"Сумма", readonly=False, store=True, group_operator="sum")
    nalog_nds_id = fields.Many2one('nalog.nds',string=u"%НДС", required=True, readonly=False, compute='_nomen', inverse='_set_nds',  store=True, copy=True)
    amount_bez_nds = fields.Float(digits=(10, 2), string=u"Сумма без НДС", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    amount_nds = fields.Float(digits=(10, 2), string=u"Сумма НДС", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    amount_total = fields.Float(digits=(10, 2), string=u"Всего", readonly=True, compute='_amount_all',  store=True, group_operator="sum")
    amount_uslugi = fields.Float(digits=(10, 2), string=u"Доп расходы (услуг)", readonly=True,  store=True, group_operator="sum")
    sequence = fields.Integer(string=u"Сорт.", help="Сортировка")



class pokupka_pokupka_uslugi_line(models.Model):
    _name = 'pokupka.pokupka_uslugi_line'
    _description = u'Поступление товаров Услуги строки'
    _order = 'sequence'


    @api.model
    def create(self, vals):
        print vals
        if vals.get('nalog_nds_id') == False:
            raise exceptions.ValidationError(_(u"Не заполнено поле НДС"))

        result = super(pokupka_pokupka_uslugi_line, self).create(vals)
        return result

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
        
        if self.nomen_nomen_id:
            # func_model = self.env['nomen.ed_izm']
            # function = func_model.search([('name', '=', self.nomen_nomen_id.ed_izm_id.name)]).id
            self.ed_izm_id = self.nomen_nomen_id.ed_izm_id
            if self.nomen_nomen_id.nalog_nds_id:
                self.nalog_nds_id = self.nomen_nomen_id.nalog_nds_id

    def return_name(self):
        self.name = self.pokupka_pokupka_id.name

    #@api.one
    def _set_nds(self):
        for record in self:
            if not record.nalog_nds_id: continue

    name = fields.Char(string=u"Номер", required=True, compute='return_name')
    pokupka_pokupka_id = fields.Many2one('pokupka.pokupka', ondelete='cascade', string=u"Поступление", required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Услуги', required=True, domain=[('is_usluga', '=', True)])
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", compute='_nomen',  store=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во", required=True)
    price = fields.Float(digits=(10, 2), string=u"Цена", readonly=False, compute='_amount',  store=True)
    amount = fields.Float(digits=(10, 2), string=u"Сумма", readonly=False, store=True, group_operator="sum")
    nalog_nds_id = fields.Many2one('nalog.nds',string=u"%НДС", readonly=False, compute='_nomen', inverse='_set_nds',  store=True)
    amount_bez_nds = fields.Float(digits=(10, 2), string=u"Сумма без НДС", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    amount_nds = fields.Float(digits=(10, 2), string=u"Сумма НДС", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    amount_total = fields.Float(digits=(10, 2), string=u"Всего", readonly=True, compute='_amount_all',  store=True, group_operator="sum")
    sequence = fields.Integer(string=u"Сорт.", help="Сортировка")
    




    

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
            if sp.state == 'confirmed':
                raise exceptions.ValidationError(_(u"Документ №%s Проведен и не может быть удален!" % (sp.name)))

        return super(sklad_peremeshenie, self).unlink()


    name = fields.Char(string=u"Номер", required=True, copy=False, index=True, default='New')
    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now)
    
    sklad_razmeshenie_id = fields.Many2one('sklad.razmeshenie', string='Размещение', copy=False)
    sklad_otp_id = fields.Many2one('sklad.sklad', string='Склад отправитель', required=True)
    sklad_pol_id = fields.Many2one('sklad.sklad', string='Склад получатель', required=True)
    sklad_peremeshenie_line = fields.One2many('sklad.peremeshenie_line', 'sklad_peremeshenie_id', string=u"Строка Перемещение товаров", copy=True)
    
    state = fields.Selection([
        ('create', "Создан"),
        ('draft', "Черновик"),
        ('confirmed', "Проведен"),
        ('done', "Отменен"),
        
    ], default='create')

    
   
    @api.multi
    def action_draft(self):
        for doc in self:
            # vals_otp = []
            # vals_pol = []
            # for line in doc.sklad_peremeshenie_line:
            #     vals_otp.append({
            #                  'name': line.nomen_nomen_id.name, 
            #                  'sklad_sklad_id': doc.sklad_otp_id.id, 
            #                  'nomen_nomen_id': line.nomen_nomen_id.id, 
            #                  'kol': line.kol, 
            #                 })
            #     vals_pol.append({
            #                  'name': line.nomen_nomen_id.name, 
            #                  'sklad_sklad_id': doc.sklad_pol_id.id, 
            #                  'nomen_nomen_id': line.nomen_nomen_id.id, 
            #                  'kol': line.kol, 
            #                 })
            
            sklad_ostatok = self.env['sklad.ostatok']
            
            if sklad_ostatok.reg_move_draft(doc)==True:
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
                             'sklad_sklad_id': line.sklad_otp_razmeshenie_id.id, 
                             'nomen_nomen_id': line.nomen_nomen_id.id, 
                             'kol': line.kol, 
                            })
                vals_pol.append({
                             'name': line.nomen_nomen_id.name, 
                             'sklad_sklad_id': doc.sklad_pol_id.id, 
                             'nomen_nomen_id': line.nomen_nomen_id.id, 
                             'kol': line.kol, 
                            })

            sklad_ostatok = self.env['sklad.ostatok']
            if (sklad_ostatok.reg_move(doc, vals_otp, 'rashod')==True and 
                sklad_ostatok.reg_move(doc, vals_pol, 'prihod')==True):
                self.state = 'confirmed'





    @api.multi
    def action_done(self):
        self.state = 'done'


    @api.multi
    def action_razmeshenie(self):
                
        if not self.sklad_razmeshenie_id:
            razmeshenie = self.env['sklad.razmeshenie'].create({
                'sklad_otp_id': self.sklad_pol_id.id,
                'obj_id': self.id,
                'obj': self.__class__.__name__  
                
            })

            self.sklad_razmeshenie_id = razmeshenie.id
            
            vals = []
            for line in self.sklad_peremeshenie_line:
                vals.append({
                                 'name': line.nomen_nomen_id.name, 
                                 'nomen_nomen_id': line.nomen_nomen_id.id, 
                                 'kol': line.kol, 
                               
                                })

            razmeshenie.zapolnit(vals)


        return {
            'name': ('Assignment Sub'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sklad.razmeshenie',
            'res_id': self.sklad_razmeshenie_id.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target':'self'
        }



class sklad_peremeshenie_line(models.Model):
    _name = 'sklad.peremeshenie_line'
    _description = u'Перемещение товаров строки'
    _order = 'sequence'

    @api.one
    @api.depends('nomen_nomen_id')
    def _nomen(self):
        """
        Compute the total amounts.
        """
        #print "---------------------**********************"  
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

    @api.one
    @api.depends('nomen_nomen_id')
    def _get_sklad(self):
        
        self.sklad_otp_id = self.sklad_peremeshenie_id.sklad_otp_id
        
        nomen_sklad = self.env['nomen.nomen_sklad_line']
        self.sklad_otp_razmeshenie_id = nomen_sklad.search([
                                
                                ('nomen_nomen_id', '=', self.nomen_nomen_id.id),
                                ('sklad_sklad_id', 'child_of', self.sklad_peremeshenie_id.sklad_otp_id.id),

                                ], limit=1).sklad_sklad_id.id or self.sklad_otp_id.id
              
        
        


    def _set_sklad(self):
        for record in self:
            if not record.sklad_otp_razmeshenie_id: continue


    name = fields.Char(string=u"Номер", required=True, compute='return_name')
    sklad_peremeshenie_id = fields.Many2one('sklad.peremeshenie', ondelete='cascade', string=u"Перемещение", required=True)
    
    sklad_otp_id = fields.Many2one('sklad.sklad', string='Склад отправитель', 
                                        compute='_get_sklad', 
                                        )
    sklad_otp_razmeshenie_id = fields.Many2one('sklad.sklad', string='Склад откуда', 
                                        compute='_get_sklad', 
                                        inverse='_set_sklad', 
                                        domain="[('id','child_of',sklad_otp_id)]", 
                                        store=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True, domain=[('is_usluga', '=', False)])
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", compute='_nomen',  store=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во", required=True)
    sequence = fields.Integer(string=u"Сорт.", help="Сортировка")



class sklad_razmeshenie(models.Model):
    _name = 'sklad.razmeshenie'
    _description = u'Размещение товаров'
    _order = 'date desc, id desc'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New' or vals.get('name', 'New') == None:
            vals['name'] = self.env['ir.sequence'].next_by_code('sklad.razmeshenie') or 'New'
            vals['state'] = 'draft'


        result = super(sklad_razmeshenie, self).create(vals)
        return result

    @api.multi
    def unlink(self):
        
        for sp in self:
            if sp.state == 'confirmed':
                raise exceptions.ValidationError(_(u"Документ №%s Проведен и не может быть удален!" % (sp.name)))

        return super(sklad_razmeshenie, self).unlink()

    @api.multi
    def _get_obj_name(self):
        
        for record in self:
            if record.obj and record.obj_id:
                doc = self.env[record.obj]
                obj_name = doc.search([
                                        ('id', '=', record.obj_id),
                                        ], limit=1) or False
                if obj_name:
                    record.obj_name = obj_name._description + u' ' + obj_name.name + u' от ' + str(obj_name.date)
            else:
                record.obj_name = False

    name = fields.Char(string=u"Номер", required=True, copy=False, index=True, default='New')
    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now)
    obj_name = fields.Char(string=u"Основание", compute='_get_obj_name', copy=False)
    obj = fields.Char(string=u"Регистратор", copy=False)
    obj_id = fields.Integer(string=u"ID Регистратора", copy=False)
    sklad_otp_id = fields.Many2one('sklad.sklad', string='Склад отправитель', required=True)
    sklad_razmeshenie_line = fields.One2many('sklad.razmeshenie_line', 'sklad_razmeshenie_id', string=u"Строка Размещения товаров", copy=True)
    
    state = fields.Selection([
        ('create', "Создан"),
        ('draft', "Черновик"),
        ('confirmed', "Проведен"),
        ('done', "Отменен"),
        
    ], default='create')

    
   
    @api.multi
    def action_draft(self):
        for doc in self:
            
            sklad_ostatok = self.env['sklad.ostatok']
            
            if sklad_ostatok.reg_move_draft(doc)==True:
                self.state = 'draft'

        
    

    @api.multi
    def action_confirm(self):
        #self.write({'state': 'confirmed'})
        
        for doc in self:
            vals_otp = []
            vals_pol = []
            for line in doc.sklad_razmeshenie_line:
                vals_otp.append({
                             'name': line.nomen_nomen_id.name, 
                             'sklad_sklad_id': doc.sklad_otp_id.id, 
                             'nomen_nomen_id': line.nomen_nomen_id.id, 
                             'kol': line.kol, 
                            })
                vals_pol.append({
                             'name': line.nomen_nomen_id.name, 
                             'sklad_sklad_id': line.sklad_pol_id.id, 
                             'nomen_nomen_id': line.nomen_nomen_id.id, 
                             'kol': line.kol, 
                            })

            sklad_ostatok = self.env['sklad.ostatok']
            if (sklad_ostatok.reg_move(doc, vals_otp, 'rashod')==True and 
                sklad_ostatok.reg_move(doc, vals_pol, 'prihod')==True):
                self.state = 'confirmed'





    @api.multi
    def action_done(self):
        self.state = 'done'

    def zapolnit(self, vals):
        for line in vals:
            line['sklad_razmeshenie_id'] = self.id
            nomen_sklad = self.env['nomen.nomen_sklad_line']
            sklad_pol_id = nomen_sklad.search([
                                    
                                    ('nomen_nomen_id', '=', line['nomen_nomen_id']),
                                    ('sklad_sklad_id', 'child_of', self.sklad_otp_id.id),

                                    ], limit=1).sklad_sklad_id.id or self.sklad_otp_id.id
            # line['sklad_pol_id'] = sklad_pol_id.id or self.sklad_otp_id.id
            #line['sklad_pol_id'] = self.sklad_otp_id.id
            print line
            self.sklad_razmeshenie_line.create({
                'sklad_razmeshenie_id': self.id,
                'nomen_nomen_id': line['nomen_nomen_id'],
                'kol': line['kol'],
                'sklad_pol_id': sklad_pol_id,




                })



class sklad_razmeshenie_line(models.Model):
    _name = 'sklad.razmeshenie_line'
    _description = u'Размещение товаров строки'
    _order = 'sequence'

    @api.one
    @api.depends('nomen_nomen_id')
    def _nomen(self):
        """
        Compute the total amounts.
        """
        #print "---------------------**********************"  
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
        self.name = self.sklad_razmeshenie_id.name


    @api.one
    @api.depends('nomen_nomen_id')
    def _get_sklad(self):
        
        nomen_sklad = self.env['nomen.nomen_sklad_line']
        self.sklad_pol_id = nomen_sklad.search([
                                
                                ('nomen_nomen_id', '=', self.nomen_nomen_id.id),
                                ('sklad_sklad_id', 'child_of', self.sklad_razmeshenie_id.sklad_otp_id.id),

                                ], limit=1).sklad_sklad_id.id
        self.sklad_otp_id = self.sklad_razmeshenie_id.sklad_otp_id
        
        


    def _set_sklad(self):
        for record in self:
            if not record.sklad_pol_id: continue


    def _search_sklad(self, operator, value):
        sklad = self.env['sklad.sklad']
        sklad_pol_ids = sklad.search([
                                
                                ('id', 'child_of', self.sklad_razmeshenie_id.sklad_otp_id.id),

                                ], )

        return sklad_pol_ids

    name = fields.Char(string=u"Номер", required=True, compute='return_name')
    

    sklad_razmeshenie_id = fields.Many2one('sklad.razmeshenie', ondelete='cascade', string=u"Размещение", required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True, domain=[('is_usluga', '=', False)])
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", compute='_nomen',  store=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во", required=True)
    sklad_otp_id = fields.Many2one('sklad.sklad', string='Склад отправитель', compute='_get_sklad')
    sklad_pol_id = fields.Many2one('sklad.sklad', string='Склад размещения', compute='_get_sklad', inverse='_set_sklad', domain="[('id','child_of',sklad_otp_id)]", store=True)
    sequence = fields.Integer(string=u"Сорт.", help="Сортировка")
   


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
        
        #print 'sssssssssssssssssssssssssssssssssssssssssssssss', self
        for sp in self:
            if sp.state == 'confirmed':
                raise exceptions.ValidationError(_(u"Документ №%s Проведен и не может быть удален!" % (sp.name)))

        return super(prodaja_prodaja, self).unlink()


    name = fields.Char(string=u"Номер", required=True, copy=False, index=True, default='New')
    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now)
    partner_id = fields.Many2one('res.partner', string='Контрагент', required=True)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', required=True)
    prodaja_prodaja_line = fields.One2many('prodaja.prodaja_line', 'prodaja_prodaja_id', string=u"Строка Реализации товаров" , copy=True)
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
            # vals = []
            # for line in doc.prodaja_prodaja_line:
            #     vals.append({
            #                  'name': line.nomen_nomen_id.name, 
            #                  'sklad_sklad_id': doc.sklad_sklad_id.id, 
            #                  'nomen_nomen_id': line.nomen_nomen_id.id, 
            #                  'kol': line.kol, 
            #                 })

                #print "++++++++++++++++++++++++++++++++++++++++++++", doc.sklad_sklad_id.id
            sklad_ostatok = self.env['sklad.ostatok']    
            if sklad_ostatok.reg_move_draft(doc)==True:
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

                #print "++++++++++++++++++++++++++++++++++++++++++++", doc.sklad_sklad_id.id
            sklad_ostatok = self.env['sklad.ostatok']    
            if sklad_ostatok.reg_move(doc, vals, 'rashod')==True:
                self.state = 'confirmed'





    @api.multi
    def action_done(self):
        self.state = 'done'


class prodaja_prodaja_line(models.Model):
    _name = 'prodaja.prodaja_line'
    _description = u'Реализация товаров строки'
    _order = 'sequence'

    
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
        
        if self.nomen_nomen_id:
            # func_model = self.env['nomen.ed_izm']
            # function = func_model.search([('name', '=', self.nomen_nomen_id.ed_izm_id.name)]).id
            self.ed_izm_id = self.nomen_nomen_id.ed_izm_id
            if self.nomen_nomen_id.nalog_nds_id:
                self.nalog_nds_id = self.nomen_nomen_id.nalog_nds_id

    def return_name(self):
        self.name = self.prodaja_prodaja_id.name

    def _set_nds(self):
        for record in self:
            if not record.nalog_nds_id: continue

    name = fields.Char(string=u"Номер", required=True, compute='return_name')
    prodaja_prodaja_id = fields.Many2one('prodaja.prodaja', ondelete='cascade', string=u"Реализация", required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True, domain=[('is_usluga', '=', False)])
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", compute='_nomen',  store=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во", required=True)
    price = fields.Float(digits=(10, 2), string=u"Цена", readonly=False, compute='_amount',  store=True)
    amount = fields.Float(digits=(10, 2), string=u"Сумма", readonly=False, store=True, group_operator="sum")
    nalog_nds_id = fields.Many2one('nalog.nds',string=u"%НДС", required=True, readonly=False, compute='_nomen', inverse='_set_nds',  store=True, copy=True)
    amount_bez_nds = fields.Float(digits=(10, 2), string=u"Сумма без НДС", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    amount_nds = fields.Float(digits=(10, 2), string=u"Сумма НДС", readonly=True, compute='_amount_all', store=True, group_operator="sum")
    amount_total = fields.Float(digits=(10, 2), string=u"Всего", readonly=True, compute='_amount_all',  store=True, group_operator="sum")
    sequence = fields.Integer(string=u"Сорт.", help="Сортировка")


class sklad_trebovanie_nakladnaya(models.Model):
    _name = 'sklad.trebovanie_nakladnaya'
    _description = u'Требование-накладная'
    _order = 'date desc, id desc'

    @api.model
    def create(self, vals):
        #print '******************',vals
        if vals.get('name', 'New') == 'New' or vals.get('name', 'New') == None:
            vals['name'] = self.env['ir.sequence'].next_by_code('sklad.trebovanie_nakladnaya') or 'New'
            vals['state'] = 'draft'


        result = super(sklad_trebovanie_nakladnaya, self).create(vals)
        return result

    @api.multi
    def unlink(self):
        
        #print 'sssssssssssssssssssssssssssssssssssssssssssssss', self
        for pp in self:
            if pp.state == 'confirmed':
                raise exceptions.ValidationError(_(u"Документ №%s Проведен и не может быть удален!" % (pp.name)))

        return super(sklad_trebovanie_nakladnaya, self).unlink()


    name = fields.Char(string=u"Номер", required=True, copy=False, index=True, default='New')
    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', required=True)
    sklad_trebovanie_nakladnaya_line = fields.One2many('sklad.trebovanie_nakladnaya_line', 'sklad_trebovanie_nakladnaya_id', string=u"Строка Списание товаров", copy=True)
    buh_nomen_group_id = fields.Many2one('buh.nomen_group', string='Номенклатурная группа (бух)')
    buh_stati_zatrat_id = fields.Many2one('buh.stati_zatrat', string='Статьи затрат')
    mol_id = fields.Many2one('res.partner', string='МОЛ')
    utverdil_id = fields.Many2one('res.partner', string='Утвердил')
    predsedatel_id = fields.Many2one('res.partner', string='Председатель')
    chlen1_id = fields.Many2one('res.partner', string='Член1')
    chlen2_id = fields.Many2one('res.partner', string='Член2')
    chlen3_id = fields.Many2one('res.partner', string='Член3')
    #chlen4_id = fields.Many2one('res.partner', string='Член4')

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
            # vals = []
            # for line in doc.sklad_trebovanie_nakladnaya_line:
            #     vals.append({
            #                  'name': line.nomen_nomen_id.name, 
            #                  'sklad_sklad_id': doc.sklad_sklad_id.id, 
            #                  'nomen_nomen_id': line.nomen_nomen_id.id, 
            #                  'kol': line.kol, 
            #                 })

                #print "++++++++++++++++++++++++++++++++++++++++++++", doc.sklad_sklad_id.id
            sklad_ostatok = self.env['sklad.ostatok']     
            if sklad_ostatok.reg_move_draft(doc)==True:
                self.state = 'draft'

        
    

    @api.multi
    def action_confirm(self):
        #self.write({'state': 'confirmed'})
        
        for doc in self:
            vals = []
            for line in doc.sklad_trebovanie_nakladnaya_line:
                vals.append({
                             'name': line.nomen_nomen_id.name, 
                             'sklad_sklad_id': doc.sklad_sklad_id.id, 
                             'nomen_nomen_id': line.nomen_nomen_id.id, 
                             'kol': line.kol, 
                            })

                #print "++++++++++++++++++++++++++++++++++++++++++++", doc.sklad_sklad_id.id
            sklad_ostatok = self.env['sklad.ostatok']    
            if sklad_ostatok.reg_move(doc, vals, 'rashod')==True:
                self.state = 'confirmed'





    @api.multi
    def action_done(self):
        self.state = 'done'


class sklad_trebovanie_nakladnaya_line(models.Model):
    _name = 'sklad.trebovanie_nakladnaya_line'
    _description = u'Требование-накладная строки'
    _order = 'sequence'

    # @api.model
    # def create(self, vals):
    #     if vals.get('sklad_trebovanie_nakladnaya_id.buh_nomen_group_id', 'New') != None:
    #         vals['buh_nomen_group_id'] = self.sklad_trebovanie_nakladnaya_id.buh_nomen_group_id
            


    #     result = super(sklad_trebovanie_nakladnaya_line, self).create(vals)
    #     return result

    @api.one
    @api.depends('nomen_nomen_id')
    def _nomen(self):
        """
        Compute the total amounts.
        """

        #print "---------------------**********************"  
        if self.nomen_nomen_id:
            # func_model = self.env['nomen.ed_izm']
            # function = func_model.search([('name', '=', self.nomen_nomen_id.ed_izm_id.name)]).id
            self.ed_izm_id = self.nomen_nomen_id.ed_izm_id
            self.nalog_nds_id = self.nomen_nomen_id.nalog_nds_id
            self.nomen_name = self.nomen_nomen_id.name
            
            #Подставляем , вначале по Номенклатуре потом Общую если есть
            if self.sklad_trebovanie_nakladnaya_id.buh_nomen_group_id:
                self.buh_nomen_group_id = self.sklad_trebovanie_nakladnaya_id.buh_nomen_group_id
            else:
                self.buh_nomen_group_id = self.nomen_nomen_id.buh_nomen_group_id
            
            if self.sklad_trebovanie_nakladnaya_id.buh_stati_zatrat_id:
                self.buh_stati_zatrat_id = self.sklad_trebovanie_nakladnaya_id.buh_stati_zatrat_id
            else:
                self.buh_stati_zatrat_id = self.nomen_nomen_id.buh_stati_zatrat_id
                self.sorting = self.buh_stati_zatrat_id.sorting
    @api.one
    @api.onchange('buh_stati_zatrat_id')
    def _buh_stati_zatrat_id(self):
        """
        Compute the total amounts.
        """

        #print "---------------------**********************"  
        if self.buh_stati_zatrat_id:
            self.sorting = self.buh_stati_zatrat_id.sorting
            


    def return_name(self):
        self.name = self.sklad_trebovanie_nakladnaya_id.name

    @api.one
    @api.depends('nomen_nomen_id')
    def _get_sklad(self):
        
        nomen_sklad = self.env['nomen.nomen_sklad_line']
        self.sklad_sklad_id = nomen_sklad.search([
                                
                                ('nomen_nomen_id', '=', self.nomen_nomen_id.id),
                                ('sklad_sklad_id', 'child_of', self.sklad_trebovanie_nakladnaya_id.sklad_sklad_id.id),

                                ], limit=1).sklad_sklad_id.id
              
        
        


    def _set_sklad(self):
        for record in self:
            if not record.sklad_sklad_id: continue
            

    name = fields.Char(string=u"Номер", required=True, compute='return_name')
    sklad_trebovanie_nakladnaya_id = fields.Many2one('sklad.trebovanie_nakladnaya', ondelete='cascade', string=u"Требование-Накладная", required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True, domain=[('is_usluga', '=', False)])
    nomen_name = fields.Char(string=u"Наименование для сортировки", compute='_nomen', store=True)
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", compute='_nomen',  store=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во", required=True)

    buh_nomen_group_id = fields.Many2one('buh.nomen_group', string='Номенклатурная группа (бух)', required=True)
    buh_stati_zatrat_id = fields.Many2one('buh.stati_zatrat', string='Статьи затрат', required=True)
    #sorting = fields.Char(string=u"С.", help="Сортировка")
    sequence = fields.Integer(string=u"Сорт.", help="Сортировка", oldname='sorting')
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', 
                                        compute='_get_sklad', 
                                        inverse='_set_sklad', 
                                        store=True)









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
            if pp.state == 'confirmed':
                raise exceptions.ValidationError(_(u"Документ №%s Проведен и не может быть удален!" % (pp.name)))

        return super(sklad_spisanie, self).unlink()


    name = fields.Char(string=u"Номер", required=True, copy=False, index=True, default='New')
    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', required=True)
    sklad_spisanie_line = fields.One2many('sklad.spisanie_line', 'sklad_spisanie_id', string=u"Строка Списание товаров", copy=True)
    mol_id = fields.Many2one('res.partner', string='МОЛ')
    utverdil_id = fields.Many2one('res.partner', string='Утвердил')
    predsedatel_id = fields.Many2one('res.partner', string='Председатель')
    chlen1_id = fields.Many2one('res.partner', string='Член1')
    chlen2_id = fields.Many2one('res.partner', string='Член2')
    chlen3_id = fields.Many2one('res.partner', string='Член3')
    #chlen4_id = fields.Many2one('res.partner', string='Член4')
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
            # vals = []
            # for line in doc.sklad_spisanie_line:
            #     vals.append({
            #                  'name': line.nomen_nomen_id.name, 
            #                  'sklad_sklad_id': doc.sklad_sklad_id.id, 
            #                  'nomen_nomen_id': line.nomen_nomen_id.id, 
            #                  'kol': line.kol, 
            #                 })

                #print "++++++++++++++++++++++++++++++++++++++++++++", doc.sklad_sklad_id.id
            sklad_ostatok = self.env['sklad.ostatok']    
            if sklad_ostatok.reg_move_draft(doc)==True:
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
            sklad_ostatok = self.env['sklad.ostatok']    
            if sklad_ostatok.reg_move(doc, vals, 'rashod')==True:
                self.state = 'confirmed'





    @api.multi
    def action_done(self):
        self.state = 'done'


class sklad_spisanie_line(models.Model):
    _name = 'sklad.spisanie_line'
    _description = u'Списание товаров строки'
    _order = 'sequence'

    @api.one
    @api.depends('nomen_nomen_id')
    def _nomen(self):
        """
        Compute the total amounts.
        """

        #print "---------------------**********************"  
        if self.nomen_nomen_id:
            # func_model = self.env['nomen.ed_izm']
            # function = func_model.search([('name', '=', self.nomen_nomen_id.ed_izm_id.name)]).id
            self.ed_izm_id = self.nomen_nomen_id.ed_izm_id
            self.nalog_nds_id = self.nomen_nomen_id.nalog_nds_id


    def return_name(self):
        self.name = self.sklad_spisanie_id.name

    @api.one
    @api.depends('nomen_nomen_id')
    def _get_sklad(self):
        
        nomen_sklad = self.env['nomen.nomen_sklad_line']
        self.sklad_sklad_id = nomen_sklad.search([
                                
                                ('nomen_nomen_id', '=', self.nomen_nomen_id.id),
                                ('sklad_sklad_id', 'child_of', self.sklad_spisanie_id.sklad_sklad_id.id),

                                ], limit=1).sklad_sklad_id.id
              
        
        


    def _set_sklad(self):
        for record in self:
            if not record.sklad_sklad_id: continue

    name = fields.Char(string=u"Номер", required=True, compute='return_name')
    sklad_spisanie_id = fields.Many2one('sklad.spisanie', ondelete='cascade', string=u"Списание", required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True, domain=[('is_usluga', '=', False)])
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", compute='_nomen',  store=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во", required=True)
    amaunt = fields.Float(digits=(10, 2), string=u"Сумма", required=True)
    osnovanie = fields.Text(string=u"Основание")
    sequence = fields.Integer(string=u"Сорт.", help="Сортировка")
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', 
                                        compute='_get_sklad', 
                                        inverse='_set_sklad', 
                                        store=True)




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
            if pp.state == 'confirmed':
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
            # vals_prihod = []
            # vals_rashod = []
            # for line in doc.sklad_inventarizaciya_line:
            #     if line.kol_otk>0:
            #         vals_prihod.append({
            #                      'name': line.nomen_nomen_id.name, 
            #                      'sklad_sklad_id': doc.sklad_sklad_id.id, 
            #                      'nomen_nomen_id': line.nomen_nomen_id.id, 
            #                      'kol': line.kol_otk, 
            #                     })
            #     if line.kol_otk<0:
            #         vals_rashod.append({
            #                      'name': line.nomen_nomen_id.name, 
            #                      'sklad_sklad_id': doc.sklad_sklad_id.id, 
            #                      'nomen_nomen_id': line.nomen_nomen_id.id, 
            #                      'kol': line.kol_otk, 
            #                     })
                      

                #print "++++++++++++++++++++++++++++++++++++++++++++", doc.sklad_sklad_id.id
            sklad_ostatok = self.env['sklad.ostatok'] 
            if sklad_ostatok.reg_move_draft(doc) == True:
                 self.state = 'draft'   
            # if ((len(vals_prihod)==0 or sklad_ostatok.reg_move(doc, vals_prihod, 'prihod-draft')==True) and 
            #     (len(vals_rashod)==0 or sklad_ostatok.reg_move(doc, vals_rashod, 'rashod-draft')==True)):
            #     self.state = 'draft'

        
    

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
                                 'sklad_sklad_id': line.sklad_sklad_id.id or doc.sklad_sklad_id.id, 
                                 'nomen_nomen_id': line.nomen_nomen_id.id, 
                                 'kol': line.kol_otk, 
                                })
                if line.kol_otk<0:
                    vals_rashod.append({
                                 'name': line.nomen_nomen_id.name, 
                                 'sklad_sklad_id': line.sklad_sklad_id.id or doc.sklad_sklad_id.id, 
                                 'nomen_nomen_id': line.nomen_nomen_id.id, 
                                 'kol': line.kol_otk, 
                                })
                      

                #print "++++++++++++++++++++++++++++++++++++++++++++", doc.sklad_sklad_id.id
            sklad_ostatok = self.env['sklad.ostatok']    
            if ((len(vals_prihod)==0 or sklad_ostatok.reg_move(doc, vals_prihod, 'prihod')==True) and 
                (len(vals_rashod)==0 or sklad_ostatok.reg_move(doc, vals_rashod, 'rashod')==True)):
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

    @api.one
    @api.depends('nomen_nomen_id')
    def _get_sklad(self):
        
        nomen_sklad = self.env['nomen.nomen_sklad_line']
        self.sklad_sklad_id = nomen_sklad.search([
                                
                                ('nomen_nomen_id', '=', self.nomen_nomen_id.id),
                                ('sklad_sklad_id', 'child_of', self.sklad_inventarizaciya_id.sklad_sklad_id.id),

                                ], limit=1).sklad_sklad_id.id
              
        
        


    def _set_sklad(self):
        for record in self:
            if not record.sklad_sklad_id: continue


    name = fields.Char(string=u"Номер", required=True, compute='return_name')
    sklad_inventarizaciya_id = fields.Many2one('sklad.inventarizaciya', ondelete='cascade', string=u"Инвентаризация", required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True, domain=[('is_usluga', '=', False)])
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", compute='_nomen',  store=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во по учету", required=True, default=0)
    kol_fact = fields.Float(digits=(10, 3), string=u"Кол-во по факту", required=True, default=0)
    kol_otk = fields.Float(digits=(10, 3), string=u"Отклонение от факта", compute='_amount',  store=True, default=0)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', 
                                        compute='_get_sklad', 
                                        inverse='_set_sklad', 
                                        store=True)




class nomen_price(models.Model):
    _name = 'nomen.price'
    _description = u'Установка цен номенклатуры'
    _order = 'date desc'

    
    @api.model
    def create(self, vals):
        #print "ssssssssssssssssssssssssssss", self.date
        if vals.get('name', 'New') == 'New' or vals.get('name', 'New') == None:
            vals['name'] = self.env['ir.sequence'].next_by_code('nomen.price') or 'New'
        if vals.get('obj_osnovaniya') == None:
             vals['obj_osnovaniya'] = ''
             vals['obj_osnovaniya_id'] = 0
            
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

    @api.multi
    def unlink(self):
        
        for pp in self:
            if pp.obj_osnovaniya:
                raise exceptions.ValidationError(_(u"Документ Установка цен %s от %s не может быть удален, т.к создан на основании %s и удаляется вместе с ним!  " % (pp.name, pp.date, pp.obj_osnovaniya)))

        return super(nomen_price, self).unlink()

    @api.one
    def _get_name_obj(self):
        if self.obj_osnovaniya!='' and self.obj_osnovaniya!=False:
            print "obj_osnovaniya=", self.obj_osnovaniya
            obj = self.env[self.obj_osnovaniya].browse(self.obj_osnovaniya_id)
            self.obj_name = obj[0]._description + u' от ' + obj[0].date
        else:
            self.obj_name = ''

    name = fields.Char(string=u"Номер", required=True, copy=False, index=True, default='New')
    date = fields.Date(string='Дата', required=True, default=fields.Datetime.now)
    nomen_price_line = fields.One2many('nomen.price_line', 'nomen_price_id', string=u"Строка Установка цен номенклатуры")
    obj_osnovaniya = fields.Char(string=u"Введен на основании объекта", copy=False, default='')
    obj_osnovaniya_id = fields.Integer(string=u"Id объекта основания", copy=False, default=0)
    obj_name = fields.Char(store=False, copy=False, compute='_get_name_obj')
    

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
 