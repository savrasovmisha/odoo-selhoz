# -*- coding: utf-8 -*-

from __future__ import division #при делении будет возвращаться float
from openerp import models, fields, api, exceptions, _
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError


#----------------------------------------------------------
# Активы предприятия
#----------------------------------------------------------
class aktiv_categ(models.Model):
    """Категории  активов. используются для вывода иерархического вида справочника"""
    _name = 'aktiv.categ'
    _description = u'Категории активов'
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _order  = 'parent_left'
    _rec_name = 'complete_name'


    @api.one
    @api.depends('name', 'parent_id.complete_name')
    def _complete_name(self):
        """ Forms complete name of location from parent location to child location. """
        if self.parent_id.complete_name:
            self.complete_name = '%s/%s' % (self.parent_id.complete_name, self.name)
        else:
            self.complete_name = self.name


    def name_get(self):
        ret_list = []
        for parent_id in self:
            orig_location = parent_id
            name = parent_id.name
            while parent_id.parent_id:
                parent_id = parent_id.parent_id
                if not name:
                    raise UserError(_('You have to set a name for this location.'))
                name = parent_id.name + "/" + name
            ret_list.append((orig_location.id, name))
        return ret_list

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """ search full name and barcode """
        if args is None:
            args = []
        recs = self.search(['|', ('name', operator, name), ('complete_name', operator, name)] + args, limit=limit)
        return recs.name_get()


    @api.model
    def create(self, vals):
        result = super(aktiv_categ, self).create(vals)
        return result


    name = fields.Char(string=u"Наименование", required=True) 
    complete_name = fields.Char(string=u"Наименование", compute='_complete_name', store=True) 
    parent_id = fields.Many2one('aktiv.categ', string=u'Родительский элемент', index=True, ondelete='cascade')
    child_ids = fields.One2many('aktiv.categ', 'parent_id', string=u'Подчиненные элементы')
    parent_left = fields.Integer('Left Parent', index=True)
    parent_right = fields.Integer('Right Parent', index=True)






class aktiv_status(models.Model):
    """Статус активов (В работе, в ремонте и т.п"""
    _name = 'aktiv.status'
    _description = u'Статусы активов'
    _order  = 'name'
  
    name = fields.Char(string=u"Наименование", required=True) 



class aktiv_vid_rabot(models.Model):
    """Виды работ по ТОиР"""
    _name = 'aktiv.vid_rabot'
    _description = u'Виды работ'
    _order  = 'name'

 
    name = fields.Char(string=u"Наименование", required=True)
    description = fields.Text(string=u"Коментарии")

    aktiv_vid_rabot_price_line = fields.One2many('aktiv.vid_rabot_price_line', 'aktiv_vid_rabot_id', string=u"Строка Стоимость Виды работ", copy=True)


class aktiv_vid_rabot_price_line(models.Model):
    """Строка Стоимость работ"""
    _name = 'aktiv.vid_rabot_price_line'
    _description = u'Строка Стоимость работ'
    _order  = 'date desc'
    
    @api.one
    @api.depends('aktiv_vid_rabot_id.name')
    def return_name(self):
        self.name = self.aktiv_vid_rabot_id.name
    
    name = fields.Char(string=u"Наименование", compute='return_name', store=True)
    aktiv_vid_rabot_id = fields.Many2one('aktiv.vid_rabot', ondelete='cascade', string=u"Виды работ", required=True)

    date = fields.Date(string='Дата', required=True, index=True, copy=False)
    aktiv_type_id = fields.Many2one('aktiv.type', string='Тип актива', required=True)
    price = fields.Float(digits=(10, 2), string=u"Стоимость работ", required=True)
    currency_id = fields.Many2one('res.currency', string='Валюта', default=lambda self: self.env.user.company_id.currency_id.id)
    is_hozsposob = fields.Boolean(string=u"Хозспособ", default=True)
    is_podryad = fields.Boolean(string=u"Подрядный", default=False)
    partner_id = fields.Many2one('res.partner', string='Подрядчик')





class aktiv_vid_remonta(models.Model):
    """Виды ремонтов и диагностирования"""
    _name = 'aktiv.vid_remonta'
    _description = u'Виды ремонтов и диагностирования'
    _order  = 'name'
  
    name = fields.Char(string=u"Наименование", required=True)
    


