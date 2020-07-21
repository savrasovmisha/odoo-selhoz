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
    description = fields.Text(string=u"Коментарии")

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
    


class rast_kultura(models.Model):
    _name = 'rast.kultura'
    _description = u'Справочник Список культур'
    _order = 'name'

    
    name = fields.Char(string=u"Наименование", required=True, copy=False, index=True)
    active = fields.Boolean(string=u"Используется", default=True)


class rast_naznachenie(models.Model):
    _name = 'rast.naznachenie'
    _description = u'Справочник Назначение культур'
    _order = 'name'

    
    name = fields.Char(string=u"Наименование", required=True, copy=False, index=True)
    


class rast_polya_fizsvoystva(models.Model):
    _name = 'rast.polya_fizsvoystva'
    _description = u'Справочник Физичиские свойства поля'
    _order = 'name'

    
    name = fields.Char(string=u"Наименование", required=True, copy=False, index=True)
    active = fields.Boolean(string=u"Используется", default=True)






class rast_norm(models.Model):
    _name = 'rast.norm'
    _description = u'Справочник Нормы'
    _order = 'date desc'

    @api.one
    @api.depends('rast_kultura_id')
    def return_name(self):
        self.name = self.rast_kultura_id.name
    
    name = fields.Char(string=u"Имя", compute='return_name', store=True)
    date = fields.Date(string='Дата начала', required=True)
    
    rast_kultura_id = fields.Many2one('rast.kultura', string='Культура', required=True)    
    rast_naznachenie_id = fields.Many2one('rast.naznachenie', string='Назначение', required=True)    
    description = fields.Text(string=u"Коментарии")


    rast_norm_line = fields.One2many('rast.norm_line', 'rast_norm_id', string=u"Строка таблицы Нормы")
    

class rast_norm_line(models.Model):
    _name = 'rast.norm_line'
    _description = u'Справочник Нормы - Материалы'
    

    @api.one
    @api.depends('rast_norm_id.name',
                    'rast_norm_id.date',
                    'rast_norm_id.rast_kultura_id',
                    'rast_norm_id.rast_naznachenie_id')
    def return_name(self):
        self.name = self.rast_norm_id.name
        self.date = self.rast_norm_id.date
        self.rast_kultura_id = self.rast_norm_id.rast_kultura_id
        self.rast_naznachenie_id = self.rast_norm_id.rast_naznachenie_id
    
    name = fields.Char(string=u"Номер", compute='return_name', index=True)
    date = fields.Date(string='Дата начала', compute='return_name', store=True)
    rast_kultura_id = fields.Many2one('rast.kultura', string='Культура', compute='return_name', store=True)    
    rast_naznachenie_id = fields.Many2one('rast.naznachenie', string='Назначение', compute='return_name', store=True)    
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True, domain=[('is_usluga', '=', False)])
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", related='nomen_nomen_id.ed_izm_id', readonly=True,  store=True)
    kol_norma_ga = fields.Float(digits=(10, 3), string=u"Норма на 1 га", required=True)
    
    rast_norm_id = fields.Many2one('rast.norm', ondelete='cascade', string=u"Справочник Нормы", required=True)
    






class rast_spp(models.Model):
    _name = 'rast.spp'
    _description = u'Справочник Структура посевных площадей'
    _order = 'name'

    @api.one
    @api.depends('rast_polya_id')
    def _get_ploshad_polya(self):
        if self.rast_polya_id:
            self.ploshad_max = self.rast_polya_id.ploshad

    @api.one
    @api.depends('ploshad', 'urojay', 'refakciya')
    def _get_sbor(self):
        self.valoviy_sbor = self.urojay * self.ploshad / 10
        self.zachetniy_ves = self.valoviy_sbor * (100 - self.refakciya) / 100 
    
    
    name = fields.Char(string=u"Наименование", required=True, copy=False, index=True)
    date = fields.Date(string='Дата', required=True)
    rast_polya_id = fields.Many2one('rast.polya', string='Поле', required=True)    
    ploshad = fields.Float(digits=(10, 1), string=u"Прощадь, га", required=True)
    ploshad_max = fields.Float(digits=(10, 1), string=u"Макс. возможная, га", readonly=True, compute='_get_ploshad_polya')
    rast_kultura_id = fields.Many2one('rast.kultura', string='Культура', required=True)    
    rast_naznachenie_id = fields.Many2one('rast.naznachenie', string='Назначение', required=True)    
    buh_nomen_group_id = fields.Many2one('buh.nomen_group', string='Номенклатурная группа (бух)')
    rast_polya_fizsvoystva_id = fields.Many2one('rast.polya_fizsvoystva', string='Физичиские св-ва поля')
    year = fields.Char(string=u"Год", required=True, default=str(datetime.today().year))
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Продукция', required=True, domain=[('is_usluga', '=', False)])
    urojay = fields.Float(digits=(10, 1), string=u"Урожайность, ц/га", group_operator="avg")
    valoviy_sbor = fields.Float(digits=(10, 1), string=u"Валовый сбор, т", compute='_get_sbor', store=True)
    refakciya = fields.Float(digits=(10, 1), string=u"Планируемая рефакция, %", default=10, group_operator="avg")
    zachetniy_ves = fields.Float(digits=(10, 1), string=u"Зачетный вес, т", compute='_get_sbor', store=True)
    
    active = fields.Boolean(string=u"Используется", default=True)
    description = fields.Text(string=u"Коментарии")





