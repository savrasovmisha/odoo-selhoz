# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError
import math


class krs_result_otel(models.Model):
	_name = 'krs.result_otel'
	_description = u'Результаты отелов'
	_order = 'name'

	@api.one
	@api.depends('kol_telok_jiv', 'kol_telok_mert', 'kol_bik_jiv', 'kol_bik_mert', 'kol_mert')
	def _raschet(self):
		self.kol_itog_jiv = self.kol_telok_jiv + self.kol_bik_jiv
		self.kol_itog_mert = self.kol_telok_mert + self.kol_bik_mert + self.kol_mert
		self.kol_itog = self.kol_itog_jiv + self.kol_itog_mert


	name = fields.Char(string=u"Наименование", required=True)

	abort = fields.Boolean(string=u"Аборт", default=False)

	kol_itog = fields.Integer(string=u"Всего родилось", store=True, compute='_raschet')
	kol_itog_jiv = fields.Integer(string=u"Всего Живых", store=True, compute='_raschet')
	kol_itog_mert = fields.Integer(string=u"Всего Мертвородов", store=True, compute='_raschet')
	kol_telok_jiv = fields.Integer(string=u"Живых телок", store=True)
	kol_telok_mert = fields.Integer(string=u"Мертв. телок", store=True)
	kol_bik_jiv = fields.Integer(string=u"Живых бычков", store=True)
	kol_bik_mert = fields.Integer(string=u"Мертв. бычков", store=True)
	kol_mert = fields.Integer(string=u"Мертвородов", store=True)



class krs_hoz(models.Model):
	_name = 'krs.hoz'
	_description = u'Хозяйства'
	_order = 'name'


	name = fields.Char(string=u"Наименование", required=True)

	kod = fields.Integer(string=u"Код", store=True)
	nashe = fields.Boolean(string=u"Наше хозяйство", default=False)
	selex_id = fields.Integer(string=u"selex_id", default=False)



class krs_spv(models.Model):
	_name = 'krs.spv'
	_description = u'Справочник Причины выбытия'
	_order = 'name'

	name = fields.Char(string=u"Наименование", required=True)
	
	kod = fields.Integer(string=u"Код",required=True)


class krs_srashod(models.Model):
	_name = 'krs.srashod'
	_description = u'Справочник Расход КРС'
	_order = 'name'

	name = fields.Char(string=u"Наименование", required=True)
	
	kod = fields.Integer(string=u"Код",required=True)






class krs_otel(models.Model):
	_name = 'krs.otel'
	_description = u'Отелы КРС'
	_order = 'date desc'

	@api.one
	def _raschet_load(self, hoz_selex_id, result):
		
		result_otel = self.env['krs.result_otel'].search([('name', '=', result)],limit=1)
		
		#print "/////////////////////////", result_otel

		
		result_hoz = self.env['krs.hoz'].search([('selex_id', '=', hoz_selex_id)],limit=1)
		if len(result_hoz)>0:
			self.krs_hoz_id = result_hoz
			#print "\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", result_hoz

	
		if len(result_otel)>0:
			self.krs_result_otel_id = result_otel.id
			self.kol_itog = result_otel.kol_itog
			self.kol_itog_jiv = result_otel.kol_itog_jiv
			self.kol_itog_mert = result_otel.kol_itog_mert
			self.kol_telok_jiv = result_otel.kol_telok_jiv
			self.kol_telok_mert = result_otel.kol_telok_mert
			self.kol_bik_jiv = result_otel.kol_bik_jiv
			self.kol_bik_mert = result_otel.kol_bik_mert
			self.kol_mert = result_otel.kol_mert
			self.abort = result_otel.abort

		self.name = self.inv_nomer
		self.nomer_lakt_str = str(self.nomer_lakt)

	@api.one
	@api.depends('krs_result_otel_id', 'inv_nomer')
	def _raschet(self):
		
		if self.krs_result_otel_id:
			
			self.kol_itog = self.krs_result_otel_id.kol_itog
			self.kol_itog_jiv = self.krs_result_otel_id.kol_itog_jiv
			self.kol_itog_mert = self.krs_result_otel_id.kol_itog_mert
			self.kol_telok_jiv = self.krs_result_otel_id.kol_telok_jiv
			self.kol_telok_mert = self.krs_result_otel_id.kol_telok_mert
			self.kol_bik_jiv = self.krs_result_otel_id.kol_bik_jiv
			self.kol_bik_mert = self.krs_result_otel_id.kol_bik_mert
			self.kol_mert = self.krs_result_otel_id.kol_mert
			self.abort = self.krs_result_otel_id.abort

		self.name = self.inv_nomer
		self.nomer_lakt_str = str(self.nomer_lakt)


	name = fields.Char(string=u"Наименование", compute='_raschet', store=True)
	inv_nomer = fields.Char(string=u"Инв. №", required=True)
	
	date = fields.Date(string='Дата отела', required=True, default=fields.Datetime.now)
	nomer_lakt = fields.Integer(string=u"Номер лактации",required=True)
	nomer_lakt_str = fields.Char(string=u"Номер лактации")
	
	krs_result_otel_id = fields.Many2one('krs.result_otel', string='Результат отела')
	krs_hoz_id = fields.Many2one('krs.hoz', string='Хозяйство рождения')
	
	kol_itog = fields.Integer(string=u"Всего родилось", store=True, compute='_raschet')
	kol_itog_jiv = fields.Integer(string=u"Всего Живых", store=True, compute='_raschet')
	kol_itog_mert = fields.Integer(string=u"Всего Мертвородов", store=True, compute='_raschet')
	kol_telok_jiv = fields.Integer(string=u"Живых телок", store=True, compute='_raschet')
	kol_telok_mert = fields.Integer(string=u"Мертв. телок", store=True, compute='_raschet')
	kol_bik_jiv = fields.Integer(string=u"Живых бычков", store=True, compute='_raschet')
	kol_bik_mert = fields.Integer(string=u"Мертв. бычков", store=True, compute='_raschet')
	kol_mert = fields.Integer(string=u"Мертвородов", store=True, compute='_raschet')

	abort = fields.Boolean(string=u"Аборт", default=False)