class aktiv_type(models.Model):
    """Типы активов (Оборудование, транспорт и т.п"""
    _name = 'aktiv.type'
    _description = u'Типы активов'
    _order  = 'name'
  
    name = fields.Char(string=u"Наименование", required=True) 
    aktiv_tr = fields.One2many('aktiv.tr', 'aktiv_type_id', string=u"Типовые ремонты", copy=True)



class aktiv_tr(models.Model):
    """Типовые ремонты"""
    _name = 'aktiv.tr'
    _description = u'Типовые ремонты'
    _order  = 'name'

    
    @api.one
    @api.depends(   'is_raschet_price',
                    'aktiv_tr_price_line',
                    'aktiv_tr_raboti_line', 
                    'aktiv_tr_raboti_line.aktiv_vid_rabot_id.aktiv_vid_rabot_price_line',
                    'aktiv_tr_nomen_line',
                    'aktiv_tr_nomen_line.nomen_nomen_id.nomen_nomen_price_line'
                    )
    def _get_price(self):
        
        self.price_raboti = self.price_raboti = self.price_nomen = 0
        if self.is_raschet_price == True:
            if self.aktiv_tr_price_line:
                self.price_raboti = self.aktiv_tr_price_line[0].price
        else:
            for line in self.aktiv_tr_raboti_line:
                self.price_raboti += line.price

        if self.aktiv_tr_nomen_line:
            for line in self.aktiv_tr_nomen_line:
                self.price_nomen += line.amount
        self.price = self.price_raboti + self.price_nomen

  
    name = fields.Char(string=u"Наименование ремонта", required=True)

    aktiv_type_id = fields.Many2one('aktiv.type', ondelete='cascade', string='Тип актива', required=True)
    aktiv_vid_remonta_id = fields.Many2one('aktiv.vid_remonta', string='Виды ремонтов и диагностирования')

    
    is_raschet_price = fields.Boolean(string=u"Стоимость работ задается в ручную", default=True)
    price_raboti = fields.Float(digits=(10, 2), string=u"Стоимость работ", compute='_get_price', store=True)
    price_nomen = fields.Float(digits=(10, 2), string=u"Стоимость ТМЦ", compute='_get_price', store=True)
    price = fields.Float(digits=(10, 2), string=u"Общая стоимость", compute='_get_price', store=True)
    currency_id = fields.Many2one('res.currency', string='Валюта', default=lambda self: self.env.user.company_id.currency_id)
    is_hozsposob = fields.Boolean(string=u"Хозспособ", default=True)
    is_podryad = fields.Boolean(string=u"Подрядный", default=False)
    partner_id = fields.Many2one('res.partner', string='Подрядчик')

    period1 = fields.Integer(string="Интервал 1")
    period1_edizm = fields.Selection([
        ('hours', "ч."),
        ('days', "дн."),
        ('months', "мес."),
        ('years', "г."),
        ('km', "км."),
    ], default='hours', string="Ед.изм.")
    period2 = fields.Integer(string="Интервал 2")
    period2_edizm = fields.Selection([
        ('hours', "ч."),
        ('days', "дн."),
        ('months', "мес."),
        ('years', "г."),
        ('km', "км"),
    ], default='hours', string="Ед.изм.")
    
    



    aktiv_tr_raboti_line = fields.One2many('aktiv.tr_raboti_line', 'aktiv_tr_id', string=u"Строка регламентных работ. Типовые ремонты", copy=True)
    aktiv_tr_nomen_line = fields.One2many('aktiv.tr_nomen_line', 'aktiv_tr_id', string=u"Строка материалы. Типовые ремонты", copy=True)
    aktiv_tr_price_line = fields.One2many('aktiv.tr_price_line', 'aktiv_tr_id', string=u"Строка Стоимость Типовые ремонты", copy=False)


