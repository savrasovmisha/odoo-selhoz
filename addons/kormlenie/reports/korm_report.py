# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import tools
from openerp import models, fields, api
from datetime import datetime, timedelta, date
from openerp.exceptions import ValidationError

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

def week_magic(day):
	if type(day)==str:
		day = datetime.strptime(day, "%Y-%m-%d").date()
	day_of_week = day.weekday()

	to_beginning_of_week = timedelta(days=day_of_week)
	beginning_of_week = day - to_beginning_of_week

	to_end_of_week = timedelta(days=6 - day_of_week)
	end_of_week = day + to_end_of_week
	number_of_week = day.isocalendar()[1]

	return (beginning_of_week, end_of_week, number_of_week)

def last_day_of_month(date):
	if type(date)==str:
		date = datetime.strptime(date, "%Y-%m-%d").date()
	if date.month == 12:
		return date.replace(day=31)
	return date.replace(month=date.month+1, day=1) - timedelta(days=1)



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
	stado_podvid_fiz_group_id = fields.Many2one('stado.podvid_fiz_group', string=u'Подвид физ. группы')
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
					t.stado_vid_fiz_group_id,
					t.stado_podvid_fiz_group_id


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
									fg.stado_vid_fiz_group_id,
									fg.stado_podvid_fiz_group_id
									
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
										 fg.stado_vid_fiz_group_id,
										 fg.stado_podvid_fiz_group_id
								Order by d.name, s.date,
										 date_part('month',s.date),
										 to_char(s.date, 'YYYY'),
										 s.nomen_nomen_id,
										 kl.stado_fiz_group_id,
										 fg.stado_vid_fiz_group_id,
										 fg.stado_podvid_fiz_group_id

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
	procent_raciona = fields.Integer(string=u"% дачи рациона", group_operator="avg")
	kol_korma_norma = fields.Float(digits=(10, 3), string=u"Дача корма по норме", group_operator="sum")
	kol_korma_fakt = fields.Float(digits=(10, 3), string=u"Дача корма по факту", group_operator="sum")
	kol_korma_otk = fields.Float(digits=(10, 3), string=u"Откл.", group_operator="sum")
	
	kol_ostatok = fields.Float(digits=(10, 3), string=u"Кол-во остаток корма", group_operator="sum")
	procent_ostatkov = fields.Float(digits=(10, 1), string=u"% остатков", group_operator="avg")
	sred_kol_milk = fields.Float(digits=(10, 1), string=u"Ср. надой, кг/гол", group_operator="avg")
	sv_golova = fields.Float(digits=(10, 1), string=u"СВ, кг/гол", group_operator="avg")
	konversiay_korma = fields.Float(digits=(10, 1), string=u"Конверсия корма СВ/молоко", group_operator="avg")
	
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
					l.procent_raciona as procent_raciona,
					l.kol_korma_norma as kol_korma_norma,
					l.kol_korma_fakt as kol_korma_fakt,
					l.kol_korma_otk as kol_korma_otk,
					l.kol_ostatok as kol_ostatok,
					l.procent_ostatkov as procent_ostatkov,
					z.name as stado_zagon_name,
					ml.kol as sred_kol_milk,
					l.sv_golova as sv_golova,
					case
						when ml.kol>0 then l.sv_golova/ml.kol
						else 0
					end as konversiay_korma

					
				from korm_korm_ostatok_line l
				left join stado_zagon z on 
										( z.id = l.stado_zagon_id)
				left join stado_struktura_line s on
										(date_trunc('day',s.date) = date_trunc('day',l.date) and 
										 s.stado_zagon_id = l.stado_zagon_id)

				left join milk_nadoy_group m on (m.date = l.date)
				left join milk_nadoy_group_line ml on 
								(l.stado_zagon_id = ml.stado_zagon_id and
								m.id = ml.milk_nadoy_group_id)

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
	stado_podvid_fiz_group_id = fields.Many2one('stado.podvid_fiz_group', string=u'Подвид физ. группы')
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
							fg.stado_podvid_fiz_group_id as stado_podvid_fiz_group_id,
							z.kol_golov_zagon as kol_golov_zagon
					
						from reg_rashod_kormov s

						left join stado_fiz_group fg on ( fg.id = s.stado_fiz_group_id )
						
						left join (select 
									date::date as date, 
									stado_zagon_id,
									max(kol_golov_zagon) as kol_golov_zagon
								   from stado_struktura_line
								   group by date::date, stado_zagon_id) z 
							on (z.date::date = s.date::date and
								z.stado_zagon_id = s.stado_zagon_id)   


					)
		""" % self.pool['res.currency']._select_companies_rates())


class korm_plan_fakt_report(models.Model):
	_name = "korm.plan_fakt_report"
	_description = "Korm plan fakt"
	_auto = False
	_rec_name = 'nomen_nomen_id'
	_order = 'nomen_nomen_id'

	
	year = fields.Char(string=u"Год")
	month = fields.Char(string=u"Месяц")
	
	nomen_nomen_id = fields.Many2one('nomen.nomen', string=u'Наименование корма')
	
	#stado_fiz_group_id = fields.Many2one('stado.fiz_group', string=u'Физиологическая группа')
	#stado_vid_fiz_group_id = fields.Many2one('stado.vid_fiz_group', string=u'Вид физ. группы')
	#kol_golov_zagon = fields.Integer(string=u"Ср. кол-во голов в загоне", group_operator="avg")
	#kol_golov_zagon_sum = fields.Integer(string=u"Кол-во голов в загоне", group_operator="sum")
	#kol_korma_golova = fields.Float(digits=(10, 3), string=u"Кол-во корма на голову", group_operator="sum")
	kol_fakt = fields.Float(digits=(10, 3), string=u"Кол-во по факту", group_operator="sum")
	kol_plan = fields.Float(digits=(10, 3), string=u"Кол-во по плану", group_operator="sum")
	prognoz = fields.Float(digits=(10, 3), string=u"Прогноз выполнения плана %", group_operator="avg")
	kol_prognoz = fields.Float(digits=(10, 3), string=u"Кол-во прогноз", group_operator="sum")
	price = fields.Float(digits=(10, 2), string=u"Цена", group_operator="avg")
	sum_fakt = fields.Float(digits=(10, 2), string=u"Сумма факт", group_operator="sum")
	sum_prognoz = fields.Float(digits=(10, 2), string=u"Сумма прогноз", group_operator="sum")
	sum_plan = fields.Float(digits=(10, 2), string=u"Сумма план", group_operator="sum")
	sum_otk_prognoz = fields.Float(digits=(10, 2), string=u"Сумма прогноз откл.", group_operator="sum")
	#kol_korma_otk = fields.Float(digits=(10, 3), string=u"Откл.", group_operator="sum")
	
	#kol_ostatok = fields.Float(digits=(10, 3), string=u"Кол-во остаток корма", group_operator="sum")
	#procent_ostatkov = fields.Float(digits=(10, 1), string=u"% остатков", group_operator="avg")
	#sred_kol_milk = fields.Float(digits=(10, 1), string=u"Средний надой", group_operator="avg")
	

	def init(self, cr):
		tools.sql.drop_view_if_exists(cr, self._table)
		cr.execute("""
			create or replace view korm_plan_fakt_report as (
				WITH currency_rate as (%s)
						SELECT
							tt.id,
							tt.month,
							tt.year,
							tt.nomen_nomen_id,
							tt.kol_plan,
							tt.kol_fakt,
							--tt.day,
							--tt.count_day,
							tt.kol_prognoz,
							tt.prognoz,
							tt.price,
							tt.price*tt.kol_fakt as sum_fakt,
							tt.price*tt.kol_prognoz as sum_prognoz,
							tt.price*tt.kol_plan as sum_plan,
							tt.price*tt.kol_prognoz-tt.price*tt.kol_plan as sum_otk_prognoz

						FROM (

									SELECT
													min(t.id) as id,
													t.month as month,
													t.year as year,
													t.nomen_nomen_id as nomen_nomen_id,
													sum(t.kol_plan) as kol_plan,
													sum(t.kol_fakt) as kol_fakt,
													max(t.day) as day,
													max(t.count_day) as count_day,
										
													case
														when max(t.day)>0 then
															sum(t.kol_fakt)/max(t.day)*max(t.count_day)
														else 0
													end as kol_prognoz,
													case
														when sum(t.kol_plan)>0 and max(t.day)>0 then
															sum(t.kol_fakt)/max(t.day)*max(t.count_day)/sum(t.kol_plan)*100 
														else 0
													end as prognoz,
													--avg(npl.price) as price,
													
													(Select 
										 np.price
													From nomen_price_line np
										Where np.nomen_nomen_id = t.nomen_nomen_id and
											date_trunc('month',np.date)::date<=make_date(t.year::integer, t.month::integer,1)
										Order by np.date desc
										Limit 1
										) as price
													
													
												FROM    
												(   select 
														pl.id as id,
														p.month as month,
														p.year as year,
														pl.nomen_nomen_id as nomen_nomen_id,
														pl.kol as kol_plan,
														0 as kol_fakt,
														0 as day,
														p.count_day as count_day
													from korm_plan_line pl
													left join korm_plan p on (p.id = pl.korm_plan_id)

													UNION ALL

													select
														min(s.id) as id,
														to_char(s.date, 'MM') as month,
														to_char(s.date, 'YYYY') as year,
														s.nomen_nomen_id as nomen_nomen_id,
														sum(0) as kol_plan,
														sum(s.kol) as kol_fakt,
														max(EXTRACT(day FROM s.date)) as day,
														max(EXTRACT(day FROM (date_trunc('month',s.date)+interval '1 month'-interval '1 second'))) as count_day
														

													from reg_rashod_kormov s
													group by to_char(s.date, 'MM'),
														to_char(s.date, 'YYYY'),
														s.nomen_nomen_id

												) t
									
									
												GROUP BY t.month,
													t.year,
													t.nomen_nomen_id 

								  ) tt
						

					)
		""" % self.pool['res.currency']._select_companies_rates())




class korm_buh_report(models.Model):
	_name = "korm.buh_report"
	_description = "Korm buh report"
	#_auto = False
	# _rec_name = 'nomen_nomen_id'


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


	
	# date = fields.Date(string='Дата')
	# # nomen_nomen_id = fields.Many2one('nomen.nomen', string=u'Наименование корма')
	# stado_fiz_group_id = fields.Many2one('stado.fiz_group', string=u'Физ. группа')
	# stado_vid_fiz_group_id = fields.Many2one('stado.vid_fiz_group', string=u'Вид физ. группы')

	# month = fields.Text(string=u"Месяц")
	# year = fields.Text(string=u"Год")

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
	
	po_fiz_group = fields.Boolean(string=u"Формировать по физиологическим группам (по рационам)")

	#list_nomer = fields.Integer(string=u"Номер листа", default=0)
	
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
					limit 100; """ #%(self.id,)
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

		#print table

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
		#print rr

		return rr

	@api.multi
	def report_print(self):#, cr, uid, ids, context=None):
		"""Сводные ведомости"""

		self.ensure_one()
		
		def write_sheet(workbook, name_group, data_pivot, list_nomer='', korm_racion=None, normi_dict=None):
			start_row_num = 13 #Начало данных таблицы
			start_col_num = 2 #Начало названий корма

			

			total_rows = data_pivot['date'].count()  #Кол-во строк данных
			total_cols = len(data_pivot.columns)   #Кол-во колонок в данных

			#self.list_nomer += 1
			
			list_name = str(list_nomer) + ' ' + name_group

			
				



			worksheet = workbook.add_worksheet(list_name[:30]) #Обрезка имени до 30 символов
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
																				
			



			worksheet.write(0, total_cols, u'Генеральный директор ООО "Эвика-Агро"', text_format_utv)
			worksheet.write(1, total_cols, u'___________ С.М. Кривич"', text_format_utv)


			worksheet.merge_range('A3:%s' % (xl_rowcol_to_cell(2, total_cols)), 
									u'Сводная ведомость расхода кормов', 
									merge_format)
									
			worksheet.merge_range('A4:%s' % (xl_rowcol_to_cell(3, total_cols)), 
									u'за %s %s г.' % (self.month_text, self.year), 
									merge_format)


			worksheet.write(4, 0, u'Организация', text_format_head) 
			worksheet.write(4, 2, u'ООО "Эвика-Агро"', text_format_head_bold)   

			worksheet.write(5, 0, u'Отделений, участок', text_format_head)
			worksheet.write(5, 2, u'Животноводческий комплекс', text_format_head_bold)

			worksheet.write(6, 0, u'Группа скота', text_format_head)
			if self.po_fiz_group and korm_racion !=None:
				name_full = name_group + u' (рацион от ' + str(korm_racion.date) + ')'
				worksheet.write(6, 2, name_full, text_format_head_bold)     
			else:
				worksheet.write(6, 2, name_group, text_format_head_bold)                    
				        


			worksheet.merge_range('A9:B9', u'Норма на одну голову, кг', format_table_head)
			worksheet.merge_range('A10:B10', u'Факт на одну голову, кг', format_table_head)
			worksheet.merge_range('A11:B11', u'Лимит на месяц, кг', format_table_head)

			worksheet.merge_range('C12:%s' % (xl_rowcol_to_cell(11, total_cols-1)), 
									u'Наименование использованных кормов', 
									format_table_head)

			#Вставляем рамки ячеек                      
			for col_num in range(total_cols-2):
				worksheet.write(8, col_num+2, None, format_table_head)
				worksheet.write(9, col_num+2, None, format_table_head)
				worksheet.write(10, col_num+2, None, format_table_head)
				
				

			# Вставляем названия столбцов                       
			for col_num, value in enumerate(data_pivot.columns.values):
				worksheet.write(12, col_num, value, format_table_head)
				worksheet.set_column(0, col_num+1, 10) #Задаем ширину колонки

				#Вставляем нормы из рациона
				if self.po_fiz_group and normi_dict !=None:
					if value in normi_dict: #проверяем есть ли такой корм в словаре
						norma = normi_dict[value]
						worksheet.write(8, col_num, norma, format_table_float)


				num=col_num + 1


			worksheet.set_row(12,50) #Задаем высоту строк с названиями корма

			worksheet.merge_range('C14:%s' % (xl_rowcol_to_cell(13, total_cols-1)), 
									u'Кол-во использованных кормов',format_table_head)


			worksheet.merge_range('A12:A14', u'Дата', format_table_head)    
			worksheet.merge_range('B12:B14', u'Кол-во скота (в наличии), гол.', format_table_head)              
			worksheet.merge_range('%s:%s' % (   xl_rowcol_to_cell(8, total_cols),
												xl_rowcol_to_cell(13, total_cols)), 
									u'Итого за день', 
									format_table_head)                  

			row=start_row_num+1
			for index, rows in data_pivot.iterrows():
				col=0
				#print rows
				for i, val in enumerate(rows):
					#print val
					if i>0:
						worksheet.write(row, col, val, format_table_int)
					else:
						worksheet.write(row, col, val, format_table_date)
							
					#worksheet.write(row, col, None, format_table_data)
					col+=1
				
				row+=1

			row_num = start_row_num + 1



			#Итоги за день
			for i in list(range(total_rows)):
				
				worksheet.write_formula(row_num,total_cols,
									'{=SUM(%s:%s)}' % (xl_rowcol_to_cell(row_num, start_col_num),
														xl_rowcol_to_cell(row_num, total_cols-1)), format_table_int)
				row_num+=1

			#Вставляем рамки ячеек                      
			for col_num in range(total_cols-1):
				worksheet.write(row_num, col_num+2, None, format_table_int)
				worksheet.write(row_num+2, col_num+2, None, format_table_int)
				
			 
			col_num = start_col_num
			#среднее для поголовья
			worksheet.write(row_num, 0, u'Ср. поголовье', format_table_head)
			worksheet.write_formula(row_num, 1,
									'{=AVERAGE(%s:%s)}' % (xl_rowcol_to_cell(start_row_num, 1),
														xl_rowcol_to_cell(row_num-1, 1)), format_table_int)
														
			row_num += 1 
													   
			#Итоги по корму
			worksheet.write(row_num, 0, u'Итого', format_table_head)
			col_num = start_col_num - 1
			for i in range(len(data_pivot.columns)):
				
				worksheet.write_formula(row_num, col_num,
									'{=SUM(%s:%s)}' % (xl_rowcol_to_cell(start_row_num+1, col_num),
														xl_rowcol_to_cell(row_num-2, col_num)), format_table_int)
				col_num+=1




			#Факт на голову
			col_num = start_col_num
			for i in range(len(data_pivot.columns)-1):
				
				worksheet.write_formula(9, col_num,
									'{=%s/%s}' % (xl_rowcol_to_cell(row_num, col_num),
														xl_rowcol_to_cell(row_num, 1)), format_table_float)
				col_num+=1


			#Лимит на месяц
			if self.po_fiz_group and korm_racion !=None:
				col_num = start_col_num
				for i in range(len(data_pivot.columns)-1):
					
					worksheet.write_formula(10, col_num,
										'{=%s*%s}' % (xl_rowcol_to_cell(8, col_num),
															xl_rowcol_to_cell(row_num, 1)), format_table_int)
					col_num+=1





			row_num += 1
			#worksheet.write(row_num, 0, u'Остаток лимита', format_table_head)
			worksheet.merge_range('%s:%s' % (xl_rowcol_to_cell(row_num, 0),
												xl_rowcol_to_cell(row_num, 1)), 
								  u'Остаток лимита', 
								  format_table_head)
			
			#Остаток лимита
			if self.po_fiz_group and korm_racion !=None:
				col_num = start_col_num
				for i in range(len(data_pivot.columns)-2):
					
					worksheet.write_formula(row_num, col_num,
										'{=%s-%s}' % (xl_rowcol_to_cell(10, col_num),
															xl_rowcol_to_cell(row_num-1, col_num)), format_table_int)
					col_num+=1

			

			#Установки печати
			worksheet.set_landscape() #Ландшафт
			worksheet.set_margins(0.5, 0.5, 0.5, 0.5) #Поля по умолчанию
			#print_area( first_row , first_col , last_row , last_col )
			worksheet.fit_to_pages(1, 1) #Разместить на одной странице


			#writer.save()













		reload(sys)
		sys.setdefaultencoding("utf-8")
		
		
		
		

		tmp_dir = tempfile.mkdtemp()

		

		output_filename = tmp_dir + '/BuhReport.xlsx'

		workbook = xlsxwriter.Workbook(output_filename, {'default_date_format': 'DD.MM.YYYY'})

		list_nomer = '' #Номерация листов. 1,  1.1, 2, 2.2
		list_nomer_vid = 0
		#writer = pd.ExcelWriter(output_filename, engine='xlsxwriter')
		stado_vid_fiz_group_ids = self.env['stado.vid_fiz_group'].search([])
		
		for stado_vid_fiz_group in stado_vid_fiz_group_ids:


			zapros = """select 
							n.name,
							r.date::date,
							r.nomen_nomen_id,
							r.kol as kol_fakt
						from reg_rashod_kormov r
						left join nomen_nomen n on (n.id=r.nomen_nomen_id)
						left join stado_fiz_group fg on (fg.id = r.stado_fiz_group_id)
						
						where r.date::date>='%s' and r.date::date<='%s' and
								fg.stado_vid_fiz_group_id=%s
						
						

						""" %(self.date_start, self.date_end, stado_vid_fiz_group.id)
			#print zapros
			self.env.cr.execute(zapros,)
			res = self.env.cr.fetchall()
			if len(res)>0:
				#pd.core.format.header_style = None

				datas = DataFrame(data=res,columns=['name', 'date', 'nomen_nomen_id', 'kol_fakt'] )


				table = pivot_table(datas, values=['kol_fakt'], 
								index=['date'],
								#rows=['date'], 
								columns=['name'], 
								aggfunc=np.sum, 
								#margins=True
								)


						
				#print table2

				data_pivot= DataFrame(data=table) 
				data_pivot.fillna(0, inplace=True)
				data_pivot.reset_index(inplace=True)



				data_pivot.columns = data_pivot.columns.droplevel()

				data_pivot['Total'] = 0
				data_pivot.rename(columns={"": "date"}, inplace=True)
				for index, row in data_pivot.iterrows():
					#row['Total']=200
					#data_pivot.set_value(index, 'Total',200)
					l = row['date']
					
					date=l#.strftime("%Y-%m-%d")
					zapros = """select 
										
										to_char(s.date, 'YYYY-mm-dd'),
										sum(s.kol_golov_zagon) as kol_golov_zagon
										
									from stado_struktura_line s
									left join stado_fiz_group fg on (fg.id = s.stado_fiz_group_id)
									where to_char(s.date, 'YYYY-mm-dd')='%s' and
									fg.stado_vid_fiz_group_id=%s                                
									Group by to_char(s.date, 'YYYY-mm-dd')
									
														
									

									""" % (date, stado_vid_fiz_group.id)
					self.env.cr.execute(zapros,)
					gol = self.env.cr.fetchone()
					if gol!=None:
						if len(gol)>0:
							data_pivot.loc[index, "Total"] = gol[1]
					#print row['date'], row['Total']





				#print data_pivot
				Total = data_pivot['Total']
				data_pivot.drop(labels=['Total'], axis=1,inplace = True)
				data_pivot.insert(1, 'Total', Total)
				
				list_nomer_vid += 1
				list_nomer = str(list_nomer_vid) + '.'
				write_sheet(workbook, stado_vid_fiz_group.name, data_pivot, list_nomer)




				#Формирование листов по подвидам групп кормления
				
				list_nomer_podvid = 0
				stado_podvid_fiz_group_ids = self.env['stado.podvid_fiz_group'].search([]) 
				for stado_podvid_fiz_group in stado_podvid_fiz_group_ids:
					
					zapros = """select 
							n.name,
							r.date::date,
							r.nomen_nomen_id,
							r.kol as kol_fakt
						from reg_rashod_kormov r
						left join nomen_nomen n on (n.id=r.nomen_nomen_id)
						left join stado_fiz_group fg on (fg.id = r.stado_fiz_group_id)
						
						where r.date::date>='%s' and r.date::date<='%s' and
								fg.stado_vid_fiz_group_id=%s and
								fg.stado_podvid_fiz_group_id=%s
						
						

						""" %(self.date_start, self.date_end, stado_vid_fiz_group.id, stado_podvid_fiz_group.id)
					#print zapros
					self.env.cr.execute(zapros,)
					res = self.env.cr.fetchall()
					if len(res)>0:
						#pd.core.format.header_style = None

						datas = DataFrame(data=res,columns=['name', 'date', 'nomen_nomen_id', 'kol_fakt'] )


						table = pivot_table(datas, values=['kol_fakt'], 
										index=['date'],
										#rows=['date'], 
										columns=['name'], 
										aggfunc=np.sum, 
										#margins=True
										)


								
						#print table2

						data_pivot= DataFrame(data=table) 
						data_pivot.fillna(0, inplace=True)
						data_pivot.reset_index(inplace=True)



						data_pivot.columns = data_pivot.columns.droplevel()

						data_pivot['Total'] = 0
						data_pivot.rename(columns={"": "date"}, inplace=True)
						for index, row in data_pivot.iterrows():
							#row['Total']=200
							#data_pivot.set_value(index, 'Total',200)
							l = row['date']
							
							date=l#.strftime("%Y-%m-%d")
							zapros = """select 
												
												to_char(s.date, 'YYYY-mm-dd'),
												sum(s.kol_golov_zagon) as kol_golov_zagon
												
											from stado_struktura_line s
											left join stado_fiz_group fg on (fg.id = s.stado_fiz_group_id)
											where to_char(s.date, 'YYYY-mm-dd')='%s' and
											fg.stado_vid_fiz_group_id=%s and
											fg.stado_podvid_fiz_group_id=%s                                         
											Group by to_char(s.date, 'YYYY-mm-dd')
											
																
											

											""" % (date, stado_vid_fiz_group.id, stado_podvid_fiz_group.id)
							self.env.cr.execute(zapros,)
							gol = self.env.cr.fetchone()
							if gol!=None:
								if len(gol)>0:
									data_pivot.loc[index, "Total"] = gol[1]
							#print row['date'], row['Total']





						#print data_pivot
						Total = data_pivot['Total']
						data_pivot.drop(labels=['Total'], axis=1,inplace = True)
						data_pivot.insert(1, 'Total', Total)
						name_group = (stado_podvid_fiz_group.name+ ' ' +stado_vid_fiz_group.name)
						
						list_nomer_podvid += 1
						list_nomer = str(list_nomer_vid) + '.' + str(list_nomer_podvid)
						write_sheet(workbook, name_group , data_pivot, list_nomer)

						

						#Формирование листов по видам (рационам) групп кормления

						list_nomer_racion = 0
						if self.po_fiz_group == True:
							stado_fiz_group_ids = self.env['stado.fiz_group'].search([('stado_podvid_fiz_group_id', '=', stado_podvid_fiz_group.id)]) 
							for stado_fiz_group in stado_fiz_group_ids:
								zapros = """
											select DISTINCT
												k.id

											from reg_rashod_kormov r
											left join korm_racion k on (k.id = r.korm_racion_id)
											left join stado_fiz_group fg on (fg.id = r.stado_fiz_group_id)
											where 	r.date::date>='%s' and r.date::date<='%s' and
													r.stado_fiz_group_id=%s and k.id is not Null
											--Order by k.date
									

									""" %(self.date_start, self.date_end, stado_fiz_group.id)
								#print zapros
								self.env.cr.execute(zapros,)
								rez_racions = self.env.cr.fetchall()
								if len(rez_racions)>0:

									korm_racion_ids = self.env['korm.racion'].browse([racions for racions, in rez_racions])
									#print 'kkkkkkkkk====', korm_racion_ids 
									#print "POOOOOOOOOOOOOOOOOOOOOOOOOOO"
							

									for korm_racion in korm_racion_ids:
										#print "--POOOOOOOOOOOOOOOOOOOOOOOOOOO"

										#print 'rrrrrrrrrrrrrrrr=', racion

										#Т.к есть записи без рациона (кормление без кормораздатчика),
										#чтобы эти записи попали в выборку
										#То выборку кормов нужно сделать не по рациону а по датам,
										#когда этот рацион использовался

										#Находим мин макс даты использования рациона
										zapros = """select 
														min(r.date::date),
														max(r.date::date)

													from reg_rashod_kormov r
													where r.date::date>='%s' and r.date::date<='%s' and
													r.stado_fiz_group_id=%s and
													r.korm_racion_id=%s

											
											

											""" %(self.date_start, self.date_end, stado_fiz_group.id, korm_racion.id)
										#print zapros
										self.env.cr.execute(zapros,)
										res = self.env.cr.fetchone()

										date_start_racion = date_end_racion = ''

										if len(res)>0:
											date_start_racion = res[0]  #min date
											date_end_racion = res[1]	#max date
										else:
											continue  #Если запрос вернул пустые данные но переходим на следующий цикл	



										zapros = """select 
												n.name,
												r.date::date,
												r.nomen_nomen_id,
												r.kol as kol_fakt
											from reg_rashod_kormov r
											left join nomen_nomen n on (n.id=r.nomen_nomen_id)
											left join stado_fiz_group fg on (fg.id = r.stado_fiz_group_id)
											
											where r.date::date>='%s' and r.date::date<='%s' and
													r.stado_fiz_group_id=%s and
													r.korm_racion_id=%s
											
											

											""" %(date_start_racion, date_end_racion, stado_fiz_group.id, korm_racion.id)
										#print zapros
										self.env.cr.execute(zapros,)
										res = self.env.cr.fetchall()
										if len(res)>0:
											#print "----POOOOOOOOOOOOOOOOOOOOOOOOOOO"
											#pd.core.format.header_style = None

											datas = DataFrame(data=res,columns=['name', 'date', 'nomen_nomen_id', 'kol_fakt'] )


											table = pivot_table(datas, values=['kol_fakt'], 
															index=['date'],
															#rows=['date'], 
															columns=['name'], 
															aggfunc=np.sum, 
															#margins=True
															)


													
											#print table2

											data_pivot= DataFrame(data=table) 
											data_pivot.fillna(0, inplace=True)
											data_pivot.reset_index(inplace=True)



											data_pivot.columns = data_pivot.columns.droplevel()

											data_pivot['Total'] = 0
											data_pivot.rename(columns={"": "date"}, inplace=True)
											for index, row in data_pivot.iterrows():
												#row['Total']=200
												#data_pivot.set_value(index, 'Total',200)
												l = row['date']
												
												date=l#.strftime("%Y-%m-%d")
												zapros = """select 
																	
																	to_char(s.date, 'YYYY-mm-dd'),
																	sum(s.kol_golov_zagon) as kol_golov_zagon
																	
																from stado_struktura_line s
																left join stado_fiz_group fg on (fg.id = s.stado_fiz_group_id)
																where to_char(s.date, 'YYYY-mm-dd')='%s' and
																fg.stado_vid_fiz_group_id=%s and
																fg.stado_podvid_fiz_group_id=%s and
																s.stado_fiz_group_id = %s                                        
																Group by to_char(s.date, 'YYYY-mm-dd')
																
																					
																

																""" % (date, stado_vid_fiz_group.id, stado_podvid_fiz_group.id, stado_fiz_group.id)
												self.env.cr.execute(zapros,)
												gol = self.env.cr.fetchone()
												if gol!=None:
													if len(gol)>0:
														data_pivot.loc[index, "Total"] = gol[1]
												#print row['date'], row['Total']


											#Данные по норме кормления
											normi_dict = {}
											for line in korm_racion.korm_racion_line:
												normi_dict[line.nomen_nomen_id.name] = line.kol


											#print data_pivot
											Total = data_pivot['Total']
											data_pivot.drop(labels=['Total'], axis=1,inplace = True)
											data_pivot.insert(1, 'Total', Total)
											name_group = (stado_fiz_group.name+ ' ' +stado_vid_fiz_group.name + '')
											
											list_nomer_racion += 1
											list_nomer = str(list_nomer_vid) + '.' + str(list_nomer_podvid) + '.' + str(list_nomer_racion)
											write_sheet(workbook, name_group , data_pivot, list_nomer, korm_racion, normi_dict)

			

		
		workbook.close()







		export_id = self.pool.get('excel.extended').create(self.env.cr, self.env.uid, 
					{'excel_file': base64.encodestring(open(output_filename,"rb").read()), 'file_name': 'BuhReport.xlsx'}, context=self.env.context)

		return{

			'view_mode': 'form',

			'res_id': export_id,

			'res_model': 'excel.extended',

			'view_type': 'form',

			'type': 'ir.actions.act_window',

			'context': self.env.context,

			'target': 'new',

			}



	@api.multi
	def report_print_analitic(self):#, cr, uid, ids, context=None):
		"""Аналитический отчет"""
		self.ensure_one()

		reload(sys)
		sys.setdefaultencoding("utf-8")
		
		tmp_dir = tempfile.mkdtemp()

		output_filename = tmp_dir + '/KormAnaliticReport.xlsx'

		#workbook = xlsxwriter.Workbook(output_filename, {'default_date_format': 'DD.MM.YYYY'})
		#worksheet = workbook.add_worksheet(u'База')
		zapros = """select
						z2.date,
						sfg.name as stado_fiz_group,
						case 
							when z2.doc='korm.korm' then 'Кормовое задание' 
							else 'Расход кормов и добавок' 
						end as vid_doc,
						kr.date as racion_date,
						nn.name as nomen_nomen,
						z2.kol_golov_zagon,
						z2.kol_racion_golova,
						z2.kol_norma,
						z2.kol_fakt
						

					from 
					(
						select
						z1.date,
						z1.stado_fiz_group_id,
						z1.doc,
						z1.korm_racion_id,
						z1.nomen_nomen_id,
						z1.kol_fakt,
						z1.kol_norma,
						(select 
							sum(kol_golov_zagon )
						from stado_struktura_line
						where z1.date=date::date and stado_fiz_group_id=z1.stado_fiz_group_id
						group by stado_fiz_group_id
						) as kol_golov_zagon,
						(select
							kol
						from korm_racion_line
						where nomen_nomen_id=z1.nomen_nomen_id and 
							korm_racion_id=z1.korm_racion_id
						) as kol_racion_golova
						
						from (
						select 
							rrk.date::date as date,
							rrk.stado_fiz_group_id,
							rrk.obj as doc,
							rrk.korm_racion_id as korm_racion_id,
							rrk.nomen_nomen_id,
							sum(rrk.kol) as kol_fakt,
							sum(rrk.kol_norma) as kol_norma
						

						from reg_rashod_kormov rrk
						
						Group by rrk.date::date, rrk.stado_fiz_group_id, rrk.obj, 
								 rrk.korm_racion_id, rrk.nomen_nomen_id
						
						) as z1
					) as z2
					left join stado_fiz_group as sfg on (sfg.id=z2.stado_fiz_group_id)
					left join korm_racion as kr on (kr.id=z2.korm_racion_id)
					left join nomen_nomen as nn on (nn.id=z2.nomen_nomen_id)
					where z2.date>='%s' and z2.date<='%s'
					Order by z2.date, sfg.name, nn.name

			""" %(self.date_start, self.date_end)
		#print zapros
		self.env.cr.execute(zapros,)
		res = self.env.cr.fetchall()
		writer = pd.ExcelWriter(output_filename, engine='xlsxwriter', date_format='dd.mm.yyyy')

		workbook  = writer.book
		
		
		if len(res)>0:
			datas = DataFrame(data=res,columns=[u'Дата', 
												u'Физ. группа', 
												u'Вид документа', 
												u'Дата рациона', 
												u'Наименование корма', 
												u'Кол-во голов', 
												u'На голову по рациону, кг', 
												u'Норма по заданию, кг',
												u'Факт, кг'] )

			datas[u'Норма по рациону, кг'] = datas[u'На голову по рациону, кг'] * datas[u'Кол-во голов']
			datas[u'На голову по заданию, кг'] = datas[u'Норма по заданию, кг'] / datas[u'Кол-во голов']
			datas[u'На голову по факту, кг'] = datas[u'Факт, кг'] / datas[u'Кол-во голов']
			
			datas[u'% откл факт от рациона'] = (datas[u'На голову по факту, кг'] - datas[u'На голову по рациону, кг']) / datas[u'На голову по рациону, кг']
			datas[u'% откл факт от задания'] = (datas[u'На голову по факту, кг'] - datas[u'На голову по заданию, кг']) / datas[u'На голову по заданию, кг']
			datas[u'% откл задания от рациона'] = (datas[u'На голову по заданию, кг'] - datas[u'На голову по рациону, кг']) / datas[u'На голову по рациону, кг']
			
			datas[u'Откл факта от задания, кг'] = (datas[u'Факт, кг'] - datas[u'Норма по заданию, кг'])
			datas.head()
			datas = datas[[ u'Дата', 
							u'Физ. группа', 
							u'Наименование корма', 
							u'Кол-во голов', 
							u'На голову по рациону, кг',
							u'На голову по заданию, кг',
							u'На голову по факту, кг',
							u'% откл факт от рациона',
							u'% откл факт от задания',
							u'% откл задания от рациона',
							u'Норма по рациону, кг', 
							u'Норма по заданию, кг',
							u'Факт, кг',
							u'Откл факта от задания, кг',
							u'Дата рациона', 
							u'Вид документа' 

							]]
			datas.to_excel(writer, sheet_name='База', index=False)
		

		worksheet = writer.sheets['База']
		
		text_fmt = workbook.add_format({   'text_wrap': True,
											'border':1,
											'align':'center',
											'valign':'vcenter',
											'font_size':8       })
		percent_fmt = workbook.add_format({'num_format': '0.0%' })
		float2_fmt = workbook.add_format({'num_format': '# ##0.00' })
		int_fmt = workbook.add_format({'num_format': '# ##0'})

		# Вставляем названия столбцов                       
		for col_num, value in enumerate(datas.columns.values):
			worksheet.write(0, col_num, value, text_fmt)
			


		worksheet.set_row(0,50)

		worksheet.set_column('A:A', 10)
		worksheet.set_column('B:B', 30)
		worksheet.set_column('C:C', 26)
		worksheet.set_column('D:D', 5, int_fmt)
		worksheet.set_column('E:G', 7, float2_fmt)
		worksheet.set_column('H:J', 7, percent_fmt)
		worksheet.set_column('K:N', 7, int_fmt)
		worksheet.set_column('O:O', 10)
		worksheet.set_column('P:P', 20)

		number_rows = len(datas.index)
		# Define our range for the color formatting
		color_range = "H2:J{}".format(number_rows+1)

				# Add a format. Light red fill with dark red text.
		format1 = workbook.add_format({'bg_color': '#FFC7CE',
									   'font_color': '#9C0006'})

		# Add a format. Green fill with dark green text.
		format2 = workbook.add_format({'bg_color': '#C6EFCE',
									   'font_color': '#006100'})

		# Highlight the top 5 values in Green
		worksheet.conditional_format(color_range, {'type': 'cell',
												   'criteria': '>',
												   'value': '0.12',
												   'format': format2})

		# Highlight the bottom 5 values in Red
		worksheet.conditional_format(color_range, {'type': 'cell',
													'criteria': '<',
												   'value': '-0.12',
												   'format': format1})


		color_range = "N2:N{}".format(number_rows+1)
		# Highlight the top 5 values in Green
		worksheet.conditional_format(color_range, {'type': 'cell',
												   'criteria': '>',
												   'value': '10',
												   'format': format2})

		# Highlight the bottom 5 values in Red
		worksheet.conditional_format(color_range, {'type': 'cell',
													'criteria': '<',
												   'value': '-10',
												   'format': format1})

		worksheet.set_zoom(90)
		worksheet.freeze_panes(1, 0)
		#Установки печати
		worksheet.set_landscape() #Ландшафт
		worksheet.set_margins(0.5, 0.5, 0.5, 0.5) #Поля по умолчанию
		worksheet.repeat_rows(0)
		#print_area( first_row , first_col , last_row , last_col )
		worksheet.fit_to_pages(1, 100) #Разместить на одной странице
		writer.save()
		#workbook.close()







		export_id = self.pool.get('excel.extended').create(self.env.cr, self.env.uid, 
					{'excel_file': base64.encodestring(open(output_filename,"rb").read()), 'file_name': 'KormAnaliticReport.xlsx'}, context=self.env.context)

		return{

			'view_mode': 'form',

			'res_id': export_id,

			'res_model': 'excel.extended',

			'view_type': 'form',

			'type': 'ir.actions.act_window',

			'context': self.env.context,

			'target': 'new',

			}
		
		# vid1 = self.read()
		
		# datas = {"date":self.date, "stado_vid_fiz_group_id": "sdsd"}
		# s = self.read()
		# print s

		# data = self.read()[0]
		# datas = {
		#   'ids': self.ids,
		#   'model': 'korm.buh_report',
		#   'form': data,
		#   'get_list': self.get_list()
		# }
		# return {
		#           'type': 'ir.actions.report.xml',
		#           'report_name': 'kormlenie.report_korm_buh_report_view',
		#           'datas': datas,
		#       }



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