class krs_cow_vibitiya(models.Model):
	_name = 'krs.cow_vibitiya'
	_description = u'Выбытия коров'
	_order = 'date desc'


	@api.one
	@api.depends('inv_nomer')
	def _get_name(self):

		self.name = self.inv_nomer


	@api.one
	def _raschet(self, hoz_selex_id, kod_spv, kod_srashod):

		if hoz_selex_id:
			result_hoz = self.env['krs.hoz'].search([('selex_id', '=', hoz_selex_id)],limit=1)
			if len(result_hoz)>0:
				self.krs_hoz_id = result_hoz

		if kod_spv:
			result_spv = self.env['krs.spv'].search([('kod', '=', kod_spv)],limit=1)
			if len(result_spv)>0:
				self.krs_spv_id = result_spv
		if kod_srashod:
			result_srashod = self.env['krs.srashod'].search([('kod', '=', kod_srashod)],limit=1)
			if len(result_srashod)>0:
				self.krs_srashod_id = result_srashod

		self.name = self.inv_nomer
		self.nomer_lakt_str = str(self.nomer_lakt)


	name = fields.Char(string=u"Наименование", compute='_get_name', store=True)
	inv_nomer = fields.Char(string=u"Инв. №", required=True)
	date_rogd = fields.Date(string='Дата рождения', required=True)
	date = fields.Date(string='Дата выбытия', required=True, default=fields.Datetime.now)
	nomer_lakt = fields.Integer(string=u"Номер лактации",required=True)
	nomer_lakt_str = fields.Char(string=u"Номер лактации")


	krs_hoz_id = fields.Many2one('krs.hoz', string='Хозяйство рождения')

	krs_spv_id = fields.Many2one('krs.spv', string='Причина выбытия')

	krs_srashod_id = fields.Many2one('krs.srashod', string='Вид расхода')