class aktiv_tr_price_line(models.Model):
    """Строка Стоимость Типовые ремонты"""
    _name = 'aktiv.tr_price_line'
    _description = u'Строка Стоимость Типовые ремонты'
    _order  = 'date desc'
    
    @api.one
    @api.depends('date')
    def return_name(self):
        self.name = self.aktiv_tr_id.name
    
    name = fields.Char(string=u"Наименование", compute='return_name', store=True)
    aktiv_tr_id = fields.Many2one('aktiv.tr', ondelete='cascade', string=u"Типовые ремонты", required=True)

    date = fields.Date(string='Дата', required=True, index=True, copy=False)
    price = fields.Float(digits=(10, 2), string=u"Стоимость работ", required=True)
    currency_id = fields.Many2one('res.currency', string=u'Валюта', default=lambda self: self.env.user.company_id.currency_id)
    is_hozsposob = fields.Boolean(string=u"Хозспособ", default=True)
    is_podryad = fields.Boolean(string=u"Подрядный", default=False)
    partner_id = fields.Many2one('res.partner', string=u'Подрядчик')


class aktiv_tr_raboti_line(models.Model):
    """Строка регламентных работ. Типовые ремонты"""
    _name = 'aktiv.tr_raboti_line'
    _description = u'Строка регламентных работ'
    _order  = 'name'


    @api.one
    @api.depends('aktiv_vid_rabot_id')
    def return_name(self):
        self.name = self.aktiv_vid_rabot_id.name


    @api.one
    @api.depends('aktiv_vid_rabot_id', 'aktiv_vid_rabot_id.aktiv_vid_rabot_price_line')
    def _get_price(self):
      
        vr_price = self.aktiv_vid_rabot_id.aktiv_vid_rabot_price_line.search([
                                                                                ('aktiv_type_id', '=', self.aktiv_tr_id.aktiv_type_id.id),
                                                                                ('aktiv_vid_rabot_id', '=', self.aktiv_vid_rabot_id.id),

                                                                            ],order="date desc", limit=1)
        if vr_price:
            self.price = vr_price[0].price
            self.currency_id = vr_price[0].currency_id
  

    name = fields.Char(string=u"Наименование", compute='return_name', store=True)
    aktiv_tr_id = fields.Many2one('aktiv.tr', ondelete='cascade', string=u"Типовые ремонты", required=True)

    aktiv_vid_rabot_id = fields.Many2one('aktiv.vid_rabot', string='Виды работ')
    

    is_hozsposob = fields.Boolean(string=u"Хозспособ", default=True)
    is_podryad = fields.Boolean(string=u"Подрядный", default=False)
    partner_id = fields.Many2one('res.partner', string='Подрядчик')
    price = fields.Float(digits=(10, 2), string=u"Стоимость", compute='_get_price', store=True)
    currency_id = fields.Many2one('res.currency', string='Валюта', compute='_get_price', store=True)

    aktiv_type_id = fields.Many2one('aktiv.type', string='Тип актива', related='aktiv_tr_id.aktiv_type_id', readonly=True,  store=True)
    aktiv_vid_remonta_id = fields.Many2one('aktiv.vid_remonta', string='Виды ремонтов и диагностирования', related='aktiv_tr_id.aktiv_vid_remonta_id', readonly=True,  store=True)


class aktiv_tr_nomen_line(models.Model):
    """Строка материалы. Типовые ремонты"""
    _name = 'aktiv.tr_nomen_line'
    _description = u'Строка материалы'
    _order  = 'name'

    @api.one
    @api.depends('nomen_nomen_id')
    def return_name(self):
        self.name = self.nomen_nomen_id.name


    @api.one
    @api.depends('nomen_nomen_id', 'nomen_nomen_id.nomen_nomen_price_line', 'kol')
    def _get_price(self):
        self.price = self.nomen_nomen_id.price
        self.currency_id = self.nomen_nomen_id.currency_id.id
        self.amount = self.price * self.kol
  
    name = fields.Char(string=u"Наименование", compute='return_name', store=True)
    aktiv_tr_id = fields.Many2one('aktiv.tr', ondelete='cascade', string=u"Типовые ремонты", required=True)

    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Материалы', required=True)
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", related='nomen_nomen_id.ed_izm_id', readonly=True,  store=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во", required=True)
    price = fields.Float(digits=(10, 2), string=u"Цена", compute='_get_price', store=True)
    currency_id = fields.Many2one('res.currency', string='Валюта', compute='_get_price', store=True)
    amount = fields.Float(digits=(10, 2), string=u"Стоимость", compute='_get_price', store=True)

    aktiv_type_id = fields.Many2one('aktiv.type', string='Тип актива', related='aktiv_tr_id.aktiv_type_id', readonly=True,  store=True)
    aktiv_vid_remonta_id = fields.Many2one('aktiv.vid_remonta', string='Виды ремонтов и диагностирования', related='aktiv_tr_id.aktiv_vid_remonta_id', readonly=True,  store=True)