class korm_analiz_sv_report(models.Model):
	_name = "korm.korm_analiz_sv_report"
	_description = "Анализ потребления СВ"
	_auto = False
	_rec_name = 'stado_fiz_group_id'

	
	date = fields.Date(string='Дата')
	
	
	#stado_fiz_group_name = fields.Char(string=u'Физиологическая группа (наим.)')
	stado_fiz_group_id = fields.Many2one('stado.fiz_group', string=u'Физиологическая группа')
	pok = fields.Char(string=u'Показатель')
	#kol_golov_zagon = fields.Integer(string=u"Ср. кол-во голов в загоне", group_operator="avg")
	#procent_raciona = fields.Integer(string=u"% дачи рациона", group_operator="avg")
	#kol_korma_norma = fields.Float(digits=(10, 3), string=u"Дача корма по норме", group_operator="sum")
	#kol_korma_fakt = fields.Float(digits=(10, 3), string=u"Дача корма по факту", group_operator="sum")
	#kol_korma_otk = fields.Float(digits=(10, 3), string=u"Откл.", group_operator="sum")
	
	#kol_ostatok = fields.Float(digits=(10, 3), string=u"Кол-во остаток корма", group_operator="sum")
	#procent_ostatkov = fields.Float(digits=(10, 1), string=u"% остатков", group_operator="avg")
	#sred_kol_milk = fields.Float(digits=(10, 1), string=u"Средний надой", group_operator="avg")
	kol = fields.Float(digits=(10, 1), string=u"Кол-во кг/гол.", group_operator="avg")
	
	_order = 'stado_fiz_group_id'

	def init(self, cr):
		tools.sql.drop_view_if_exists(cr, self._table)
		cr.execute("""
			create or replace view korm_korm_analiz_sv_report as (
				WITH currency_rate as (%s)
				SELECT
					row_number() OVER () AS id,
					z.date,
					z.stado_fiz_group_id,
					z.pok,
					z.kol


				FROM 	
				(
					(
						select 
							--l.id as id,
							l.date as date,
							l.stado_fiz_group_id as stado_fiz_group_id,
							
							case 
								when l.sv_golova is Not Null then 'СВ'
							else 'СВ' 
							end as pok,
							l.sv_golova as kol
							

							
						from korm_korm_ostatok_line l
					)

					UNION

					(
						select 
							--max(l.id) as id,
							d.date as date,
							l.stado_fiz_group_id as stado_fiz_group_id,
							
							case 
								when avg(l.kol) is Not Null then 'Молоко'
							else 'Молоко' 
							end as pok,
							sum(l.kol*l.kol_golov)/sum(l.kol_golov) as kol
							

							
						from milk_nadoy_group_line l
						left join milk_nadoy_group d on (d.id=l.milk_nadoy_group_id)
						group by d.date, l.stado_fiz_group_id
					)
				) z
					

			)
		""" % self.pool['res.currency']._select_companies_rates())



