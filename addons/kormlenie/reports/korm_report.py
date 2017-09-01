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
    _order = 'nomen_nomen_id'

    
    date = fields.Date(string='Дата')
    name = fields.Char(string='Номер документа')
    sarting = fields.Char(string='Сортировка')
    
    nomen_nomen_id = fields.Many2one('nomen.nomen', string=u'Наименование корма')
    #nomen_name = fields.Char(string='Номенклатура')
    stado_fiz_group_id = fields.Many2one('stado.fiz_group', string=u'Физ. группа')
    stado_vid_fiz_group_id = fields.Many2one('stado.vid_fiz_group', string=u'Вид физ. группы')
    kol_norma = fields.Float(digits=(10, 3), string=u"Кол-во по норме")
    kol_racion = fields.Float(digits=(10, 3), string=u"Кол-во по рациону")
    kol_fakt = fields.Float(digits=(10, 3), string=u"Кол-во по факту")
    kol_otk = fields.Float(digits=(10, 3), string=u"Кол-во отклонение")
    kol_otk_racion = fields.Float(digits=(10, 3), string=u"Кол-во откл. от рациона")



    price = fields.Float(digits=(10, 2), string=u"Цена" , group_operator="avg")
    amount_norma = fields.Float(digits=(10, 2), string=u"Сумма по норме")
    amount_racion = fields.Float(digits=(10, 2), string=u"Сумма по рациону")
    amount_fakt = fields.Float(digits=(10, 2), string=u"Сумма по факту")
    amount_otk = fields.Float(digits=(10, 2), string=u"Сумма отклонение")
    amount_otk_racion = fields.Float(digits=(10, 2), string=u"Сумма откл. от рациона")

    kol_golov = fields.Integer(string=u"Кол-во голов для расчета", group_operator="sum")
    kol_golov_srednee = fields.Integer(string=u"Кол-во голов по среднему")
    month = fields.Text(string=u"Месяц", store=True)
    year = fields.Text(string=u"Год", store=True)
    #stado_zagon_id = fields.Many2one('stado.zagon', string=u'Загон')
    
    _order = 'nomen_nomen_id desc'
    #Н462ВВ89
    def init(self, cr):

        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
            create or replace view korm_korm_svod_report as (
                WITH currency_rate as (%s)
                SELECT
                    t.id as id,
                    t.sorting as sorting,
                    t.name as name,
                    t.date as date,
                    t.month as month,
                    t.year as year,
                    t.nomen_nomen_id as nomen_nomen_id,
                    t.kol_norma as kol_norma,
                    t.kol_racion as kol_racion,
                    t.kol_fakt as kol_fakt,
                    t.kol_fakt - t.kol_norma as kol_otk,
                    t.kol_fakt - t.kol_racion as kol_otk_racion,
                    t.kol_golov as kol_golov,
                    t.kol_golov_srednee as kol_golov_srednee,
                    t.price as price,
                    t.kol_norma*t.price as amount_norma,
                    t.kol_racion*t.price as amount_racion,
                    t.kol_fakt*t.price as amount_fakt,
                    (t.kol_fakt - t.kol_norma)*t.price as amount_otk,
                    (t.kol_fakt - t.kol_racion)*t.price as amount_otk_racion,


                    t.stado_fiz_group_id,
                    t.stado_vid_fiz_group_id


                FROM (
                        select 
                                    min(s.id) as id,
                                    s.sorting::text as sorting,
                                    d.name as name,
                                    s.date as date,
                                    date_part('month',s.date) as month,
                                    to_char(s.date, 'YYYY') as year,
                                    s.nomen_nomen_id as nomen_nomen_id,
                                    sum(s.kol_norma)/count(s.id) as kol_norma,
                                    sum(rl.kol*sv.kol_golov)/count(s.id) as kol_racion,
                                    sum(s.kol_fakt)/count(s.id) as kol_fakt,
                                    sum(s.kol_fakt-s.kol_norma)/count(s.id) as kol_otk,
                                    sum(s.kol_fakt)/count(s.id)-sum(rl.kol*sv.kol_golov)/count(s.id) as kol_otk_racion,
                                    sum(sv.kol_golov) as kol_golov,
                                    avg(sv.kol_golov_zagon) as kol_golov_srednee,
                                    avg(pll.price) as price,
                                    sum(s.kol_norma)/count(s.id)*avg(pll.price) as amount_norma,
                                    sum(rl.kol*sv.kol_golov)*avg(pll.price)/count(s.id) as amount_racion,
                                    sum(s.kol_fakt)/count(s.id)*avg(pll.price) as amount_fakt,
                                    sum(s.kol_fakt-s.kol_norma)/count(s.id)*avg(pll.price) as amount_otk,
                                    (sum(s.kol_fakt)/count(s.id)-sum(rl.kol*sv.kol_golov))*avg(pll.price)/count(s.id) as amount_otk_racion,


                                    kl.stado_fiz_group_id,
                                    fg.stado_vid_fiz_group_id
                                    
                                from korm_korm_detail_line s
                                left join korm_korm_svod_line sv on 
                                                        ( sv.korm_korm_id = s.korm_korm_id and 
                                                            sv.sorting = s.sorting)
                                left join korm_korm_line kl on (kl.korm_korm_id = s.korm_korm_id and 
                                                            kl.sorting = s.sorting)
                                left join korm_korm d on (d.id = s.korm_korm_id)
                                left join stado_fiz_group fg on ( fg.id = kl.stado_fiz_group_id )
                                left join korm_racion_line rl on 
                                                            (rl.nomen_nomen_id = s.nomen_nomen_id and
                                                             rl.korm_racion_id = sv.korm_racion_id)
                                left join ( Select DISTINCT ON (pl.nomen_nomen_id)
                                                pl.price,
                                                pl.nomen_nomen_id
                                            From nomen_price_line pl
                                            Order by  pl.nomen_nomen_id, pl.date desc
                                             ) pll on (pll.nomen_nomen_id = s.nomen_nomen_id)
                             
                           
                                Group by d.name, s.date,s.sorting,
                                         date_part('month',s.date),
                                         to_char(s.date, 'YYYY'),
                                         s.nomen_nomen_id,
                                         kl.stado_fiz_group_id,
                                         fg.stado_vid_fiz_group_id
                                Order by d.name, s.date,
                                         date_part('month',s.date),
                                         to_char(s.date, 'YYYY'),
                                         s.nomen_nomen_id,
                                         kl.stado_fiz_group_id,
                                         fg.stado_vid_fiz_group_id

                        ) t
                )
        """ % self.pool['res.currency']._select_companies_rates())

    # @api.model
    # def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
    #     " Overwrite the read_group in order to sum the function field 'inventory_value' in group by "
    #     # TDE NOTE: WHAAAAT ??? is this because inventory_value is not stored ?
    #     # TDE FIXME: why not storing the inventory_value field ? company_id is required, stored, and should not create issues
    #     res = super(korm_svod_report, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
    #     print fields
    #     if 'date' in fields:
    #         for line in res:
    #             if '__domain' in line:
    #                 print '----------------------------'
    #                 print line
    #                 print '++++++++++++++++++++++++++++'
    #                 print line['__domain']

    #                 korm_ostatok_line = self.env['korm.korm_ostatok_line']
    #                 lines = korm_ostatok_line.search(line['__domain'],)
    
    #                 #lines = self.search(line['__domain'])
    #                 kol = 0.0
    #                 k = 0
    #                 for line2 in lines:
    #                     k += 1
    #                     kol += line2.kol_golov_zagon
            
    #                 line['kol_golov'] = kol
    #     return res


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


class korm_ostatok_report(models.Model):
    _name = "korm.korm_ostatok_report"
    _description = "Korm Ostatok Statistics"
    _auto = False
    _rec_name = 'stado_zagon_name'

    
    date = fields.Date(string='Дата')
    
    stado_zagon_id = fields.Many2one('stado.zagon', string=u'Загон')
    stado_zagon_name = fields.Char(string=u'Загон наименование')
    stado_fiz_group_id = fields.Many2one('stado.fiz_group', string=u'Физиологическая группа')
    kol_golov_zagon = fields.Integer(string=u"Ср. кол-во голов в загоне", group_operator="avg")
    kol_korma_norma = fields.Float(digits=(10, 3), string=u"Дача корма по норме", group_operator="sum")
    kol_korma_fakt = fields.Float(digits=(10, 3), string=u"Дача корма по факту", group_operator="sum")
    kol_korma_otk = fields.Float(digits=(10, 3), string=u"Откл.", group_operator="sum")
    
    kol_ostatok = fields.Float(digits=(10, 3), string=u"Кол-во остаток корма", group_operator="sum")
    procent_ostatkov = fields.Float(digits=(10, 1), string=u"% остатков", group_operator="avg")
    sred_kol_milk = fields.Float(digits=(10, 1), string=u"Средний надой", group_operator="avg")
    
    _order = 'stado_zagon_name'

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
            create or replace view korm_korm_ostatok_report as (
                WITH currency_rate as (%s)
                select 
                    l.id as id,
                    l.date as date,
                    l.stado_zagon_id as stado_zagon_id,
                    l.stado_fiz_group_id as stado_fiz_group_id,
                    l.kol_golov_zagon as kol_golov_zagon,
                    l.kol_korma_norma as kol_korma_norma,
                    l.kol_korma_fakt as kol_korma_fakt,
                    l.kol_korma_otk as kol_korma_otk,
                    l.kol_ostatok as kol_ostatok,
                    l.procent_ostatkov as procent_ostatkov,
                    z.name as stado_zagon_name,
                    s.sred_kol_milk as sred_kol_milk

                    
                from korm_korm_ostatok_line l
                left join stado_zagon z on 
                                        ( z.id = l.stado_zagon_id)
                left join stado_struktura_line s on
                                        (date_trunc('day',s.date) = date_trunc('day',l.date) and 
                                         s.stado_zagon_id = l.stado_zagon_id)

                )
        """ % self.pool['res.currency']._select_companies_rates())