class aktiv_aktiv(models.Model):
    """Активы предприятия. ОС и оборудования."""
    _name = 'aktiv.aktiv'
    _description = u'Активы (оборудование)'
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _order  = 'parent_left'
    _rec_name = 'complete_name'


    @api.one
    @api.depends('name', 'parent_id.complete_name')
    def _complete_name(self):
        """ Forms complete name of location from parent location to child location. """
        if self.parent_id.complete_name:
            self.complete_name = '%s/%s' % (self.parent_id.complete_name, self.name)
        else:
            self.complete_name = self.name


    def name_get(self):
        ret_list = []
        for parent_id in self:
            orig_location = parent_id
            name = parent_id.name
            while parent_id.parent_id:
                parent_id = parent_id.parent_id
                if not name:
                    raise UserError(_('You have to set a name for this location.'))
                name = parent_id.name + "/" + name
            ret_list.append((orig_location.id, name))
        return ret_list

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """ search full name and barcode """
        if args is None:
            args = []
        recs = self.search(['|', ('name', operator, name), ('complete_name', operator, name)] + args, limit=limit)
        return recs.name_get()


    @api.model
    def create(self, vals):
        result = super(aktiv_aktiv, self).create(vals)
        return result


    @api.one
    @api.depends('srok_slujbi_ot_vvoda', 'srok_slujbi', 'date_vipuska', 'date_vvoda')
    def _srok_slujbi(self):
        """ Forms complete name of location from parent location to child location. """
        if self.srok_slujbi:
            
            if self.srok_slujbi_ot_vvoda==True and self.date_vvoda:
                self.date_start = self.date_vvoda
            
            if self.srok_slujbi_ot_vvoda==False and self.date_vipuska:
                self.date_start = self.date_vipuska

            if self.date_start:
                date_end = fields.Date.from_string(self.date_start)# + timedelta(days=self.srok_slujbi*365)
                self.date_end = fields.Date.to_string(date_end.replace(year=date_end.year+self.srok_slujbi))
   

        

    name = fields.Char(string=u"Наименование", required=True)
    complete_name = fields.Char(string=u"Представление", compute='_complete_name', store=True) 
    parent_id = fields.Many2one('aktiv.aktiv', string=u'Входит в состав', index=True, ondelete='cascade')
    child_ids = fields.One2many('aktiv.aktiv', 'parent_id', string=u'Составные части')
    parent_left = fields.Integer('Left Parent', index=True)
    parent_right = fields.Integer('Right Parent', index=True)
    
    aktiv_categ_id = fields.Many2one('aktiv.categ', string=u"Категория", default=None)
    id_1c = fields.Char(string=u"Номер в 1С")
    active = fields.Boolean(string=u"Используется", default=True)
    is_uzel = fields.Boolean(string=u"Узел объекта", default=False)
    is_group = fields.Boolean(string=u"Это группа", default=False)

    model = fields.Char(string=u"Модель")
    kod = fields.Char(string=u"Код")
    
    inv_nomer = fields.Char(string=u"Инвентарный номер")
    serial_nomer = fields.Char(string=u"Серийный номер")
    reg_nomer = fields.Char(string=u"Регистрационный номер")
    
    zavod_nomer = fields.Char(string=u"Заводской номер")
    zavod_name = fields.Char(string=u"Завод производитель")
    country_id = fields.Many2one('res.country', string=u"Страна производитель")

    postavshik_id = fields.Many2one('res.partner', string='Поставщик')
    otvetstvenniy_id = fields.Many2one('res.partner', string='Ответственный')
    aktiv_type_id = fields.Many2one('aktiv.type', string='Тип')



    date_vipuska = fields.Date(string='Дата выпуска')
    date_postupleniya = fields.Date(string='Дата поступления')
    date_vvoda = fields.Date(string='Дата ввода в экспл.')
    date_spisaniya = fields.Date(string='Дата списания')

    aktiv_status_id = fields.Many2one('aktiv.status', string='Статус')

    price = fields.Integer(string=u"Стоимость")
    srok_slujbi = fields.Integer(string=u"Срок службы, лет")
    srok_slujbi_ot_vvoda = fields.Boolean(string=u"Срок службы от ввода в эксплуатацию", default=True)
    date_start = fields.Date(string='Срок службы, Дата начала', compute='_srok_slujbi', store=True)
    date_end = fields.Date(string='Срок службы, Дата окончания', compute='_srok_slujbi', store=True)

    teh_har = fields.Text(string=u"Технические характеристики")

    description = fields.Text(string=u"Коментарии")
    
    attachment_ids = fields.Many2many(
        'ir.attachment', 'aktiv_aktiv_ir_attachments_rel',
        'aktiv_aktiv_id', 'attachment_id', string='Вложения')



