# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import tools
from openerp import models, fields, api
from datetime import datetime, timedelta, date
from openerp.exceptions import ValidationError
from ..models.work_date import week_magic, last_day_of_month

class sale_milk_report(models.Model):
    _name = "milk.sale_milk_report"
    _description = "Sales Milk Statistics"
    _auto = False
    _rec_name = 'date_ucheta'

    
    date_ucheta = fields.Date(string='Дата', readonly=True)
   
    fact_zachet = fields.Float(digits=(10, 3),string='Факт Зачетный вес', readonly=True)
    plan_zachet = fields.Float(digits=(10, 3),string='План Зачетный вес', readonly=True, group_operator="avg")
    otk_zachet = fields.Float(digits=(10, 3),string='Откл Зачетный вес', readonly=True)

    _order = 'date_ucheta desc'

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
            create or replace view milk_sale_milk_report as (
                WITH currency_rate as (%s)
                select 
                    min(s.id) as id,
                    s.date_ucheta as date_ucheta,
                    
                    sum(s.amount_ves_zachet/1000) as fact_zachet,
                    
                    avg(p.zachet) as plan_zachet,
                    sum(s.amount_ves_zachet/1000)-avg(p.zachet)/avg(p.count_day) as otk_zachet
                from milk_sale_milk s
                    left join milk_plan_sale_milk p on (p.month=to_char(s.date_ucheta, 'MM') and 
                                        p.year=to_char(s.date_ucheta, 'YYYY'))
                group by s.date_ucheta 
                order by s.date_ucheta
                    
            )
        """ % self.pool['res.currency']._select_companies_rates())

import json
class sale_milk_dashboard(models.Model):
    _name = "milk.sale_milk_dashboard"
    _description = "Sales Milk Dashboard"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    now_date = date.today() # Текущая дата (без времени)
    now_year = now_date.year # Год текущий
    now_month = now_date.month # Месяц текущий

    @api.one
    # @api.depends('zachet_fact')
    def return_prognoz(self):
        now_date = date.today() # Текущая дата (без времени)
        now_year = now_date.year # Год текущий
        now_month = now_date.month # Месяц текущий
        self.zachet_otk = self.zachet_fact - self.zachet_plan
        self.visible = 'False'
        #print u"Из запроса %s Из объекта %s" % (self.month, now_month)
        #Если это текущий месяц то выводим Производство за день и Показатели эффективности
        #расчытываем прогноз выполнения плана
        if int(self.month) == now_month and int(self.year) == now_year:
            self.visible = 'True'
            #print "Год и месяц совпадают"
            # self.env.cr.execute(""" select id from milk_trace_milk 
            #                         where date_doc<='%s' 
            #                         Order by date_doc desc LIMIT 1;""" % (now_date))
            # p = self.env.cr.fetchone()
            tm = self.env['milk.trace_milk'].search([('date_doc', '<=', now_date)], order='date_doc desc', limit=1)
            if len(tm)>0:

                trace_milk = tm[0]
                self.date_end = trace_milk.date_doc
                self.nadoy_doy = trace_milk.nadoy_doy
                self.nadoy_fur = trace_milk.nadoy_fur
                self.otk_nadoy_doy = trace_milk.otk_nadoy_doy
                self.valoviy_nadoy = trace_milk.valoviy_nadoy
                self.otk_valoviy_nadoy = trace_milk.otk_valoviy_nadoy
                self.cow_fur = trace_milk.cow_fur
                self.sale_natura = trace_milk.sale_natura/1000
                self.sale_zachet = trace_milk.sale_zachet/1000
                #РАСЧЕТ ПРОГНОЗА
                # last_document_day = datetime.strptime(trace_milk.date_doc, "%Y-%m-%d").date()
                #now_day = last_document_day.days
                last_day_month = last_day_of_month(trace_milk.date_doc)
                day_month = last_day_month.day
                # ostalos_dney = int(last_day_month) - int(now_day)
                ostalos_dney = last_day_month - datetime.strptime(trace_milk.date_doc, "%Y-%m-%d").date()
                print 'dddddddddddd===', ostalos_dney.days
                
                v_den = self.zachet_plan/day_month
                self.zachet_prognoz = (self.zachet_fact + v_den*ostalos_dney.days)/self.zachet_plan*100
                
                if trace_milk.valoviy_nadoy>0:
                    from openerp.tools.float_utils import float_round
                    #koef_tovarnosti = round(trace_milk.sale_natura, 2)/round(trace_milk.valoviy_nadoy, 2)
                    self.koef_tovarnosti = round(trace_milk.sale_natura, 2)/round(trace_milk.valoviy_nadoy, 2)
                    #print "tttttttttttttt", koef_tovarnosti
                    
                if trace_milk.sale_natura>0:
                    self.koef_zachet = round(trace_milk.sale_zachet,2)/round(trace_milk.sale_natura, 2)
                self.sale_jir = trace_milk.sale_jir
                self.sale_belok = trace_milk.sale_belok
                
                pre_tm = self.env['milk.trace_milk'].search([('date_doc', '<', self.date_end)], order='date_doc desc', limit=1)
                if len(tm)>0:
                    pre_trace_milk = pre_tm[0]
                    if pre_trace_milk.valoviy_nadoy>0:
                        self.otk_koef_tovarnosti = self.koef_tovarnosti - round(pre_trace_milk.sale_natura,2)/round(pre_trace_milk.valoviy_nadoy,2)
                    if pre_trace_milk.sale_natura>0:
                        self.otk_koef_zachet = self.koef_zachet - round(pre_trace_milk.sale_zachet,2)/round(pre_trace_milk.sale_natura,2)
                    self.otk_sale_jir = self.sale_jir - pre_trace_milk.sale_jir
                    self.otk_sale_belok = self.sale_belok - pre_trace_milk.sale_belok

                    self.izmenenie_viruchki = self.otk_koef_zachet*trace_milk.sale_natura*self.price

        else: 
            #Расчитываем фактическое исполнения плана
            if self.zachet_plan>0:
                self.zachet_prognoz = self.zachet_fact/self.zachet_plan*100


        self.amount_sale_fact = self.zachet_fact * self.price
        self.natura_otk = self.natura_fact - self.natura_plan
        self.env.cr.execute("""select
                    sum(p.zachet) as zachet_plan
                 from milk_plan_sale_milk p
                 where p.month='06'""")
        p = self.env.cr.fetchall()
        for l in p:
            print "pppppppppppppppp======", l
        print "vvvvvvvvvv-===", self.visible
        
    date = fields.Date(string='Дата', readonly=True)
    month = fields.Text(string='Месяц', readonly=True)
    year = fields.Text(string='Год', readonly=True)
    zachet_fact = fields.Float(digits=(10, 1),string='Зачетный вес (факт), тонн', readonly=True)
    zachet_plan = fields.Float(digits=(10, 1),string='Зачетный вес (план), тонн', readonly=True)
    zachet_otk = fields.Float(digits=(10, 1),string='Откл. Зачетный вес', readonly=True, compute='return_prognoz')
    zachet_prognoz = fields.Float(digits=(10, 1),string='% выполнения плана', store=False, compute='return_prognoz')
    
    price = fields.Float(digits=(10, 2),string='Цена', readonly=True, default=0, group_operator="avg")

    natura_fact = fields.Float(digits=(10, 1),string='Вес в натуре (факт), тонн', readonly=True)
    natura_plan = fields.Float(digits=(10, 1),string='Вес в натуре (план), тонн', readonly=True)
    natura_otk = fields.Float(digits=(10, 1),string='Откл. вес в натуре', readonly=True, compute='return_prognoz')

    date_end = fields.Date(string='Дата', readonly=True, compute='return_prognoz')
    nadoy_doy = fields.Float(digits=(10, 2),string='Надой на дойную', readonly=True, compute='return_prognoz', group_operator="avg")
    nadoy_fur = fields.Float(digits=(10, 2),string='Надой на фуражную', readonly=True, compute='return_prognoz', group_operator="avg")
    otk_nadoy_doy = fields.Float(digits=(10, 2),string='Откл. Надой на дойную', readonly=True, compute='return_prognoz', group_operator="avg")
    valoviy_nadoy = fields.Float(digits=(10, 0),string='Валовый надой', readonly=True, compute='return_prognoz')
    otk_valoviy_nadoy = fields.Float(digits=(10, 0),string='Откл. Валовый надой', readonly=True, compute='return_prognoz')
    cow_fur = fields.Integer(string='Поголовье (фуражное)', readonly=True, compute='return_prognoz', group_operator="avg")
    sale_natura = fields.Float(digits=(10, 2),string="Реализованно за день в натуре, тонн", compute='return_prognoz')
    sale_zachet = fields.Float(digits=(10, 2),string="Реализованно за день в зачетном весеб тонн", compute='return_prognoz')
    amount_sale_fact = fields.Float(digits=(10, 1),string="Выручка (факт), тыс.руб.")
    amount_sale_plan = fields.Float(digits=(10, 1),string="Выручка (план), тыс.руб.")
    otk_amount_sale = fields.Float(digits=(10, 1),string="Откл. выручка, тыс.руб.")
    
    koef_tovarnosti = fields.Float(digits=(10, 2), string="Коэффициент товарности", compute='return_prognoz')
    koef_zachet = fields.Float(digits=(10, 2),string="Коэффициент зачетного веса", compute='return_prognoz')
    sale_jir = fields.Float(digits=(10, 1),string="Жир", compute='return_prognoz', group_operator="avg")
    sale_belok = fields.Float(digits=(10, 2),string="Белок", compute='return_prognoz', group_operator="avg")
    otk_koef_tovarnosti = fields.Float(digits=(10, 2),string="Коэффициент товарности", compute='return_prognoz')
    otk_koef_zachet = fields.Float(digits=(10, 2),string="Коэффициент зачетного веса", compute='return_prognoz')
    otk_sale_jir = fields.Float(digits=(10, 2),string="Жир", compute='return_prognoz')
    otk_sale_belok = fields.Float(digits=(10, 2),string="Белок", compute='return_prognoz')
    izmenenie_viruchki = fields.Integer(string="Изменение выручки от измнения жира/белка", compute='return_prognoz')
    

    visible = fields.Text(string='Видимый', readonly=True, compute='return_prognoz')

    def init(self, cr):

        print "ddddddddddddddddddddddddddd"
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
            create or replace view milk_sale_milk_dashboard as (
                select  sm.id, 
                        sm.date,
                        sm.month,
                        sm.year,
                        sm.zachet_fact/1000 as zachet_fact, 
                        sm1.natura/1000 as natura_fact,
                        p.zachet_plan, 
                        p.natura_plan, 
                        p.amount_sale_plan as amount_sale_plan, 
                        p.price*sm.zachet_fact/1000 as amount_sale_fact, 
                        p.price,
                        p.price*sm.zachet_fact/1000-p.amount_sale_plan as otk_amount_sale

                        
                        

                from 
                ( select
                    max(sm.date_ucheta) as date,
                    max(to_char(sm.date_ucheta, 'MM')) as month,
                    max(to_char(sm.date_ucheta, 'YYYY')) as year,   
                    min(sm.id) as id,
                     
                    sum(sm.amount_ves_zachet) as zachet_fact
                    from milk_sale_milk sm
                    Group by to_char(sm.date_ucheta, 'MM'), to_char(sm.date_ucheta, 'YYYY')
                ) sm
                FULL OUTER JOIN
                ( select
                    max(to_char(date_ucheta, 'MM')) as month,
                    sum(amount_ves_natura) as natura,
                    max(to_char(date_ucheta, 'YYYY')) as year
                    from milk_sale_milk
                    Group by to_char(date_ucheta, 'MM'), to_char(date_ucheta, 'YYYY')
                ) sm1 ON sm1.month=sm.month and sm1.year=sm.year
                FULL OUTER JOIN
                ( select
    
                    max(month) as month,
                    max(year) as year,
                    sum(p.zachet) as zachet_plan,
                    sum(p.natura) as natura_plan,
                    sum(p.amount_nds) as amount_sale_plan,
                    max(p.price) as price
                 from milk_plan_sale_milk p
                 group by month, year

                ) p ON p.month=sm.month and p.year=sm.year
            order by sm.year, sm.month
            )""")
        
    # @api.model
    # def some_method(self):

    #     return {"kkk" : 15}