class korm_rashod_kormov_report(models.Model):
    _name = "korm.rashod_kormov_report"
    _description = "Korm rashod kormov"
    _auto = False
    _rec_name = 'nomen_nomen_id'
    _order = 'nomen_nomen_id'

    
    date = fields.Date(string='Дата')
    
    nomen_nomen_id = fields.Many2one('nomen.nomen', string=u'Наименование корма')
    stado_zagon_id = fields.Many2one('stado.zagon', string=u'Загон')
    stado_fiz_group_id = fields.Many2one('stado.fiz_group', string=u'Физиологическая группа')
    stado_vid_fiz_group_id = fields.Many2one('stado.vid_fiz_group', string=u'Вид физ. группы')
    kol_golov_zagon = fields.Integer(string=u"Ср. кол-во голов в загоне", group_operator="avg")
    #kol_golov_zagon_sum = fields.Integer(string=u"Кол-во голов в загоне", group_operator="sum")
    kol_korma_golova = fields.Float(digits=(10, 3), string=u"Ср. Кол-во корма на голову", group_operator="sum")
    kol_fakt = fields.Float(digits=(10, 3), string=u"Кол-во по факту", group_operator="sum")
    #kol_korma_otk = fields.Float(digits=(10, 3), string=u"Откл.", group_operator="sum")
    
    #kol_ostatok = fields.Float(digits=(10, 3), string=u"Кол-во остаток корма", group_operator="sum")
    #procent_ostatkov = fields.Float(digits=(10, 1), string=u"% остатков", group_operator="avg")
    #sred_kol_milk = fields.Float(digits=(10, 1), string=u"Средний надой", group_operator="avg")
    

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
            create or replace view korm_rashod_kormov_report as (
                WITH currency_rate as (%s)
                        select 
                            s.id as id,
                            
                            s.date::date as date,
                            
                            s.nomen_nomen_id as nomen_nomen_id,
                   
                            s.kol as kol_fakt,
                            case 
                                when z.kol_golov_zagon>0 then s.kol/z.kol_golov_zagon
                                else 0
                            end as kol_korma_golova,
                            
                            s.stado_fiz_group_id as stado_fiz_group_id,
                            s.stado_zagon_id as stado_zagon_id,
                            fg.stado_vid_fiz_group_id as stado_vid_fiz_group_id,
                            z.kol_golov_zagon as kol_golov_zagon
                    
                        from reg_rashod_kormov s

                        left join stado_fiz_group fg on ( fg.id = s.stado_fiz_group_id )
                        
                        left join stado_struktura_line z on (z.date::date = s.date::date and
                                                            z.stado_zagon_id = s.stado_zagon_id)   
                        

                    )
        """ % self.pool['res.currency']._select_companies_rates())


# class korm_plan_fakt_report(models.Model):
#     _name = "korm.plan_fakt_report"
#     _description = "Korm plan fakt"
#     _auto = False
#     _rec_name = 'nomen_nomen_id'
#     _order = 'nomen_nomen_id'

    
#     year = fields.Char(string=u"Год")
#     month = fields.Char(string=u"Месяц")
    
#     nomen_nomen_id = fields.Many2one('nomen.nomen', string=u'Наименование корма')
    
#     #stado_fiz_group_id = fields.Many2one('stado.fiz_group', string=u'Физиологическая группа')
#     #stado_vid_fiz_group_id = fields.Many2one('stado.vid_fiz_group', string=u'Вид физ. группы')
#     #kol_golov_zagon = fields.Integer(string=u"Ср. кол-во голов в загоне", group_operator="avg")
#     #kol_golov_zagon_sum = fields.Integer(string=u"Кол-во голов в загоне", group_operator="sum")
#     #kol_korma_golova = fields.Float(digits=(10, 3), string=u"Кол-во корма на голову", group_operator="sum")
#     kol_fakt = fields.Float(digits=(10, 3), string=u"Кол-во по факту", group_operator="sum")
#     kol_plan = fields.Float(digits=(10, 3), string=u"Кол-во по плану", group_operator="sum")
#     prognoz = fields.Float(digits=(10, 3), string=u"Прогноз выполнения плана %", group_operator="avg")
#     kol_prognoz = fields.Float(digits=(10, 3), string=u"Кол-во прогноз", group_operator="sum")
#     price = fields.Float(digits=(10, 2), string=u"Цена", group_operator="avg")
#     sum_fakt = fields.Float(digits=(10, 2), string=u"Сумма факт", group_operator="sum")
#     sum_prognoz = fields.Float(digits=(10, 2), string=u"Сумма прогноз", group_operator="sum")
#     sum_plan = fields.Float(digits=(10, 2), string=u"Сумма план", group_operator="sum")
#     sum_otk_prognoz = fields.Float(digits=(10, 2), string=u"Сумма прогноз откл.", group_operator="sum")
#     #kol_korma_otk = fields.Float(digits=(10, 3), string=u"Откл.", group_operator="sum")
    
#     #kol_ostatok = fields.Float(digits=(10, 3), string=u"Кол-во остаток корма", group_operator="sum")
#     #procent_ostatkov = fields.Float(digits=(10, 1), string=u"% остатков", group_operator="avg")
#     #sred_kol_milk = fields.Float(digits=(10, 1), string=u"Средний надой", group_operator="avg")
    

#     def init(self, cr):
#         tools.sql.drop_view_if_exists(cr, self._table)
#         cr.execute("""
#             create or replace view korm_plan_fakt_report as (
#                 WITH currency_rate as (%s)
#                         SELECT
#                             tt.id,
#                             tt.month,
#                             tt.year,
#                             tt.nomen_nomen_id,
#                             tt.kol_plan,
#                             tt.kol_fakt,
#                             --tt.day,
#                             --tt.count_day,
#                             tt.kol_prognoz,
#                             tt.prognoz,
#                             tt.price,
#                             tt.price*tt.kol_fakt as sum_fakt,
#                             tt.price*tt.kol_prognoz as sum_prognoz,
#                             tt.price*tt.kol_plan as sum_plan,
#                             tt.price*tt.kol_prognoz-tt.price*tt.kol_plan as sum_otk_prognoz