class aktiv_gr(models.Model):
    """График ремонтов"""
    _name = 'aktiv.gr'
    _description = u'График ремонтов'
    _order  = 'date_start'

    
    @api.one
    def _get_aktiv_tr(self, aktiv_aktiv_id, nomer):
        """Добавляет типовые работы"""

        n = 1
        for line in aktiv_aktiv_id.aktiv_type_id.aktiv_tr:
            nomer_txt = nomer + '.' + str(n)
            n += 1
            self.aktiv_gr_line.create({

                    "aktiv_gr_id": self.id,
                    "nomer": nomer_txt,
                    "aktiv_aktiv_id": aktiv_aktiv_id.id,
                    "aktiv_tr_id": line.id,

                })
            


    @api.one
    def _get_child_aktiv(self, paren_aktiv_id, nomer):
        """Возвращает потомков актива"""

        res = []
        n = 1
        for line in paren_aktiv_id.child_ids:
            nomer_txt = nomer + '.' + str(n)
            n += 1
            self.aktiv_gr_line.create({

                    "aktiv_gr_id": self.id,
                    "nomer": nomer_txt,
                    "aktiv_aktiv_id": line.id,
                    
                })
            self._get_aktiv_tr(line, nomer_txt)
            self._get_child_aktiv(line, nomer_txt)




    @api.one
    def action_zapolnit(self):
        """Действие при нажати на кнопку Заполнить"""
        nomer = 1
        self.aktiv_gr_line.unlink()
        self._get_aktiv_tr(self.aktiv_aktiv_id, str(nomer)) #Работы по основному объекту
        if self.aktiv_gr_line:
            self.aktiv_gr_line.create({

                    "aktiv_gr_id": self.id,
                    "nomer": str(nomer),
                    "aktiv_aktiv_id": self.aktiv_aktiv_id.id,
                   

                })
            nomer += 1
        for line in self.aktiv_aktiv_id.child_ids:
            nomer_txt = str(nomer)
                
            self.aktiv_gr_line.create({

                    "aktiv_gr_id": self.id,
                    "nomer": nomer_txt,
                    "aktiv_aktiv_id": line.id,
                   

                })
            self._get_aktiv_tr(line, str(nomer))
            self._get_child_aktiv(line, str(nomer))
            nomer += 1

        for line in self.aktiv_gr_line:
            line.return_name()

    @api.one
    def action_raschet(self):
        """Расчитать график"""
        for line in self.aktiv_gr_line:
            line.raschet()
      
    
    
    name = fields.Char(string=u"Наименование ремонта", required=True)
    year = fields.Integer(string=u"Год планирования", required=True)

    aktiv_aktiv_id = fields.Many2one('aktiv.aktiv', string='Актив')
    #is_view_price = fields.Boolean(string=u"Показать стоимость", default=False)

    date_start = fields.Date(string='Дата начала')
    date_end = fields.Date(string='Дата окончания')

    aktiv_gr_line = fields.One2many('aktiv.gr_line', 'aktiv_gr_id', string=u"Строка График ремонтов", copy=False)
    aktiv_gr_price_line = fields.One2many('aktiv.gr_line', 'aktiv_gr_id', copy=False)