class korm_analiz_potrebleniya_kormov_report(models.Model):
	_name = "korm.analiz_potrebleniya_kormov_report"
	_description = "Анализ потребления кормов"
	_auto = False
	_rec_name = 'stado_fiz_group_id'

	
	date = fields.Date(string='Дата')
	
	group_pok = fields.Char(string=u'Группа показателя')
	pok = fields.Char(string=u'Показателя')
	
	#stado_fiz_group_name = fields.Char(string=u'Физиологическая группа (наим.)')
	stado_zagon_id = fields.Many2one('stado.zagon', string=u'Загон')
	stado_fiz_group_id = fields.Many2one('stado.fiz_group', string=u'Физиологическая группа')
	stado_vid_fiz_group_id = fields.Many2one('stado.vid_fiz_group', string=u'Вид Физиологической группы')
	
	kol_golov_zagon = fields.Integer(string=u"Поголовье", group_operator="sum")
	#procent_raciona = fields.Integer(string=u"% дачи рациона", group_operator="avg")
	kol_na_golovu = fields.Float(digits=(10, 3), string=u"Кол-во на голову", group_operator="avg")
	kol_na_zagon = fields.Float(digits=(10, 3), string=u"Кол-во на загон", group_operator="sum")
	#kol_korma_fakt = fields.Float(digits=(10, 3), string=u"Дача корма по факту", group_operator="sum")
	#kol_korma_otk = fields.Float(digits=(10, 3), string=u"Откл.", group_operator="sum")
	
	#kol_ostatok = fields.Float(digits=(10, 3), string=u"Кол-во остаток корма", group_operator="sum")
	#procent_ostatkov = fields.Float(digits=(10, 1), string=u"% остатков", group_operator="avg")
	#sred_kol_milk = fields.Float(digits=(10, 1), string=u"Средний надой", group_operator="avg")
	#kol = fields.Float(digits=(10, 1), string=u"Кол-во кг/гол.", group_operator="avg")
	
	_order = 'stado_fiz_group_id'

	def init(self, cr):
		tools.sql.drop_view_if_exists(cr, self._table)
		cr.execute("""
			create or replace view korm_analiz_potrebleniya_kormov_report as (
				WITH currency_rate as (%s)
				SELECT
					row_number() OVER () AS id,
					z.date,
					z.group_pok,
					z.pok,
					z.stado_zagon_id,
					z.stado_fiz_group_id,
					z.stado_vid_fiz_group_id,
					z.kol_golov_zagon,
					z.kol_na_golovu,
					z.kol_na_zagon

				FROM

					(
						(
						SELECT
							mn.date,
							case
								when mn.stado_zagon_id>0 then 'Молоко'
							end as group_pok,
							case
								when mn.stado_zagon_id>0 then 'Валовый надой'
							end as pok,

							
							mn.stado_zagon_id,
							mn.stado_fiz_group_id,
							fg.stado_vid_fiz_group_id,
							mn.kol_golov_zagon,
							mn.nadoy_golova_fakt as kol_na_golovu,
							mn.nadoy_zagon_fakt as kol_na_zagon
						FROM milk_nadoy_group_fakt_line mn
						left join stado_fiz_group fg on (fg.id = mn.stado_fiz_group_id)
						)
					UNION
						(
						SELECT
							k.date::date,
							case
								when k.id>0 then 'Корма'
							end as group_pok,
							n.name as pok,
							k.stado_zagon_id,
							k.stado_fiz_group_id,
							fg.stado_vid_fiz_group_id,
							z2.kol_golov_zagon as kol_golov_zagon,
							case
								when z2.kol_golov_zagon>0 then k.kol/z2.kol_golov_zagon
								else 0
							end as kol_na_golovu,
							k.kol as kol_na_zagon

						FROM reg_rashod_kormov as k
						left join nomen_nomen n on (n.id = k.nomen_nomen_id)
						left join stado_zagon z on (z.id = k.stado_zagon_id)
						left join (select 
															date::date as date, 
															stado_zagon_id,
															max(kol_golov_zagon) as kol_golov_zagon
														   from stado_struktura_line
														   group by date::date, stado_zagon_id) z2 
													on (z2.date::date = k.date::date and
														z2.stado_zagon_id = k.stado_zagon_id)
						left join stado_fiz_group fg on (fg.id = k.stado_fiz_group_id)
						)
					) as z

			)
		""" % self.pool['res.currency']._select_companies_rates())