#                         FROM (

#                                     SELECT
#                                                     min(t.id) as id,
#                                                     t.month as month,
#                                                     t.year as year,
#                                                     t.nomen_nomen_id as nomen_nomen_id,
#                                                     sum(t.kol_plan) as kol_plan,
#                                                     sum(t.kol_fakt) as kol_fakt,
#                                                     max(t.day) as day,
#                                                     max(t.count_day) as count_day,
                                        
#                                                     case
#                                                         when max(t.day)>0 then
#                                                             sum(t.kol_fakt)/max(t.day)*max(t.count_day)
#                                                         else 0
#                                                     end as kol_prognoz,
#                                                     case
#                                                         when sum(t.kol_plan)>0 and max(t.day)>0 then
#                                                             sum(t.kol_fakt)/max(t.day)*max(t.count_day)/sum(t.kol_plan)*100 
#                                                         else 0
#                                                     end as prognoz,
#                                                     --avg(npl.price) as price,
                                                    
#                                                     (Select 
#                                          np.price
#                                                     From nomen_price_line np
#                                         Where np.nomen_nomen_id = t.nomen_nomen_id and
#                                             date_trunc('month',np.date)::date<=make_date(t.year::integer, t.month::integer,1)
#                                         Order by np.date desc
#                                         Limit 1
#                                         ) as price
                                                    
                                                    
#                                                 FROM    
#                                                 (   select 
#                                                         pl.id as id,
#                                                         p.month as month,
#                                                         p.year as year,
#                                                         pl.nomen_nomen_id as nomen_nomen_id,
#                                                         pl.kol as kol_plan,
#                                                         0 as kol_fakt,
#                                                         0 as day,
#                                                         p.count_day as count_day
#                                                     from korm_plan_line pl
#                                                     left join korm_plan p on (p.id = pl.korm_plan_id)

