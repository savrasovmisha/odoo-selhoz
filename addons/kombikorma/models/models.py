# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError



class kombikorma_proizvodstvo(models.Model):
    _name = 'kombikorma.proizvodstvo'
    _description = u'Производство комбикормов'
    _order = 'date desc, id desc'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New' or vals.get('name', 'New') == None:
            vals['name'] = self.env['ir.sequence'].next_by_code('kombikorma.proizvodstvo') or 'New'
            vals['state'] = 'draft'


        result = super(kombikorma_proizvodstvo, self).create(vals)
        return result

    @api.multi
    def unlink(self):
        
        #print 'sssssssssssssssssssssssssssssssssssssssssssssss', self
        for pp in self:
            if pp.state != 'done':
                raise exceptions.ValidationError(_(u"Документ №%s Проведен и не может быть удален!" % (pp.name)))

        return super(kombikorma_proizvodstvo, self).unlink()



    @api.one
    @api.depends('nomen_nomen_id', 'date')
    def _get_receptura(self):
        
        korm_receptura = self.env['korm.receptura']
        self.korm_receptura_id = korm_receptura.search([
                                
                                ('nomen_nomen_id', '=', self.nomen_nomen_id.id),
                                ('date', '<=', self.date),

                                ], order="date desc", limit=1).id
              
    
    def _set_receptura(self):
        for record in self:
            if not record.sklad_sklad_id: continue


    @api.one
    def action_zapolnit(self):
        # korm_receptura_line = self.env['korm.receptura_line']
        # result = korm_receptura_line.search([
                                
        #                         ('korm_receptura_id', '=', self.korm_receptura_id.id),
        #                        ], )
        self.kombikorma_proizvodstvo_line.unlink()
        for line in self.korm_receptura_id.korm_receptura_line:
            self.kombikorma_proizvodstvo_line.create({
                                'kombikorma_proizvodstvo_id':   self.id,
                                'nomen_nomen_id':   line.nomen_nomen_id.id,
                                'kol_norma':   self.kol*line.kol_tonna/1000,
                                'kol':   self.kol*line.kol_tonna/1000,
                                })




    
    name = fields.Char(string=u"Номер", required=True, copy=False, index=True, default='New')
    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', required=True)
    kombikorma_proizvodstvo_line = fields.One2many('kombikorma.proizvodstvo_line', 'kombikorma_proizvodstvo_id', string=u"Строка ингредиентов")
    mol_id = fields.Many2one('res.partner', string='МОЛ', related='sklad_sklad_id.partner_id', readonly=True,  store=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Комбикорм', required=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во произведенно", required=True)
    korm_receptura_id = fields.Many2one(    'korm.receptura', 
                                            string='Рецептура', 
                                            required=True,
                                            compute='_get_receptura', 
                                            inverse='_set_receptura', 
                                            store=True,
                                            copy=True,
                                            domain="[('nomen_nomen_id','=',nomen_nomen_id)]")
                                            
    
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
            sklad_ostatok = self.env['sklad.ostatok']    
            if sklad_ostatok.reg_move_draft(doc)==True:
                self.state = 'draft'

        
    

    @api.multi
    def action_confirm(self):
        #self.write({'state': 'confirmed'})
        
        for doc in self:
            vals_rashod = []
            vals_prihod = []
            vals_prihod.append({
                             'name': doc.nomen_nomen_id.name, 
                             'sklad_sklad_id': doc.sklad_sklad_id.id, 
                             'nomen_nomen_id': doc.nomen_nomen_id.id, 
                             'kol': doc.kol, 
                            })
            for line in doc.kombikorma_proizvodstvo_line:
                vals_rashod.append({
                             'name': line.nomen_nomen_id.name, 
                             'sklad_sklad_id': line.sklad_sklad_id.id or doc.sklad_sklad_id.id, 
                             'nomen_nomen_id': line.nomen_nomen_id.id, 
                             'kol': line.kol, 
                            })

                #print "++++++++++++++++++++++++++++++++++++++++++++", doc.sklad_sklad_id.id
                
            sklad_ostatok = self.env['sklad.ostatok']
            if (sklad_ostatok.reg_move(doc, vals_prihod, 'prihod')==True and 
                sklad_ostatok.reg_move(doc, vals_rashod, 'rashod')==True):
                doc.state = 'confirmed' 
            else:
                err = u'Ошибка при проведении'
                raise exceptions.ValidationError(_(u"Ошибка. Документ №%s Не проведен! %s" % (doc.name, err)))
                





    @api.multi
    def action_done(self):
        self.state = 'done'


class kombikorma_proizvodstvo_line(models.Model):
    _name = 'kombikorma.proizvodstvo_line'
    _description = u'Производство комбикормов строки'
    _order = 'sequence'



    def return_name(self):
        self.name = self.kombikorma_proizvodstvo_id.name

    @api.one
    @api.depends('nomen_nomen_id')
    def _get_sklad(self):
        
        nomen_sklad = self.env['nomen.nomen_sklad_line']
        self.sklad_sklad_id = nomen_sklad.search([
                                
                                ('nomen_nomen_id', '=', self.nomen_nomen_id.id),
                                ('sklad_sklad_id', 'child_of', self.kombikorma_proizvodstvo_id.sklad_sklad_id.id),

                                ], limit=1).sklad_sklad_id.id
              
        
        


    def _set_sklad(self):
        for record in self:
            if not record.sklad_sklad_id: continue

    name = fields.Char(string=u"Номер", required=True, compute='return_name')
    kombikorma_proizvodstvo_id = fields.Many2one('kombikorma.proizvodstvo', ondelete='cascade', string=u"Списание", required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True)
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", related='nomen_nomen_id.ed_izm_id', readonly=True,  store=True)
    kol_norma = fields.Float(digits=(10, 3), string=u"Норма")
    kol = fields.Float(digits=(10, 3), string=u"Факт", required=True)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', 
                                        compute='_get_sklad', 
                                        inverse='_set_sklad', 
                                        store=True,
                                        copy=True)
    
    sequence = fields.Integer(string=u"Сорт.", help="Сортировка")


