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


    name = fields.Char(string=u"Номер", required=True, copy=False, index=True, default='New')
    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now)
    sklad_sklad_id = fields.Many2one('sklad.sklad', string='Склад', required=True)
    kombikorma_proizvodstvo_line = fields.One2many('kombikorma.proizvodstvo_line', 'kombikorma_proizvodstvo_id', string=u"Строка ингредиентов")
    mol_id = fields.Many2one('res.partner', string='МОЛ')
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Комбикорм', required=True)
    
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
            for line in doc.kombikorma_proizvodstvo_line:
                vals.append({
                             'name': line.nomen_nomen_id.name, 
                             'sklad_sklad_id': doc.sklad_sklad_id.id, 
                             'nomen_nomen_id': line.nomen_nomen_id.id, 
                             'kol': line.kol, 
                            })

                
                
            if reg_ostatok_move(self, vals, 'rashod-draft')==True:
                self.state = 'draft'

        
    

    @api.multi
    def action_confirm(self):
        #self.write({'state': 'confirmed'})
        
        for doc in self:
            vals = []
            for line in doc.kombikorma_proizvodstvo_line:
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


class kombikorma_proizvodstvo_line(models.Model):
    _name = 'kombikorma.proizvodstvo_line'
    _description = u'Производство комбикормов строки'
    _order = 'sequence'



    def return_name(self):
        self.name = self.kombikorma_proizvodstvo_id.name

    name = fields.Char(string=u"Номер", required=True, compute='return_name')
    kombikorma_proizvodstvo_id = fields.Many2one('kombikorma.proizvodstvo', ondelete='cascade', string=u"Списание", required=True)
    nomen_nomen_id = fields.Many2one('nomen.nomen', string='Номенклатура', required=True)
    ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", related='nomen_nomen_id.ed_izm_id', readonly=True,  store=True)
    kol = fields.Float(digits=(10, 3), string=u"Кол-во", required=True)
    sequence = fields.Integer(string=u"Сорт.", help="Сортировка")