#                                                     UNION ALL

#                                                     select
#                                                         min(s.id) as id,
#                                                         to_char(s.date, 'MM') as month,
#                                                         to_char(s.date, 'YYYY') as year,
#                                                         s.nomen_nomen_id as nomen_nomen_id,
#                                                         sum(0) as kol_plan,
#                                                         sum(s.kol) as kol_fakt,
#                                                         max(EXTRACT(day FROM s.date)) as day,
#                                                         max(EXTRACT(day FROM (date_trunc('month',s.date)+interval '1 month'-interval '1 second'))) as count_day
                                                        

#                                                     from reg_rashod_kormov s
#                                                     group by to_char(s.date, 'MM'),
#                                                         to_char(s.date, 'YYYY'),
#                                                         s.nomen_nomen_id

#                                                 ) t
                                    
                                    
#                                                 GROUP BY t.month,
#                                                     t.year,
#                                                     t.nomen_nomen_id 

#                                   ) tt
                        

#                     )
#         """ % self.pool['res.currency']._select_companies_rates())




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

        #print korms
        
        try:
            from pandas import DataFrame, pivot_table, np, orient
        except ImportError:
            pass
        datas = DataFrame(data=korms,columns=['name', 'date', 'nomen_nomen_id', 'kol_fakt'] )
        table = pivot_table(datas, values='kol_fakt', index=['date'],
                columns=['name'], aggfunc=np.sum)
        # import json
        # j1 = json.loads(table)
        # print j1


        nn = [0]
        for c in table.columns:
            #print c
            nn.append(c)
            
        rr = []
        rr.append(nn)
        for a in table.index: #Iterate through columns
            #print 'rrr=', a
            r = []
            r.append(a)
            for b in table.columns: #Iterate through rows
                #print table.ix[a,b]
                r.append(table.ix[a,b])
            rr.append(r)
        #tt = datas.reset_index().to_json(orient='index')
        print rr

        return rr

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