class krs_tel_vibitiya(models.Model):
	_name = 'krs.tel_vibitiya'
	_description = u'Выбытия телят'
	_order = 'date desc'


	@api.one
	@api.depends('date_rogd', 'date')
	def _vozrast(self):

		if self.date_rogd and self.date:
			date_rogd = datetime.strptime(self.date_rogd,'%Y-%m-%d')
			date_v = datetime.strptime(self.date,'%Y-%m-%d')
			year = date_v.year - date_rogd.year
			month = date_v.month - date_rogd.month
			day = date_v.day - date_rogd.day

			if month<0:
				month = 12 + month
				year = year - 1

			month = month + year*12

			if day<0:
				month = month - 1

			self.vozrast = month
			self.vozrast_txt = str(self.vozrast).rjust(2, '0')


	@api.one
	@api.depends('inv_nomer')
	def _get_name(self):

		self.name = self.inv_nomer
		self._vozrast()
		


	@api.one
	def _raschet(self, hoz_selex_id, kod_spv, kod_srashod):

		if hoz_selex_id:
			result_hoz = self.env['krs.hoz'].search([('selex_id', '=', hoz_selex_id)],limit=1)
			if len(result_hoz)>0:
				self.krs_hoz_id = result_hoz

		if kod_spv:
			result_spv = self.env['krs.spv'].search([('kod', '=', kod_spv)],limit=1)
			if len(result_spv)>0:
				self.krs_spv_id = result_spv
		if kod_srashod:
			result_srashod = self.env['krs.srashod'].search([('kod', '=', kod_srashod)],limit=1)
			if len(result_srashod)>0:
				self.krs_srashod_id = result_srashod

		self.name = self.inv_nomer
		self._vozrast()

		


	name = fields.Char(string=u"Наименование", compute='_get_name', store=True)
	inv_nomer = fields.Char(string=u"Инв. №", required=True)
	status = fields.Char(string=u"Статус", required=True)
	date_rogd = fields.Date(string='Дата рождения', required=True)
	date = fields.Date(string='Дата выбытия', required=True, default=fields.Datetime.now)
	vozrast = fields.Integer(string='Возраст (мес)' , compute='_vozrast', store=True)
	vozrast_txt = fields.Char(string='Возраст (мес)', compute='_vozrast', store=True)

	krs_hoz_id = fields.Many2one('krs.hoz', string='Хозяйство рождения')

	krs_spv_id = fields.Many2one('krs.spv', string='Причина выбытия')

	krs_srashod_id = fields.Many2one('krs.srashod', string='Вид расхода')




class krs_osemeneniya(models.Model):
	_name = 'krs.osemeneniya'
	_description = u'Осеменения'
	_order = 'date desc'


	@api.one
	@api.depends('inv_nomer')
	def _get_name(self):

		self.name = self.inv_nomer
		
		


	name = fields.Char(string=u"Наименование", compute='_get_name', store=True)
	inv_nomer = fields.Char(string=u"Инв. №", required=True)
	status = fields.Char(string=u"Статус", required=True)
	
	date = fields.Date(string='Дата осеменения', required=True, default=fields.Datetime.now)
	
	fio = fields.Char(string='Осеменатор', required=True)
	bik = fields.Char(string='Бык (семя)', required=True)
	doz = fields.Integer(string='Доз спермы', required=True)

	

class krs_abort(models.Model):
	_name = 'krs.abort'
	_description = u'Аборты'
	_order = 'date desc'


	@api.one
	@api.depends('inv_nomer')
	def _get_name(self):

		self.name = self.inv_nomer
		
		


	name = fields.Char(string=u"Наименование", compute='_get_name', store=True)
	inv_nomer = fields.Char(string=u"Инв. №", required=True)
	status = fields.Char(string=u"Статус", required=True)
	
	date = fields.Date(string='Дата аборта', required=True, default=fields.Datetime.now)






