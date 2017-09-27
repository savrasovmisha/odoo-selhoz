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
                if self.zachet_plan>0:
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




class milk_buh_report(models.Model):
    _name = "milk.buh_report"
    _description = "Milk buh report"
    

    @api.one
    @api.depends('month', 'year')
    def return_name(self):
        if self.month and self.year:
            self.name = self.year + '-' + self.month
            self.date_start = datetime.strptime(self.year+'-'+self.month+'-01', "%Y-%m-%d").date()
            last_day = last_day_of_month(self.date_start)
            self.date_end = last_day
            self.count_day = last_day.day
        #if month == '01' : month_text = u"Январь"
        if self.month == '01' : self.month_text = u"Январь"
        if self.month == '02' : self.month_text = u"Февряль"
        if self.month == '03' : self.month_text = u"Март"
        if self.month == '04' : self.month_text = u"Апрель"
        if self.month == '05' : self.month_text = u"Май"
        if self.month == '06' : self.month_text = u"Июнь"
        if self.month == '07' : self.month_text = u"Июль"
        if self.month == '08' : self.month_text = u"Август"
        if self.month == '09' : self.month_text = u"Сентябрь"
        if self.month == '10' : self.month_text = u"Октябрь"
        if self.month == '11' : self.month_text = u"Ноябрь"
        if self.month == '12' : self.month_text = u"Декабрь"

  
   
    month = fields.Selection([
        ('01', "Январь"),
        ('02', "Февряль"),
        ('03', "Март"),
        ('04', "Апрель"),
        ('05', "Май"),
        ('06', "Июнь"),
        ('07', "Июль"),
        ('08', "Август"),
        ('09', "Сентябрь"),
        ('10', "Октябрь"),
        ('11', "Ноябрь"),
        ('12', "Декабрь"),
    ], default='', required=True, string=u"Месяц")
    
    year = fields.Char(string=u"Год", required=True, default=str(datetime.today().year))
    month_text = fields.Char(string=u"Год", compute='return_name')

    date_start = fields.Date(string='Дата начала', required=True, index=True, copy=False, compute='return_name')
    date_end = fields.Date(string='Дата окончания', required=True, index=True, copy=False, compute='return_name')
    


    @api.multi
    def report_print(self):#, cr, uid, ids, context=None):
        self.ensure_one()
        import sys
        import os
        import base64
        import zipfile
        import tempfile
        from pandas import DataFrame, pivot_table
        from xlsxwriter.utility import xl_rowcol_to_cell
        import xlsxwriter
        import pandas as pd
        import numpy as np

        reload(sys)
        sys.setdefaultencoding("utf-8")
        tmp_dir = tempfile.mkdtemp()

        

        output_filename = tmp_dir + '/MilkBuhReport.xlsx'

        workbook = xlsxwriter.Workbook(output_filename, {'default_date_format': 'DD.MM.YYYY'})

        start_row_num = 13 #Начало данных таблицы
        start_col_num = 2 #Начало названий корма

        

        total_rows = 31  #Кол-во строк данных
        total_cols = 13  #Кол-во колонок в данных


        
        worksheet = workbook.add_worksheet('СП-21')
        border_format=workbook.add_format({
                                    'border':1
                                     
                                   })



        worksheet.set_column(0, 0, 14) #Задаем ширину первой колонки 

        format_table_int = workbook.add_format({
                                                    'border':1,
                                                    'font_size': 10,
                                                    'num_format': '#,##0'})
                                                    
        format_table_float = workbook.add_format({
                                                    'border':1,
                                                    'font_size': 10,
                                                    'num_format': '#,##0.00'})
                                                    
        format_table_date = workbook.add_format({
                                                    'border':1,
                                                    'font_size': 10,
                                                    'num_format': 'DD.MM.YYYY'})
        
                                                
        text_format_utv = workbook.add_format({ 'indent': True,
                                            'border':0,
                                            'align':'right',
                                            'font_size':10      })
        text_format_head = workbook.add_format({'indent': True,
                                            'border':0,
                                            'align':'left',
                                            'font_size':10      })  

        text_format_head_bold = workbook.add_format({'indent': True,
                                            'border':0,
                                            'bold': 1,
                                            'font_size':10      })                                                                  



        format_table_head = workbook.add_format({   'text_wrap': True,
                                            'border':1,
                                            'align':'center',
                                            'valign':'vcenter',
                                            'font_size':8       })
        format_table_data = workbook.add_format({   'text_wrap': True,
                                            'border':1,
                                            'align':'right',
                                            'valign':'vcenter',
                                            'font_size':10      })                                  

        ##Формат для объединенных ячеек                                 
        merge_format = workbook.add_format({
                                            'bold': 1,
                                            'border': 0,
                                            'align': 'center',
                                            'valign': 'vcenter'})   
                                                                            
        



        worksheet.write(0, total_cols-1, u'Дата составления:', text_format_utv)
        worksheet.write(0, total_cols, self.date_end, text_format_utv)
        

        worksheet.merge_range('A3:%s' % (xl_rowcol_to_cell(2, total_cols)), 
                                u'ЖУРНАЛ №%s' % (self.month), 
                                merge_format)
        worksheet.merge_range('A4:%s' % (xl_rowcol_to_cell(3, total_cols)), 
                                u'учета надоя молока за %s %s г.' % (self.month_text, self.year), 
                                merge_format)
                               
      


        worksheet.write(4, 0, u'Организация', text_format_head) 
        worksheet.write(4, 2, u'ООО "Эвика-Агро"', text_format_head_bold)   

        worksheet.write(5, 0, u'Отделений, участок', text_format_head)
        worksheet.write(5, 2, u'Животноводческий комплекс', text_format_head_bold)

        worksheet.set_row(7,20) #Задаем высоту строк с названиями 
        worksheet.set_row(8,40) #Задаем высоту строк с названиями 

        worksheet.set_column(0, 0, 14) #Задаем ширину первой колонки 
        worksheet.set_column(1, 1, 20) #Задаем ширину первой колонки 

        worksheet.merge_range('A8:A9', u'Дата', format_table_head)
        worksheet.merge_range('B8:B9', u'Фамилия, имя, отчетсво доярки (мастера машинной дойки)', format_table_head)
        
        worksheet.merge_range('C8:D8', u'Обслуживалось коров', format_table_head)
        worksheet.write(8, 2, u'всего', format_table_head)
        worksheet.write(8, 3, u'из них доилось', format_table_head)
        
        worksheet.merge_range('E8:H8', u'Надоено молока, кг', format_table_head)
        worksheet.write(8, 4, u'утром', format_table_head)
        worksheet.write(8, 5, u'в полдень', format_table_head)
        worksheet.write(8, 6, u'вечером', format_table_head)
        worksheet.write(8, 7, u'всего', format_table_head)
        
        worksheet.merge_range('I8:I9', u'Жирность, %', format_table_head)
        worksheet.merge_range('J8:J9', u'Белок, %', format_table_head)
        worksheet.merge_range('K8:K9', u'Прочие данные о качестве', format_table_head)
        worksheet.merge_range('L8:L9', u'Подпись доярки (мастера машинной дойки)', format_table_head)
        worksheet.merge_range('M8:M9', u'Всего надоено молока, кг', format_table_head)
        worksheet.merge_range('N8:N9', u'Данные о качестве', format_table_head)
        
        trace_milk = self.env['milk.trace_milk']
        trace_milk_ids = trace_milk.search([ ('date_doc',  '>=',    self.date_start),
                                               ('date_doc',  '<=',    self.date_end)
                                            ])
        row = 9
        for line in trace_milk_ids:
            worksheet.write(row, 0, line.date_doc, format_table_date)
            worksheet.write(row, 1, u'Черепанова', format_table_head) #format_table_int)
            worksheet.write(row, 2, line.cow_fur, format_table_int) 
            worksheet.write(row, 3, line.cow_doy, format_table_int) 
            worksheet.write_formula(row, 4,'{=%s/2}' % (xl_rowcol_to_cell(row, 7)), format_table_float)
            worksheet.write(row, 5, '-', format_table_int) 
            worksheet.write_formula(row, 6,'{=%s/2}' % (xl_rowcol_to_cell(row, 7)), format_table_float)
            worksheet.write(row, 7, line.valoviy_nadoy, format_table_float) 

        workbook.close()







        export_id = self.pool.get('excel.extended').create(self.env.cr, self.env.uid, 
                    {'excel_file': base64.encodestring(open(output_filename,"rb").read()), 'file_name': 'MilkBuhReport.xlsx'}, context=self.env.context)

        return{

            'view_mode': 'form',

            'res_id': export_id,

            'res_model': 'excel.extended',

            'view_type': 'form',

            'type': 'ir.actions.act_window',

            'context': self.env.context,

            'target': 'new',

            }