##from odoo.addons import decimal_precision as dp
#import openerp.addons.decimal_precision as dp

class korm_analiz_efekt_korm_report(models.Model):
    _name = "korm.analiz_efekt_korm_report"
    _description = "Анализ эффективности кормления"
    _auto = False
    _rec_name = 'date'

    
    date = fields.Date(string='Дата')

    cow_fur = fields.Integer(string=u"Фуражные", group_operator="avg")
    cow_doy = fields.Integer(string=u"Дойные", group_operator="avg")

    #valoviy_nadoy = fields.Float(digits=dp.get_precision('kol'),string=u"Валовый надой, тонн", group_operator="sum")
    valoviy_nadoy = fields.Float(digits=(3, 1),string=u"Валовый надой, тонн", group_operator="sum")

    sale_jir = fields.Float(digits=(3, 1), string=u"Жир, %", group_operator="avg")
    sale_belok = fields.Float(digits=(3, 1), string=u"Белок, %", group_operator="avg")
    
    zatrati_korma_fur = fields.Float(digits=(10, 1), string=u"Затраты корма на фуражных, тыс.руб", group_operator="sum")
    zatrati_korma_doy = fields.Float(digits=(10, 1), string=u"Затраты корма на дойных, тыс.руб", group_operator="sum")
    
    amount_sale = fields.Float(digits=(10, 1),string="Выручка, тыс.руб.", group_operator="sum")
    sale_natura = fields.Float(digits=(10, 1),string="Натура, тонн", group_operator="sum")
    sale_zachet = fields.Float(digits=(10, 1),string="Зачетный вес, тонн", group_operator="sum")
    
    zatrati_fur_golova = fields.Float(digits=(10, 1),string="Затраты на фуражную голову, руб/гол", group_operator="avg")
    zatrati_doy_golova = fields.Float(digits=(10, 1),string="Затраты на дойную голову, руб/гол", group_operator="avg")
    zatrati_fur_kg_milk = fields.Float(digits=(10, 1),string="Затраты (фуражные) на 1 кг произведенного молока, руб/кг", group_operator="avg")
    zatrati_doy_kg_milk = fields.Float(digits=(10, 1),string="Затраты (дойные) на 1 кг произведенного молока, руб/кг", group_operator="avg", oldname='zatrati_kg_milk')
    
    
    _order = 'date'

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
            create or replace view korm_analiz_efekt_korm_report as (
                WITH currency_rate as (%s)
                SELECT
                    row_number() OVER () AS id,
                    ttt.*,
                    (((mpt.price * mpt.ko * mpt.kss + (ttt.sale_belok - mpt.bb)/0.01 * mpt.pb + (ttt.sale_jir - mpt.bj)/0.01 * mpt.pj) * mpt.kk + mpt.h) * ttt.sale_natura) as amount_sale
                FROM

                (
                    SELECT
                        
                        tm.date_doc as date,
                        tm.cow_fur,
                        tm.cow_doy,
                        tm.valoviy_nadoy/1000.0 as valoviy_nadoy,
                        tm.sale_jir,
                        tm.sale_belok,
                        tm.sale_natura/1000.0 as sale_natura,
                        tm.sale_zachet/1000.0 as sale_zachet,
                        k.zatrati_korma_fur/1000.0 as zatrati_korma_fur,
                        k.zatrati_korma_doy/1000.0 as zatrati_korma_doy,
                        case
                            when tm.cow_fur>0 then k.zatrati_korma_fur/tm.cow_fur
                            else 0
                        end as zatrati_fur_golova,
                        case
                            when tm.cow_doy>0 then k.zatrati_korma_doy/tm.cow_doy
                            else 0
                        end as zatrati_doy_golova,
                        case
                            when tm.valoviy_nadoy>0 then k.zatrati_korma_doy/tm.valoviy_nadoy
                            else 0
                        end as zatrati_doy_kg_milk,
                        case
                            when tm.valoviy_nadoy>0 then k.zatrati_korma_fur/tm.valoviy_nadoy
                            else 0
                        end as zatrati_fur_kg_milk,
                        ( Select 
                                mp.id
                            From milk_price mp
                            Where mp.date::date<=tm.date_doc::date
                            Order by mp.date desc
                            Limit 1
                        ) as milk_price_id
                        
                        
                        
                    FROM milk_trace_milk tm
                    left join 

                        (
                            
                        SELECT
                            tt.date,
                            sum(tt.kol_korma * tt.price) as zatrati_korma_fur,
                            sum(tt.kol_korma_doy * tt.price) as zatrati_korma_doy
                        FROM
                            (
                            SELECT
                                t.date,
                                t.nomen_nomen_id,
                                t.kol_korma,
                                t.kol_korma_doy,
                                (
                                    Select 
                                        np.price
                                    From nomen_price_line np
                                    Where np.nomen_nomen_id = t.nomen_nomen_id and
                                        np.date::date<=t.date::date
                                    Order by np.date desc
                                    Limit 1
                                ) as price

                            FROM
                                (
                                    select
                                        r.date::date as date,
                                        r.nomen_nomen_id as nomen_nomen_id,
                                        sum(r.kol) as kol_korma,
                                        sum(
                                            case
                                                when s.mastit=True or s.doynie=True then r.kol
                                                else 0
                                            end) as kol_korma_doy
                                        
                                    from reg_rashod_kormov r
                                    left join stado_zagon s on (s.id = r.stado_zagon_id)
                                    where (s.mastit=True or s.doynie=True or s.suhostoy=True)
                                    group by r.date::date, r.nomen_nomen_id
                                 )  t
                            ) tt

                        GROUP BY tt.date




                        ) k on (k.date = tm.date_doc::date)
                ) ttt
                left join milk_price mpt on (mpt.id=ttt.milk_price_id)
              

            )
        """ % self.pool['res.currency']._select_companies_rates())