class krs_struktura(models.Model):
	_name = 'krs.struktura'
	_description = u'Структура стада'
	_order = 'date desc'


	@api.one
	@api.depends('date')
	def _get_name(self):

		self.name = self.date

	@api.one
	@api.depends('cow_neosem','cow_osem','cow_somnit','cow_stel','cow_zapusk')
	def _raschet_cow(self):

		self.cow_itog_stel = self.cow_somnit + self.cow_stel + self.cow_zapusk
		self.cow_itog_lakt = self.cow_neosem + self.cow_osem + self.cow_somnit + self.cow_stel
		self.cow_itog_fur = self.cow_neosem + self.cow_osem + self.cow_somnit + self.cow_stel + self.cow_zapusk
	
	@api.one
	@api.depends('tel_neosem','tel_osem','tel_somnit','tel_stel','tel_netel','tel_tranzit','tel_15_neosem','tel_15_osem','tel_15_stel' )
	def _raschet_tel(self):
		self.tel_itog_netel = self.tel_netel + self.tel_tranzit
		self.tel_itog_stel = self.tel_itog_netel + self.tel_stel + self.tel_somnit
		self.tel_itog_tel_netel = self.tel_itog_stel + self.tel_neosem + self.tel_osem
		

		self.tel_15_itog = 	self.tel_15_stel + self.tel_15_neosem +self.tel_15_osem

	
	@api.one
	@api.depends(	'tel_0',
					'tel_1',
					'tel_2',
					'tel_3',
					'tel_4',
					'tel_5',
					'tel_69',
					'tel_912',
					'tel_1215', 
					'tel_15' 
					)
	def _raschet_tel_itog(self):
		self.tel_itog_03 = self.tel_0 + self.tel_1 + self.tel_2
		self.tel_itog_36 = self.tel_3 + self.tel_4 + self.tel_5
		self.tel_itog_618 = self.tel_69 + self.tel_912 + self.tel_1215 + self.tel_15
		self.tel_itog = self.tel_itog_03 + self.tel_itog_36 + self.tel_itog_618

	@api.one
	@api.depends(	'bik_0',
					'bik_1',
					'bik_2',
					'bik_3',
					'bik_4',
					'bik_5',
					'bik_69',
					'bik_912',
					'bik_1215', 
					'bik_15' 
					)
	def _raschet_bik_itog(self):
		self.bik_itog_03 = self.bik_0 + self.bik_1 + self.bik_2
		self.bik_itog_36 = self.bik_3 + self.bik_4 + self.bik_5
		self.bik_itog_618 = self.bik_69 + self.bik_912 + self.bik_1215 + self.bik_15
		self.bik_itog = self.bik_itog_03 + self.bik_itog_36 + self.bik_itog_618


	@api.one
	def _raschet(self):	
		self._raschet_cow()
		self._raschet_tel()
		self._raschet_tel_itog()
		self._raschet_bik_itog()


	name = fields.Char(string=u"Наименование", compute='_get_name', store=True)
	date = fields.Date(string='Дата состояния', required=True, default=fields.Datetime.now)
	
	


	cow_neosem = fields.Integer(string=u"Неосемененных коров", group_operator="avg")
	cow_osem = fields.Integer(string=u"Осемененных коров", group_operator="avg")
	cow_somnit = fields.Integer(string=u"Сомнительных коров", group_operator="avg")
	cow_stel = fields.Integer(string=u"Стельных коров", group_operator="avg")
	cow_zapusk = fields.Integer(string=u"Запущенных коров", group_operator="avg")
	cow_itog_stel = fields.Integer(string=u"Всего стельных коров", store=True, compute='_raschet_cow', group_operator="avg")
	cow_itog_lakt = fields.Integer(string=u"Всего лактирующих коров", store=True, compute='_raschet_cow', group_operator="avg")
	cow_itog_fur = fields.Integer(string=u"Всего фуражных коров", store=True, compute='_raschet_cow', group_operator="avg")
	
	tel_neosem = fields.Integer(string=u"Неосемененная телка", group_operator="avg")
	tel_osem = fields.Integer(string=u"Осемененная телка", group_operator="avg")
	tel_somnit = fields.Integer(string=u"Сомнительная телка", group_operator="avg")
	tel_stel = fields.Integer(string=u"Стельная телка (<5 мес стел)", group_operator="avg")
	tel_netel = fields.Integer(string=u"Нетель (>5 мес стел, до 2 нед до отела)", group_operator="avg")
	tel_tranzit = fields.Integer(string=u"Нетель транзит (2 недели до отела)", group_operator="avg")
	tel_itog_stel = fields.Integer(string=u"Итого Стельных телок", store=True, compute='_raschet_tel', group_operator="avg")
	tel_itog_netel = fields.Integer(string=u"Итого Нетелей (>5 мес стел)", store=True, compute='_raschet_tel', group_operator="avg")
	tel_itog_tel_netel = fields.Integer(string=u"Итого телок+нетелей", store=True, compute='_raschet_tel', group_operator="avg")
	
	tel_15_neosem = fields.Integer(string=u"Неосемененные телки страше 15 мес", group_operator="avg")
	tel_15_osem = fields.Integer(string=u"Осемененные телки страше 15 мес", group_operator="avg")
	tel_15_stel = fields.Integer(string=u"Стельные телки страше 15 мес", group_operator="avg")
	tel_15_itog = fields.Integer(string=u"Итого страше 15 мес (в т.ч нетели)", store=True, compute='_raschet_tel', group_operator="avg")
	
	
	tel_0 = fields.Integer(string=u"Телки 0-1 мес.", group_operator="avg")
	tel_1 = fields.Integer(string=u"Телки 1-2 мес.", group_operator="avg")
	tel_2 = fields.Integer(string=u"Телки 2-3 мес.", group_operator="avg")
	tel_3 = fields.Integer(string=u"Телки 3-4 мес.", group_operator="avg")
	tel_4 = fields.Integer(string=u"Телки 4-5 мес.", group_operator="avg")
	tel_5 = fields.Integer(string=u"Телки 5-6 мес.", group_operator="avg")
	tel_69 = fields.Integer(string=u"Телки 6-9 мес.", group_operator="avg")
	tel_912 = fields.Integer(string=u"Телки 9-12 мес.", group_operator="avg")
	tel_1215 = fields.Integer(string=u"Телки 12-15 мес.", group_operator="avg")
	tel_15 = fields.Integer(string=u"Телки >15 мес.", group_operator="avg")
	
	tel_itog_03 = fields.Integer(string=u"Итого Телки 0-3 мес." , store=True, compute='_raschet_tel_itog', group_operator="avg")
	tel_itog_36 = fields.Integer(string=u"ИтогоТелки 3-6 мес.", store=True, compute='_raschet_tel_itog', group_operator="avg")
	tel_itog_618 = fields.Integer(string=u"Итого Телки >6 мес.", store=True, compute='_raschet_tel_itog', group_operator="avg")
	tel_itog = fields.Integer(string=u"Итого телок", store=True, compute='_raschet_tel_itog', group_operator="avg")


	bik_0 = fields.Integer(string=u"Быки 0-1 мес.", group_operator="avg")
	bik_1 = fields.Integer(string=u"Быки 1-2 мес.", group_operator="avg")
	bik_2 = fields.Integer(string=u"Быки 2-3 мес.", group_operator="avg")
	bik_3 = fields.Integer(string=u"Быки 3-4 мес.", group_operator="avg")
	bik_4 = fields.Integer(string=u"Быки 4-5 мес.", group_operator="avg")
	bik_5 = fields.Integer(string=u"Быки 5-6 мес.", group_operator="avg")
	bik_69 = fields.Integer(string=u"Быки 6-9 мес.", group_operator="avg")
	bik_912 = fields.Integer(string=u"Быки 9-12 мес.", group_operator="avg")
	bik_1215 = fields.Integer(string=u"Быки 12-15 мес.", group_operator="avg")
	bik_15 = fields.Integer(string=u"Быки >15 мес.", group_operator="avg")
	
	bik_itog_03 = fields.Integer(string=u"Итого Быки 0-3 мес.", store=True, compute='_raschet_bik_itog', group_operator="avg")
	bik_itog_36 = fields.Integer(string=u"Итого Быки 3-6 мес.", store=True, compute='_raschet_bik_itog', group_operator="avg")
	bik_itog_618 = fields.Integer(string=u"Итого Быки >6 мес.", store=True, compute='_raschet_bik_itog', group_operator="avg")
	bik_itog = fields.Integer(string=u"Итого Быков", store=True, compute='_raschet_bik_itog', group_operator="avg")
	

	#Коровы в разрезе лактаций
	cow_lakt_1 = fields.Integer(string=u"Коровы 1-я лактация", group_operator="avg")
	cow_lakt_2 = fields.Integer(string=u"Коровы 2-я лактация", group_operator="avg")
	cow_lakt_3 = fields.Integer(string=u"Коровы 3-я лактация", group_operator="avg")
	cow_lakt_4 = fields.Integer(string=u"Коровы >3 лактации", group_operator="avg")

	#Коровы в разрезе дней лактаций
	cow_040 = fields.Integer(string=u"Коровы 0-40 д.л", group_operator="avg")
	cow_41150 = fields.Integer(string=u"Коровы 41-150 д.л", group_operator="avg")
	cow_151300 = fields.Integer(string=u"Коровы 151-300 д.л", group_operator="avg")
	cow_300 = fields.Integer(string=u"Коровы >300 д.л", group_operator="avg")
	cow_suhostoy1 = fields.Integer(string=u"Коровы ранний сухостой", group_operator="avg")
	cow_suhostoy2 = fields.Integer(string=u"Коровы поздний сухостой", group_operator="avg")


