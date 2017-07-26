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
    stado_fiz_group_id = fields.Many2one('stado.fiz_group', string=u'Физ. группа')
    stado_vid_fiz_group_id = fields.Many2one('stado.vid_fiz_group', string=u'Вид физ. группы')
    kol_norma = fields.Float(digits=(10, 3), string=u"Кол-во по норме")
    kol_fakt = fields.Float(digits=(10, 3), string=u"Кол-во по факту")
    kol_golov = fields.Integer(string=u"Кол-во голов для расчета")
    month = fields.Text(string=u"Месяц", store=True)
    year = fields.Text(string=u"Год", store=True)
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
                    to_char(s.date, 'MM') as month,
                    to_char(s.date, 'YYYY') as year,
                    s.nomen_nomen_id as nomen_nomen_id,
                    
                    s.kol_norma as kol_norma,
                    s.kol_fakt as kol_fakt,
                    sv.kol_golov,
                    kl.stado_fiz_group_id,
                    fg.stado_vid_fiz_group_id
                    
                from korm_korm_detail_line s
                left join korm_korm_svod_line sv on 
                                        ( sv.korm_korm_id = s.korm_korm_id and 
                                            sv.sorting = s.sorting)
                left join korm_korm_line kl on (kl.korm_korm_id = s.korm_korm_id and 
                                            kl.sorting = s.sorting)
                left join stado_fiz_group fg on ( fg.id = kl.stado_fiz_group_id )

                )
        """ % self.pool['res.currency']._select_companies_rates())



class korm_receptura_report(models.Model):
    _name = "korm.korm_receptura_report"
    _description = "Korm Receptura Statistics"
    _auto = False
    _rec_name = 'nomen_nomen_id'

    
    date = fields.Date(string='Дата')
    nomen_nomen_id = fields.Many2one('nomen.nomen', string=u'Наименование корма')
    kombikorm_name_id = fields.Many2one('nomen.nomen', string=u'Наименование комбикорма')
    kol = fields.Float(digits=(10, 3), string=u"На голову, кг")
    kol_tonna = fields.Float(digits=(10, 3), string=u"На тонну, кг")
    procent = fields.Integer(string=u"%")
    active = fields.Boolean(string=u"Используется")
    #stado_zagon_id = fields.Many2one('stado.zagon', string=u'Загон')
    
    _order = 'nomen_nomen_id desc'

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
            create or replace view korm_korm_receptura_report as (
                WITH currency_rate as (%s)
                select 
                    l.id as id,
                    d.date as date,
                    d.active as active,
                    l.nomen_nomen_id as nomen_nomen_id,
                    d.nomen_nomen_id as kombikorm_name_id,
                    
                    l.kol as kol,
                    l.kol_tonna as kol_tonna,
                    l.procent as procent
                    
                from korm_receptura_line l
                left join korm_receptura d on 
                                        ( d.id = l.korm_receptura_id)

                )
        """ % self.pool['res.currency']._select_companies_rates())



class korm_buh_report(models.Model):
    _name = "korm.buh_report"
    _description = "Korm buh report"
    #_auto = False
    # _rec_name = 'nomen_nomen_id'

    
    date = fields.Date(string='Дата')
    # nomen_nomen_id = fields.Many2one('nomen.nomen', string=u'Наименование корма')
    stado_fiz_group_id = fields.Many2one('stado.fiz_group', string=u'Физ. группа')
    stado_vid_fiz_group_id = fields.Many2one('stado.vid_fiz_group', string=u'Вид физ. группы')

    month = fields.Text(string=u"Месяц")
    year = fields.Text(string=u"Год")
    #stado_zagon_id = fields.Many2one('stado.zagon', string=u'Загон')
    
    # _order = 'nomen_nomen_id desc'

    def get_list(self):
        zapros = """ SELECT 
                        n.name,
                        v.date, 
                        v.nomen_nomen_id, 
                        
                        v.kol_fakt 
                         
                    FROM korm_korm_svod_report v
                    left join nomen_nomen n on (v.nomen_nomen_id=n.id)
                    limit 20; """ #%(self.id,)
        #print zapros
        self._cr.execute(zapros,)
        korms = self._cr.fetchall()

        print korms
        
        try:
            from pandas import DataFrame, pivot_table, np
        except ImportError:
            pass
        datas = DataFrame(data=korms,columns=['name', 'date', 'nomen_nomen_id', 'kol_fakt'] )
        table = pivot_table(datas, values='kol_fakt', index=['date'],
                columns=['name'], aggfunc=np.sum)

        print table

        return [{'dd':'dddddd'},]

    @api.multi
    def report_print(self):
        vid1 = self.read()
        
        datas = {"date":self.date, "stado_vid_fiz_group_id": "sdsd"}
        s = self.read()
        print s

        data = self.read()[0]
        datas = {
            'ids': self.ids,
            'model': 'korm.buh_report',
            'form': data,
            'get_list': self.get_list()
        }

        return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'kormlenie.report_korm_buh_report_view',
                    'datas': datas,
                }


    # def init(self, cr):
    #     tools.sql.drop_view_if_exists(cr, self._table)
    #     cr.execute("""
    #         create or replace view korm_korm_svod_report as (
    #             WITH currency_rate as (%s)
    #             select 
    #                 s.id as id,
    #                 s.date as date,
    #                 to_char(s.date, 'MM') as month,
    #                 to_char(s.date, 'YYYY') as year,
    #                 s.nomen_nomen_id as nomen_nomen_id,
                    
    #                 s.kol_norma as kol_norma,
    #                 s.kol_fakt as kol_fakt,
    #                 sv.kol_golov,
    #                 kl.stado_fiz_group_id,
    #                 fg.stado_vid_fiz_group_id
                    
    #             from korm_korm_detail_line s
    #             left join korm_korm_svod_line sv on 
    #                                     ( sv.korm_korm_id = s.korm_korm_id and 
    #                                         sv.sorting = s.sorting)
    #             left join korm_korm_line kl on (kl.korm_korm_id = s.korm_korm_id and 
    #                                         kl.sorting = s.sorting)
    #             left join stado_fiz_group fg on ( fg.id = kl.stado_fiz_group_id )

    #             )
    #     """ % self.pool['res.currency']._select_companies_rates())