class aktiv_gr_line(models.Model):
    """Строка График ремонтов"""
    _name = 'aktiv.gr_line'
    _description = u'Строка График ремонтов'
    _order  = 'nomer'

    @api.one
    def _get_price(self):
        self.amount = self.kol = 0
        self.currency_id = self.aktiv_tr_id.currency_id
        for m in range(1,13):
            self.amount += self['p'+str(m)]
            if self['m'+str(m)] == True:
                self.kol += 1


    @api.one
    def return_name(self):
        if self.aktiv_tr_id:
            self.name = self.aktiv_tr_id.name
        else:
            self.name = self.aktiv_aktiv_id.name

    @api.one
    def raschet(self):
        """Расчет графика ремонта для текущего типового ремонта"""
        if self.aktiv_tr_id:
            for m in range(1,13):
                self['m'+str(m)] = False
                self['p'+str(m)] = 0

            period = self.aktiv_tr_id.period1
            if self.aktiv_tr_id.period1_edizm == "months" and period > 0:
                #Если дата последнего ремонта определена то определяем месяц следующего ремонта
                #иначе планируем ремонт на первый месяц
                if self.date_last:
                    date_last = datetime.strptime(self.date_last, "%Y-%m-%d").date()
                    m_last = date_last.month
                    y_last = date_last.year
                    m_next = m_last
                    y_next = y_last
                    y_today = self.aktiv_gr_id.year
                    if y_last < y_today:
                        while (m_next<=12 and y_next<y_today):
                            m_next += period
                            if m_next>12:
                                y_next += 1
                                m_next = m_next - 12

                else:
                    m_next = 1

                while m_next<=12:
                    self['m'+str(m_next)] = True
                    self['p'+str(m_next)] = self.aktiv_tr_id.price
                    m_next += period
            self._get_price()

    # @api.one
    # @api.depends('aktiv_gr_id.is_view_price')
    # def _get_view_price(self):
    #     self.is_view_price = self.aktiv_gr_id.is_view_price
    
    name = fields.Char(string=u"Наименование ремонта", compute='return_name', store=True)
    nomer = fields.Char(string=u"№")
    aktiv_gr_id = fields.Many2one('aktiv.gr', ondelete='cascade', string=u"График ремонтов", required=True)

    # is_view_price = fields.Boolean(string=u"Показать стоимость", compute='_get_view_price')
    aktiv_aktiv_id = fields.Many2one('aktiv.aktiv', string='Актив')
    
    is_group = fields.Boolean(string=u"Это группа", related='aktiv_aktiv_id.is_group', stote=True)
    
    aktiv_tr_id = fields.Many2one('aktiv.tr', string='Типовые ремонты')
    
    date_last = fields.Date(string='Дата последнего ремонта')

    m1 = fields.Boolean(string=u"1", default=False)
    p1 = fields.Float(digits=(10, 2), string=u"1", compute='_get_price', store=True)

    m2 = fields.Boolean(string=u"2", default=False)
    p2 = fields.Float(digits=(10, 2), string=u"2", compute='_get_price', store=True)

    m3 = fields.Boolean(string=u"3", default=False)
    p3 = fields.Float(digits=(10, 2), string=u"3", compute='_get_price', store=True)

    m4 = fields.Boolean(string=u"4", default=False)
    p4 = fields.Float(digits=(10, 2), string=u"4", compute='_get_price', store=True)

    m5 = fields.Boolean(string=u"5", default=False)
    p5 = fields.Float(digits=(10, 2), string=u"5", compute='_get_price', store=True)

    m6 = fields.Boolean(string=u"6", default=False)
    p6 = fields.Float(digits=(10, 2), string=u"6", compute='_get_price', store=True)

    m7 = fields.Boolean(string=u"7", default=False)
    p7 = fields.Float(digits=(10, 2), string=u"7", compute='_get_price', store=True)

    m8 = fields.Boolean(string=u"8", default=False)
    p8 = fields.Float(digits=(10, 2), string=u"8", compute='_get_price', store=True)

    m9 = fields.Boolean(string=u"9", default=False)
    p9 = fields.Float(digits=(10, 2), string=u"9", compute='_get_price', store=True)

    m10 = fields.Boolean(string=u"10", default=False)
    p10 = fields.Float(digits=(10, 2), string=u"10", compute='_get_price', store=True)

    m11 = fields.Boolean(string=u"11", default=False)
    p11 = fields.Float(digits=(10, 2), string=u"11", compute='_get_price', store=True)
    
    m12 = fields.Boolean(string=u"12", default=False)
    p12 = fields.Float(digits=(10, 2), string=u"12", compute='_get_price', store=True)

    kol = fields.Float(digits=(10, 2), string=u"Кол-во", compute='_get_price', store=True)
    price = fields.Float(digits=(10, 2), string=u"Цена", compute='_get_price', store=True)
    currency_id = fields.Many2one('res.currency', string='Валюта', compute='_get_price', store=True)
    #currency_id = fields.Many2one('res.currency', string='Валюта', default=lambda self: self.env.user.company_id.currency_id.id)
    amount = fields.Float(digits=(10, 2), string=u"Стоимость", compute='_get_price', store=True)