class rast_akt_rashod(models.Model):
    _name = 'rast.akt_rashod'
    _description = u'Акт расхода'
    _order = 'name'


    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New' or vals.get('name', 'New') == None:
            vals['name'] = self.env['ir.sequence'].next_by_code('rast.akt_rashod') or 'New'
            vals['state'] = 'draft'


        result = super(rast_akt_rashod, self).create(vals)
        return result

    @api.multi
    def unlink(self):
        for pp in self:
            if pp.state == 'confirmed':
                raise exceptions.ValidationError(_(u"Документ №%s Проведен и не может быть удален!" % (pp.name)))

        return super(rast_akt_rashod, self).unlink()

    
    name = fields.Char(string=u"Номер", required=True, copy=False, index=True, default='New')
    rast_akt_rashod_line = fields.One2many('rast.akt_rashod_line', 'rast_akt_rashod_id', string=u"Строка Акта расхода")
    
    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', required=True)
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
            if sklad_ostatok.reg_move_draft(doc) == True:
                 self.state = 'draft'   

  
    

    @api.multi
    def action_confirm(self):
        for doc in self:
            vals_prihod = []
            vals_rashod = []
            for line in doc.rast_akt_rashod_line:
                vals_rashod.append({
                                 'name': line.nomen_nomen_id.name, 
                                 'sklad_sklad_id': line.sklad_sklad_id.id or doc.sklad_sklad_id.id, 
                                 'nomen_nomen_id': line.nomen_nomen_id.id, 
                                 'kol': line.kol_fact, 
                                })
                      

                #print "++++++++++++++++++++++++++++++++++++++++++++", doc.sklad_sklad_id.id
            sklad_ostatok = self.env['sklad.ostatok']    
            if sklad_ostatok.reg_move(doc, vals_rashod, 'rashod')==True:
                self.state = 'confirmed'





    @api.multi
    def action_done(self):
        self.state = 'done'







