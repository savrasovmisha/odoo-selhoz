# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import tools
from openerp import models, fields, api
from datetime import datetime, timedelta, date
from openerp.exceptions import ValidationError


class korm_svod_report(models.Model):
    _name = "korm.korm_svod_report"
    _description = "Korm Statistics"
    _auto = False
    _rec_name = 'nomen_nomen_id'

    
    date = fields.Date(string='Дата')
    nomen_nomen_id = fields.Many2one('nomen.nomen', string=u'Наименование корма')
    kol_norma = fields.Float(digits=(10, 3), string=u"Кол-во по норме")
    kol_fakt = fields.Float(digits=(10, 3), string=u"Кол-во по факту")
    kol_golov = fields.Integer(string=u"Кол-во голов для расчета")
    #stado_zagon_id = fields.Many2one('stado.zagon', string=u'Загон')
    
    _order = 'nomen_nomen_id desc'

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
            create or replace view korm_korm_svod_report as (
                WITH currency_rate as (%s)
                select 
                    s.id as id,
                    s.date as date,
                    s.nomen_nomen_id as nomen_nomen_id,
                    
                    s.kol_norma as kol_norma,
                    s.kol_fakt as kol_fakt,
                    sv.kol_golov
                from korm_korm_detail_line s
                left join korm_korm_svod_line sv on 
                                        ( sv.korm_korm_id = s.korm_korm_id and 
                                            sv.sorting = s.sorting)

                )
        """ % self.pool['res.currency']._select_companies_rates())