class aktiv_remont(models.Model):
    """Ремонты"""
    _name = 'aktiv.remont'
    _description = u'Ремонты'
    _order  = 'date'

    @api.one
    @api.depends('aktiv_aktiv_id')
    def return_name(self):
        self.name = self.aktiv_aktiv_id.name

    name = fields.Char(string=u"Наименование", compute='return_name', store=True)
    
    date = fields.Date(string='Дата')

    aktiv_aktiv_id = fields.Many2one('aktiv.aktiv', string='Актив')
    
    date_start = fields.Date(string='Дата начала')
    date_end = fields.Date(string='Дата окончания')

    aktiv_tr_id = fields.Many2one('aktiv.tr', string='Типовой ремонт')


    aktiv_remont_raboti_line = fields.One2many('aktiv.remont_raboti_line', 'aktiv_remont_id', string=u"Строка регламентных работ. Ремонты", copy=True)
    aktiv_remont_nomen_line = fields.One2many('aktiv.remont_nomen_line', 'aktiv_remont_id', string=u"Строка материалы. Ремонты", copy=True)
    



class aktiv_remont_raboti_line(models.Model):
    """Строка регламентных работ. Типовые ремонты"""
    _name = 'aktiv.remont_raboti_line'
    _description = u'Строка регламентных работ'
    _order  = 'name'


    @api.one
    @api.depends('aktiv_vid_rabot_id')
    def return_name(self):
        self.name = self.aktiv_vid_rabot_id.name


    name = fields.Char(string=u"Наименование", compute='return_name', store=True)
    aktiv_remont_id = fields.Many2one('aktiv.remont', ondelete='cascade', string=u"Ремонты", required=True)

    aktiv_vid_rabot_id = fields.Many2one('aktiv.vid_rabot', string='Виды работ')
 
    price = fields.Float(digits=(10, 2), string=u"Стоимость")
    currency_id = fields.Many2one('res.currency', string='Валюта')

    

class aktiv_remont_nomen_line(models.Model):
    """Строка материалы. Ремонты"""
    _name = 'aktiv.remont_nomen_line'
    _description = u'Строка материалы'
    _order  = 'name'

    @api.one
    @api.depends('nomen_nomen_id')
    def return_name(self):
        self.name = self.nomen_nomen_id.name


    @api.one
    @api.depends('nomen_nomen_id', 'nomen_nomen_id.nomen_nomen_price_line', 'kol')
    def _get_price(self):
        self.amount = self.price * self.kol
  
    name = fields.Char(string=u"Наименование", compute='return_name', store=True)
    aktiv_remont_id = fields.Many2one('aktiv.remont', ondelete='cascade', string=u"Ремонты", required=True)

    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Материалы', required=True)
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", related='nomen_nomen_id.ed_izm_id', readonly=True,  store=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во", required=True)
    price = fields.Float(digits=(10, 2), string=u"Цена с НДС")
    currency_id = fields.Many2one('res.currency', string='Валюта', default=lambda self: self.nomen_nomen_id.currency_id)
    amount = fields.Float(digits=(10, 2), string=u"Стоимость", compute='_get_price', store=True)

    # aktiv_type_id = fields.Many2one('aktiv.type', string='Тип актива', related='aktiv_tr_id.aktiv_type_id', readonly=True,  store=True)
    # aktiv_vid_remonta_id = fields.Many2one('aktiv.vid_remonta', string='Виды ремонтов и диагностирования', related='aktiv_tr_id.aktiv_vid_remonta_id', readonly=True,  store=True)