# SELECT
#                         *

#                 FROM (  select 
#                             min(s.id) as id,
                            
#                             date_trunc('day',s.date) as date,
                            
#                             s.nomen_nomen_id as nomen_nomen_id,
                   
#                             sum(s.kol_fakt)/count(s.id) as kol_fakt,
                            
#                             kl.stado_fiz_group_id as stado_fiz_group_id,
#                             fg.stado_vid_fiz_group_id as stado_vid_fiz_group_id
                    
#                         from korm_korm_detail_line s

#                         left join korm_korm_line kl on (kl.korm_korm_id = s.korm_korm_id and 
#                                                         kl.sorting = s.sorting)
                
#                         left join stado_fiz_group fg on ( fg.id = kl.stado_fiz_group_id )
                           
#                         Group by date_trunc('day',s.date),
                         
#                              s.nomen_nomen_id,
#                              kl.stado_fiz_group_id,
#                              fg.stado_vid_fiz_group_id
                        
#                         UNION ALL
                        
#                         Select
#                                 min(s.id) as id,
                                        
#                                 date_trunc('day',s.date) as date,
                                
#                                 s.nomen_nomen_id as nomen_nomen_id,
                           
#                                 sum(s.kol) as kol_fakt,
                                
#                                 s.stado_fiz_group_id as stado_fiz_group_id,
#                                 fg.stado_vid_fiz_group_id as stado_vid_fiz_group_id
#                         From korm_rashod_kormov_line s
                                       