class rast_akt_rashod_line(models.Model):
    _name = 'rast.akt_rashod_line'
    _description = u'Строки Акт расхода'

    

    @api.one
    @api.depends('nomen_nomen_id','rast_spp_id')
    def _get_norma(self):
        norma = self.env['rast.norm_line']
        self.kol_norma_ga = norma.search([
                                
                                ('nomen_nomen_id', '=', self.nomen_nomen_id.id),
                                ('rast_kultura_id', '=', self.rast_spp_id.rast_kultura_id.id),
                                ('date', '<=', self.rast_akt_rashod_id.date),

                                ], order="date desc", limit=1).kol_norma_ga or 0




    @api.one
    @api.depends('kol_norma','kol_fact','ploshad','kol_norma_ga')
    def _amount(self):
        self.kol_norma = self.kol_norma_ga * self.ploshad
        self.kol_otk = self.kol_fact - self.kol_norma
        
    
    def return_name(self):
        self.name = self.rast_akt_rashod_id.name

    @api.one
    @api.depends('nomen_nomen_id')
    def _get_sklad(self):
        
        nomen_sklad = self.env['nomen.nomen_sklad_line']
        self.sklad_sklad_id = nomen_sklad.search([
                                
                                ('nomen_nomen_id', '=', self.nomen_nomen_id.id),
                                ('sklad_sklad_id', 'child_of', self.rast_akt_rashod_id.sklad_sklad_id.id),

                                ], limit=1).sklad_sklad_id.id
         
        
        


    def _set_sklad(self):
        for record in self:
            if not record.sklad_sklad_id: continue


    name = fields.Char(string=u"Номер", required=True, compute='return_name')
    rast_akt_rashod_id = fields.Many2one('rast.akt_rashod', ondelete='cascade', string=u"Акт расхода", required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True, domain=[('is_usluga', '=', False)])
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", related='nomen_nomen_id.ed_izm_id', readonly=True,  store=True)
    rast_spp_id = fields.Many2one('rast.spp', string='Поле спп', required=True)
    ploshad = fields.Float(digits=(10, 1), string=u"Площ., га", related='rast_spp_id.ploshad', readonly=True,  store=True)
    
    kol_norma_ga = fields.Float(digits=(10, 3), string=u"Норма на 1 га", compute='_get_norma',  store=True, default=0)
    kol_norma = fields.Float(digits=(10, 3), string=u"Кол-во по норме", default=0, compute='_amount',  store=True)
    kol_fact = fields.Float(digits=(10, 3), string=u"Кол-во по факту", required=True, default=0)
    kol_otk = fields.Float(digits=(10, 3), string=u"Откл. от факта", compute='_amount',  store=True, default=0)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', 
                                        compute='_get_sklad', 
                                        inverse='_set_sklad', 
                                        store=True)
    buh_nomen_group_id = fields.Many2one('buh.nomen_group', string='Номенклатурная группа (бух)', related='rast_spp_id.buh_nomen_group_id', readonly=True,  store=True)
    buh_stati_zatrat_id = fields.Many2one('buh.stati_zatrat', string='Статьи затрат', required=True)
    #sequence = fields.Integer(string=u"Сорт.", help="Сортировка")




  
class rast_rashod(models.Model):
    _name = 'rast.rashod'
    _description = u'Расход'
    _order = 'date desc'

    
    @api.one
    @api.depends('date', 'voditel')
    def _get_name(self):
        self.name = self.voditel.name + u" "+ self.date


    @api.one
    @api.depends('ves_tara', 'ves_brutto')
    def _get_kol(self):
        self.kol = self.ves_brutto - self.ves_tara

    def _set_kol(self):
        for record in self:
            if not record.kol: continue


    name = fields.Char(string=u"Номер", copy=False, index=True, default='', compute='_get_name')
    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now)
    voditel = fields.Many2one('res.partner', string='Водитель', required=True)    
    rast_spp_id = fields.Many2one('rast.spp', string='Поле спп', required=True, oldname='pole')
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True) 

    ves_tara = fields.Float(digits=(10, 3), string=u"Вес тары, кг", required=True, default=0)
    ves_brutto = fields.Float(digits=(10, 3), string=u"Вес брутто, кг", required=True, default=0)
    kol = fields.Float(digits=(10, 3), string=u"Вес нетто, кг", compute='_get_kol', inverse='_set_kol', store=True)
    

    
  
class rast_prihod(models.Model):
    _name = 'rast.prihod'
    _description = u'Приход'
    _order = 'date desc'

    
    @api.one
    @api.depends('date', 'voditel')
    def _get_name(self):
        self.name = self.voditel.name + u" "+ self.date


    @api.one
    @api.depends('ves_tara', 'ves_brutto')
    def _get_kol(self):
        self.kol = self.ves_brutto - self.ves_tara

    def _set_kol(self):
        for record in self:
            if not record.kol: continue


    name = fields.Char(string=u"Номер", copy=False, index=True, default='', compute='_get_name')
    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now)
    voditel = fields.Many2one('res.partner', string='Водитель', required=True)    
    kombayner = fields.Many2one('res.partner', string='Комбайнер', required=True)    
    rast_spp_id = fields.Many2one('rast.spp', string='Поле спп', required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True) 

    ves_brutto = fields.Float(digits=(10, 3), string=u"Вес брутто, кг", required=True, default=0)
    ves_tara = fields.Float(digits=(10, 3), string=u"Вес тары, кг", required=True, default=0)
    kol = fields.Float(digits=(10, 3), string=u"Вес нетто, кг", compute='_get_kol', inverse='_set_kol', store=True)
    

          
    