#                         left join stado_fiz_group fg on ( fg.id = s.stado_fiz_group_id )
                               
#                         Group by date_trunc('day',s.date),
                             
#                              s.nomen_nomen_id,
#                              s.stado_fiz_group_id,
#                              fg.stado_vid_fiz_group_id) t1






#Запрос от 24,08,2017
# select 
#                     min(s.id) as id,
#                     d.name as name,
#                     s.date as date,
#                     date_part('month',s.date) as month,
#                     to_char(s.date, 'YYYY') as year,
#                     s.nomen_nomen_id as nomen_nomen_id,
#                     sum(s.kol_norma)/count(s.id) as kol_norma,
#                     sum(rl.kol*sv.kol_golov)/count(s.id) as kol_racion,
#                     sum(s.kol_fakt)/count(s.id) as kol_fakt,
#                     sum(s.kol_fakt-s.kol_norma)/count(s.id) as kol_otk,
#                     sum(s.kol_fakt)/count(s.id)-sum(rl.kol*sv.kol_golov)/count(s.id) as kol_otk_racion,
#                     sum(sv.kol_golov) as kol_golov,
#                     avg(sv.kol_golov_zagon) as kol_golov_srednee,
#                     avg(pll.price) as price,
#                     sum(s.kol_norma)/count(s.id)*avg(pll.price) as amount_norma,
#                     sum(rl.kol*sv.kol_golov)*avg(pll.price)/count(s.id) as amount_racion,
#                     sum(s.kol_fakt)/count(s.id)*avg(pll.price) as amount_fakt,
#                     sum(s.kol_fakt-s.kol_norma)/count(s.id)*avg(pll.price) as amount_otk,
#                     (sum(s.kol_fakt)/count(s.id)-sum(rl.kol*sv.kol_golov))*avg(pll.price)/count(s.id) as amount_otk_racion,


#                     kl.stado_fiz_group_id,
#                     fg.stado_vid_fiz_group_id
                    
#                 from korm_korm_detail_line s
#                 left join korm_korm_svod_line sv on 
#                                         ( sv.korm_korm_id = s.korm_korm_id and 
#                                             sv.sorting = s.sorting)
#                 left join korm_korm_line kl on (kl.korm_korm_id = s.korm_korm_id and 
#                                             kl.sorting = s.sorting)
#                 left join korm_korm d on (d.id = s.korm_korm_id)
#                 left join stado_fiz_group fg on ( fg.id = kl.stado_fiz_group_id )
#                 left join korm_racion_line rl on 
#                                             (rl.nomen_nomen_id = s.nomen_nomen_id and
#                                              rl.korm_racion_id = sv.korm_racion_id)
#                 left join ( Select DISTINCT ON (pl.nomen_nomen_id)
#                                 pl.price,
#                                 pl.nomen_nomen_id
#                             From nomen_price_line pl
#                             Order by  pl.nomen_nomen_id, pl.date desc
#                              ) pll on (pll.nomen_nomen_id = s.nomen_nomen_id)
             
           
#                 Group by d.name, s.date,
#                          date_part('month',s.date),
#                          to_char(s.date, 'YYYY'),
#                          s.nomen_nomen_id,
#                          kl.stado_fiz_group_id,
#                          fg.stado_vid_fiz_group_id
#                 Order by d.name, s.date,
#                          date_part('month',s.date),
#                          to_char(s.date, 'YYYY'),
#                          s.nomen_nomen_id,
#                          kl.stado_fiz_group_id,
#                          fg.stado_vid_fiz_group_id