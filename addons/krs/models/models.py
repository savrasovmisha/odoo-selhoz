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

	vid_rashoda = fields.Selection([
		(u'Падеж', u"Падеж"),
		(u'Продажа', u"Продажа"),
		(u'Сдача на м/к', u"Сдача на м/к"),
		(u'Прочее', u"Прочее"),
		], default='', string=u'Вид расхода')

	







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
		

		self.tel_15_itog =  self.tel_15_stel + self.tel_15_neosem +self.tel_15_osem

	
	@api.one
	@api.depends(   'tel_0',
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
	@api.depends(   'bik_0',
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
		self.itog_pogolove = self.cow_itog_fur + self.tel_itog_tel_netel + self.bik_itog


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

	itog_pogolove = fields.Integer(string=u"Общее поголовье", default=0)


class krs_otchet_day(models.Model):
	_name = 'krs.otchet_day'
	_description = u'Ежедневная сводка по животноводству'
	_order = 'date desc'


	@api.one
	@api.depends('date')
	def _get_name(self):

		self.name = u"Ежедневная сводка по животноводсту за " + str(self.date)


	@api.one
	def action_zapolnit(self):

		nashe_ids = self.env['krs.hoz'].search([('nashe', '=', True),], limit=1)
		if len(nashe_ids)>0:
			nashe_id = nashe_ids[0].id

		tek_date = datetime.strptime(self.date,'%Y-%m-%d')
		nach_god = datetime.strptime(str(tek_date.year)+'-01-01', "%Y-%m-%d").date()

		
		last_day = tek_date - timedelta(days=1)
		last_day = last_day.date()

		#print "dddddddddd===",last_day
		try:
			last_god = tek_date.replace(year=tek_date.year - 1).date()
		except ValueError:
			
			assert tek_date.month == 2 and tek_date.day == 29 # can be removed
			last_god = tek_date.replace(month=2, day=28, year=tek_date.year-1).date()

		

		#--------- Отчет прошлого дня-------------------
		otchet_day_ids = self.env['krs.otchet_day'].search([
													('date', '=', last_day)
													], limit=1)
		if len(otchet_day_ids)>0:
			print '77777777777777777777'
			self.krs_otchet_day_lastday_id = otchet_day_ids[0].id

		#--------- Отчет прошлого года-------------------
		otchet_day_ids = self.env['krs.otchet_day'].search([
													('date', '=', last_god),
													], limit=1)
		if len(otchet_day_ids)>0:
			self.krs_otchet_day_lastgod_id = otchet_day_ids[0].id
			

		#---------ОТЕЛЫ ЗА ДЕНЬ ----------------
		
		#Отелы за день всего
		otel_day_ids = self.env['krs.otel'].search([('date', '=', self.date), ('abort', '=' ,False)])
		self.otel_day = sum(line.kol_itog for line in otel_day_ids)
		self.otel_day_jiv = sum(line.kol_itog_jiv for line in otel_day_ids)
		self.otel_day_mert = sum(line.kol_itog_mert for line in otel_day_ids)

		#Отелы за день по КОРОВАМ
		otel_day_ids = self.env['krs.otel'].search([('date', '=', self.date), 
													('abort', '=' ,False), 
													('nomer_lakt', '>' ,1)])        

		self.cow_otel_day = sum(line.kol_itog for line in otel_day_ids)
		self.cow_otel_day_jiv = sum(line.kol_itog_jiv for line in otel_day_ids)
		self.cow_otel_day_mert = sum(line.kol_itog_mert for line in otel_day_ids)

		#Отелы за день по Импортным НЕТЕЛЯМ
		otel_day_ids = self.env['krs.otel'].search([('date', '=', self.date), 
													('abort', '=' ,False),
													('nomer_lakt', '=' ,1), 
													('krs_hoz_id', '!=' ,nashe_id)])
		self.netel_imp_otel_day = sum(line.kol_itog for line in otel_day_ids)
		self.netel_imp_otel_day_jiv = sum(line.kol_itog_jiv for line in otel_day_ids)
		self.netel_imp_otel_day_mert = sum(line.kol_itog_mert for line in otel_day_ids)

		#Отелы за день по своим НЕТЕЛЯМ
		otel_day_ids = self.env['krs.otel'].search([('date', '=', self.date), 
													('abort', '=' ,False),
													('nomer_lakt', '=' ,1), 
													('krs_hoz_id', '=' ,nashe_id)])
		self.netel_otel_day = sum(line.kol_itog for line in otel_day_ids)
		self.netel_otel_day_jiv = sum(line.kol_itog_jiv for line in otel_day_ids)
		self.netel_otel_day_mert = sum(line.kol_itog_mert for line in otel_day_ids)
		#-----------------------------------------------------------------------



		#-----------------------------------------------------------------------
		#--------- ОТЕЛЫ С Н/Г-------------------

		#Отелы с н/г всего
		otel_ids = self.env['krs.otel'].search([
													('date', '>=', nach_god), 
													('date', '<=', self.date), 
													('abort', '=' ,False)])
		self.otel_god = sum(line.kol_itog for line in otel_ids)
		self.otel_god_jiv = sum(line.kol_itog_jiv for line in otel_ids)
		self.otel_god_mert = sum(line.kol_itog_mert for line in otel_ids)

		#Отелы с н/г по КОРОВАМ
		otel_ids = self.env['krs.otel'].search([    ('date', '>=', nach_god), 
													('date', '<=', self.date), 
													('abort', '=' ,False), 
													('nomer_lakt', '>' ,1)])        

		self.cow_otel_god = sum(line.kol_itog for line in otel_ids)
		self.cow_otel_god_jiv = sum(line.kol_itog_jiv for line in otel_ids)
		self.cow_otel_god_mert = sum(line.kol_itog_mert for line in otel_ids)

		#Отелы с н/г по Импортным НЕТЕЛЯМ
		otel_ids = self.env['krs.otel'].search([    ('date', '>=', nach_god), 
													('date', '<=', self.date),
													('abort', '=' ,False),
													('nomer_lakt', '=' ,1), 
													('krs_hoz_id', '!=' ,nashe_id)])
		self.netel_imp_otel_god = sum(line.kol_itog for line in otel_ids)
		self.netel_imp_otel_god_jiv = sum(line.kol_itog_jiv for line in otel_ids)
		self.netel_imp_otel_god_mert = sum(line.kol_itog_mert for line in otel_ids)

		#Отелы с н/г по своим НЕТЕЛЯМ
		otel_ids = self.env['krs.otel'].search([    ('date', '>=', nach_god), 
													('date', '<=', self.date),
													('abort', '=' ,False),
													('nomer_lakt', '=' ,1), 
													('krs_hoz_id', '=' ,nashe_id)])
		self.netel_otel_god = sum(line.kol_itog for line in otel_ids)
		self.netel_otel_god_jiv = sum(line.kol_itog_jiv for line in otel_ids)
		self.netel_otel_god_mert = sum(line.kol_itog_mert for line in otel_ids)

		#-----------------------------------------------------------------------

		
		#-----------------------------------------------------------------------
		#--------- ПАЛО ТЕЛЯТ ЗА ДЕНЬ-------------------
		krs_srashod_ids = self.env['krs.srashod'].search([('vid_rashoda', '=', u'Падеж'),])
		padej_ids = []
		for line in krs_srashod_ids:
			padej_ids.append(line.id)

		#print 'dddddddd===',padej_ids
		
		self.palo_tel_day = self.env['krs.tel_vibitiya'].search_count([
													('date', '=', self.date), 
													('krs_srashod_id', 'in', padej_ids), 
													])
		self.palo_tel01_day = self.env['krs.tel_vibitiya'].search_count([
													('date', '=', self.date), 
													('vozrast', '=', 0), 
													('krs_srashod_id', 'in', padej_ids), 
													])
		self.palo_tel12_day = self.env['krs.tel_vibitiya'].search_count([
													('date', '=', self.date), 
													('vozrast', '=', 1), 
													('krs_srashod_id', 'in', padej_ids), 
													])
		self.palo_tel23_day = self.env['krs.tel_vibitiya'].search_count([
													('date', '=', self.date), 
													('vozrast', '=', 2), 
													('krs_srashod_id', 'in', padej_ids), 
													])
		self.palo_tel3_day = self.env['krs.tel_vibitiya'].search_count([
													('date', '=', self.date), 
													('vozrast', '>', 2), 
													('krs_srashod_id', 'in', padej_ids), 
													])

		#-----------------------------------------------------------------------
		#--------- ПАЛО ТЕЛЯТ С Н/Г-------------------
		
		
		self.palo_tel_god = self.env['krs.tel_vibitiya'].search_count([
													('date', '>=', nach_god),
													('date', '<=', self.date), 
													('krs_srashod_id', 'in', padej_ids), 
													])
		self.palo_tel01_god = self.env['krs.tel_vibitiya'].search_count([
													('date', '>=', nach_god),
													('date', '<=', self.date), 
													('vozrast', '=', 0), 
													('krs_srashod_id', 'in', padej_ids), 
													])
		self.palo_tel12_god = self.env['krs.tel_vibitiya'].search_count([
													('date', '>=', nach_god),
													('date', '<=', self.date), 
													('vozrast', '=', 1), 
													('krs_srashod_id', 'in', padej_ids), 
													])
		self.palo_tel23_god = self.env['krs.tel_vibitiya'].search_count([
													('date', '>=', nach_god),
													('date', '<=', self.date), 
													('vozrast', '=', 2), 
													('krs_srashod_id', 'in', padej_ids), 
													])
		self.palo_tel3_god = self.env['krs.tel_vibitiya'].search_count([
													('date', '>=', nach_god),
													('date', '<=', self.date), 
													('vozrast', '>', 2), 
													('krs_srashod_id', 'in', padej_ids), 
													])
		

		

		#-----------------------------------------------------------------------
		#--------- ПАЛО КОРОВ-------------------
		
		
		self.palo_cow_day = self.env['krs.cow_vibitiya'].search_count([
													
													('date', '=', self.date), 
													('krs_srashod_id', 'in', padej_ids), 
													])
		self.palo_cow_god = self.env['krs.cow_vibitiya'].search_count([
													('date', '>=', nach_god),
													('date', '<=', self.date), 
													('krs_srashod_id', 'in', padej_ids), 
													])

		#-----------------------------------------------------------------------
		#--------- ОСЕМЕНЕНО КОРОВ-------------------
		
		
		self.osem_cow_day = self.env['krs.osemeneniya'].search_count([
													
													('date', '=', self.date), 
													('status', '=', u'Корова'), 
													])
		self.osem_cow_god = self.env['krs.osemeneniya'].search_count([
													('date', '>=', nach_god),
													('date', '<=', self.date), 
													('status', '=', u'Корова'), 
													])

		#-----------------------------------------------------------------------
		#--------- ОСЕМЕНЕНО ТЕЛЕЧЕК-------------------
		
		
		self.osem_tel_day = self.env['krs.osemeneniya'].search_count([
													
													('date', '=', self.date), 
													('status', '=', u'Телочка'), 
													])
		self.osem_tel_god = self.env['krs.osemeneniya'].search_count([
													('date', '>=', nach_god),
													('date', '<=', self.date), 
													('status', '=', u'Телочка'), 
													])

		#-----------------------------------------------------------------------
		#--------- ПРОДАЖА ТЕЛЯТ-------------------
		
		krs_srashod_ids = self.env['krs.srashod'].search([('vid_rashoda', '=', u'Продажа'),])
		podaja_ids = []
		for line in krs_srashod_ids:
			podaja_ids.append(line.id)

		self.prodaja_tel_day = self.env['krs.tel_vibitiya'].search_count([
													('date', '=', self.date), 
													('krs_srashod_id', 'in', podaja_ids), 
													])
		self.prodaja_tel_god = self.env['krs.tel_vibitiya'].search_count([
													('date', '>=', nach_god),
													('date', '<=', self.date), 
													('krs_srashod_id', 'in', podaja_ids), 
													])

		#-----------------------------------------------------------------------
		#--------- СДАЧА ТЕЛЯТ -------------------
		krs_srashod_ids = self.env['krs.srashod'].search([('vid_rashoda', '=', u'Сдача на м/к'),])
		sdacha_ids = []
		for line in krs_srashod_ids:
			sdacha_ids.append(line.id)  

		self.sdacha_tel_day = self.env['krs.tel_vibitiya'].search_count([
													('date', '=', self.date), 
													('krs_srashod_id', 'in', sdacha_ids), 
													])
		self.sdacha_tel_god = self.env['krs.tel_vibitiya'].search_count([
													('date', '>=', nach_god),
													('date', '<=', self.date), 
													('krs_srashod_id', 'in', sdacha_ids), 
													])

		#-----------------------------------------------------------------------
		#--------- СДАЧА КОРОВ -------------------
						
		self.sdacha_cow_day = self.env['krs.cow_vibitiya'].search_count([
													('date', '=', self.date), 
													('krs_srashod_id', 'in', sdacha_ids), 
													])
		self.sdacha_cow_god = self.env['krs.cow_vibitiya'].search_count([
													('date', '>=', nach_god),
													('date', '<=', self.date), 
													('krs_srashod_id', 'in', sdacha_ids), 
													])

		#-----------------------------------------------------------------------
		#--------- АБОРТЫ -------------------
						
		self.abort_day = self.env['krs.abort'].search_count([
													('date', '=', self.date), 
													])
		#Добавляем аборты из отелов
		self.abort_day += self.env['krs.otel'].search_count([
														('date', '=', self.date), 
														('abort', '=' ,True)
													])

		self.abort_god = self.env['krs.abort'].search_count([
													('date', '>=', nach_god),
													('date', '<=', self.date), 
													])
		#Добавляем аборты из отелов
		self.abort_god += self.env['krs.otel'].search_count([
														('date', '>=', nach_god),
														('date', '<=', self.date), 
														('abort', '=' ,True)
													])

		#--------- АБОРТЫ ОТ КОРОВ -------------------

		self.abort_cow_day = self.env['krs.abort'].search_count([
													('date', '=', self.date),
													('status', '=', u'Корова'),  
													])
		#Добавляем аборты из отелов
		self.abort_cow_day += self.env['krs.otel'].search_count([
														('date', '=', self.date), 
														('nomer_lakt', '>' ,1),
														('abort', '=' ,True)
													])
		self.abort_cow_god = self.env['krs.abort'].search_count([
													('date', '>=', nach_god),
													('date', '<=', self.date),
													('status', '=', u'Корова'),  
													])
		#Добавляем аборты из отелов
		self.abort_cow_god += self.env['krs.otel'].search_count([
														('date', '>=', nach_god),
														('date', '<=', self.date),
														('nomer_lakt', '>' ,1),
														('abort', '=' ,True)
													])





		#--------- АБОРТЫ ОТ НЕТЕЛЕЙ -------------------

		self.abort_netel_day = self.env['krs.abort'].search_count([
													('date', '=', self.date),
													('status', '=', u'Нетель'),  
													])
		#Добавляем аборты из отелов
		self.abort_netel_day += self.env['krs.otel'].search_count([
														('date', '=', self.date), 
														('nomer_lakt', '=' ,1),
														('abort', '=' ,True)
													])

		self.abort_netel_god = self.env['krs.abort'].search_count([
													('date', '>=', nach_god),
													('date', '<=', self.date),
													('status', '=', u'Нетель'),  
													])
		#Добавляем аборты из отелов
		self.abort_netel_god += self.env['krs.otel'].search_count([
														('date', '>=', nach_god),
														('date', '<=', self.date), 
														('nomer_lakt', '=' ,1),
														('abort', '=' ,True)
													])

		
		#--------- СТРУКТУРА СТАДА -------------------

		struktura_ids = self.env['krs.struktura'].search([
													('date', '=', self.date),
													], limit=1)
		if len(struktura_ids)>0:
			struktura = struktura_ids[0]

			#print 'ttttttttttttttt', struktura.cow_itog_fur

			self.cow_fur = struktura.cow_itog_fur
			self.cow_lakt = struktura.cow_itog_lakt
			self.cow_zapusk = struktura.cow_zapusk
			
			self.netel = struktura.tel_itog_netel
			self.tel = struktura.tel_itog
			self.bik = struktura.bik_itog

			self.cow_stel = struktura.cow_itog_stel
			self.cow_nestel = self.cow_fur - self.cow_stel

			self.tel_15_itog = struktura.tel_15_itog
			self.tel_15_stel = struktura.tel_15_stel
			self.tel_15_osem = struktura.tel_15_osem
			self.tel_15_neosem = struktura.tel_15_neosem

			self.itog_pogolove = self.cow_fur + self.netel + self.tel + self.bik



		#--------- МОЛОКО -------------------

		trace_milk_ids = self.env['milk.trace_milk'].search([
													('date_doc', '=', self.date),
													], limit=1)
		if len(trace_milk_ids)>0:
			trace_milk = trace_milk_ids[0]
			self.valoviy_nadoy_day = trace_milk.valoviy_nadoy
			self.otk_valoviy_nadoy_day = trace_milk.otk_valoviy_nadoy
			
			self.sale_milk_day = trace_milk.sale_natura
			self.sale_jir = trace_milk.sale_jir
			self.sale_belok = trace_milk.sale_belok

			self.nadoy_fur_day = trace_milk.nadoy_fur
			self.nadoy_doy_day = trace_milk.nadoy_doy
			self.otk_nadoy_fur_day = trace_milk.otk_nadoy_fur
			
			if self.krs_otchet_day_lastday_id:
				self.otk_sale_milk_day = self.sale_milk_day - self.krs_otchet_day_lastday_id.sale_milk_day


		#--------- МОЛОКО С Н/Г-------------------

		trace_milk_ids = self.env['milk.trace_milk'].search([
													('date_doc', '>=', nach_god),
													('date_doc', '<=', self.date), 
													],)
		
		
		self.valoviy_nadoy_god = sum(line.valoviy_nadoy for line in trace_milk_ids)
		self.nadoy_fur_god = sum(line.nadoy_fur for line in trace_milk_ids)
		
		self.nadoy_doy_god = sum(line.nadoy_doy for line in trace_milk_ids)
		





		
		
	name = fields.Char(string=u"Наименование", compute='_get_name', store=True, default=u"Ежедневная сводка по животноводсту за " + str(fields.Datetime.now))
	date = fields.Date(string='Дата сводки', required=True, default=fields.Datetime.now)

	krs_otchet_day_lastday_id = fields.Many2one('krs.otchet_day', string=u"Сводка за предыдущий день")
	krs_otchet_day_lastgod_id = fields.Many2one('krs.otchet_day', string=u"Сводка за предыдущий день года")

	valoviy_nadoy_day = fields.Integer(string=u"Валовое производство молока за день, кг", default=0)
	otk_valoviy_nadoy_day = fields.Integer(string=u"Разница с предыдущим днем +/-", default=0)
	
	valoviy_nadoy_god = fields.Integer(string=u"Валовое производство молока с н/г, кг", default=0)

	sale_milk_day = fields.Integer(string=u"Реализация молока за день, кг", default=0)
	sort = fields.Char(string=u"Сорт", default=u'в/с')
	
	sale_jir = fields.Float(digits=(3, 2), string=u"Жир, %")
	sale_belok = fields.Float(digits=(3, 2), string=u"Белок, %")
	otk_sale_milk_day = fields.Integer(string=u"Разница реализации с предудыщим днем, +/-", default=0)
	
	nadoy_fur_day = fields.Float(digits=(3, 2), string=u"Удой на фуражную за день, кг")
	nadoy_doy_day = fields.Float(digits=(3, 2), string=u"Удой на дойную за день, кг")
	
	otk_nadoy_fur_day = fields.Float(digits=(3, 2), string=u"Разница с предыдущим днем (фуражных), кг")


	nadoy_fur_god = fields.Float(digits=(3, 2), string=u"Удой на фуражную с н/г, кг")
	nadoy_doy_god = fields.Float(digits=(3, 2), string=u"Удой на дойную с н/г, кг")




	
	otel_day = fields.Integer(string=u"Отел за день всего", default=0)
	otel_day_jiv = fields.Integer(string=u"Отел за день живых", default=0)
	otel_day_mert = fields.Integer(string=u"Отел за день мертв.", default=0)

	cow_otel_day = fields.Integer(string=u"Отел за день от коров всего", default=0)
	cow_otel_day_jiv = fields.Integer(string=u"Отел за день от коров живых", default=0)
	cow_otel_day_mert = fields.Integer(string=u"Отел за день от коров мертв.", default=0)

	netel_imp_otel_day = fields.Integer(string=u"Отел за день от завезенных нетелей всего", default=0)
	netel_imp_otel_day_jiv = fields.Integer(string=u"Отел за день от завезенных нетелей живых", default=0)
	netel_imp_otel_day_mert = fields.Integer(string=u"Отел за день от завезенных нетелей мертв.х", default=0)

	netel_otel_day = fields.Integer(string=u"Отел за день от своих нетелей всего", default=0)
	netel_otel_day_jiv = fields.Integer(string=u"Отел за день от своих нетелей живых", default=0)
	netel_otel_day_mert = fields.Integer(string=u"Отел за день от своих нетелей мертв.", default=0)



	otel_god = fields.Integer(string=u"Отел с н/г всего", default=0)
	otel_god_jiv = fields.Integer(string=u"Отел с н/г живых", default=0)
	otel_god_mert = fields.Integer(string=u"Отел с н/г мертв.", default=0)

	cow_otel_god = fields.Integer(string=u"Отел с н/г от коров всего", default=0)
	cow_otel_god_jiv = fields.Integer(string=u"Отел с н/г от коров живых", default=0)
	cow_otel_god_mert = fields.Integer(string=u"Отел с н/г от коров мертв.", default=0)

	netel_imp_otel_god = fields.Integer(string=u"Отел с н/г от завезенных нетелей всего", default=0)
	netel_imp_otel_god_jiv = fields.Integer(string=u"Отел с н/г от завезенных нетелей живых", default=0)
	netel_imp_otel_god_mert = fields.Integer(string=u"Отел с н/г от завезенных нетелей мертв.", default=0)

	netel_otel_god = fields.Integer(string=u"Отел с н/г от своих нетелей всего", default=0)
	netel_otel_god_jiv = fields.Integer(string=u"Отел с н/г от своих нетелей живых", default=0)
	netel_otel_god_mert = fields.Integer(string=u"Отел с н/г от своих нетелей мертв.", default=0)

	

	palo_tel_day = fields.Integer(string=u"Пало телят за день всего", default=0)
	palo_tel01_day = fields.Integer(string=u"Пало телят за день 0-1", default=0)
	palo_tel12_day = fields.Integer(string=u"Пало телят за день 1-2", default=0)
	palo_tel23_day = fields.Integer(string=u"Пало телят за день 2-3", default=0)
	palo_tel3_day = fields.Integer(string=u"Пало телят за день 3 и старше", default=0)

	palo_tel_god = fields.Integer(string=u"Пало телят с н/г всего", default=0)
	palo_tel01_god = fields.Integer(string=u"Пало телят с н/г 0-1", default=0)
	palo_tel12_god = fields.Integer(string=u"Пало телят с н/г 1-2", default=0)
	palo_tel23_god = fields.Integer(string=u"Пало телят с н/г 2-3", default=0)
	palo_tel3_god = fields.Integer(string=u"Пало телят с н/г 3 и старше", default=0)


	palo_cow_day = fields.Integer(string=u"Пало взрослого скота за день", default=0)
	palo_cow_god = fields.Integer(string=u"Пало взрослого скота с н/г", default=0)


	osem_cow_day = fields.Integer(string=u"Осеменено коров за день", default=0)
	osem_cow_god = fields.Integer(string=u"Осеменено коров с н/г", default=0)

	osem_tel_day = fields.Integer(string=u"Осеменено телок за день", default=0)
	osem_tel_god = fields.Integer(string=u"Осеменено телок с н/г", default=0)

	prodaja_tel_day = fields.Integer(string=u"Продажа телят за день", default=0)
	prodaja_tel_god = fields.Integer(string=u"Продажа телят с н/г", default=0)

	sdacha_tel_day = fields.Integer(string=u"Сдача на м/к молодняка КРС за день", default=0)
	sdacha_tel_god = fields.Integer(string=u"Сдача на м/к молодняка КРС с н/г", default=0)

	sdacha_cow_day = fields.Integer(string=u"Сдача на м/к взрослый КРС за день", default=0)
	sdacha_cow_god = fields.Integer(string=u"Сдача на м/к взрослый КРС с н/г", default=0)


	cow_fur = fields.Integer(string=u"Поголовье фуражных коров", default=0)
	cow_lakt = fields.Integer(string=u"Лактируюших коров", default=0)
	cow_zapusk = fields.Integer(string=u"Запущенных коров", default=0)
	netel = fields.Integer(string=u"Нетелей", default=0)
	tel = fields.Integer(string=u"Телок", default=0)
	bik = fields.Integer(string=u"Бычков", default=0)

	cow_stel = fields.Integer(string=u"Стельных коров в стаде", default=0)
	cow_nestel = fields.Integer(string=u"Не стельных коров в стаде", default=0)
	tel_15_itog = fields.Integer(string=u"Телки старше 15 месяцев (в т.ч. нетели)", default=0)
	tel_15_stel = fields.Integer(string=u"Стельные Телки старше 15 месяцев", default=0)
	tel_15_osem = fields.Integer(string=u"Осемененные Телки старше 15 месяцев", default=0)
	tel_15_neosem = fields.Integer(string=u"Не осемененные Телки старше 15 месяцев", default=0)

	itog_pogolove = fields.Integer(string=u"Общее поголовье", default=0)


	abort_day = fields.Integer(string=u"Абортов за день", default=0)
	abort_god = fields.Integer(string=u"Абортов с н/г", default=0)

	abort_cow_day = fields.Integer(string=u"Абортов от коров за день", default=0)
	abort_cow_god = fields.Integer(string=u"Абортов от коров с н/г", default=0)

	abort_netel_day = fields.Integer(string=u"Абортов от нетелей за день", default=0)
	abort_netel_god = fields.Integer(string=u"Абортов от нетелей с н/г", default=0)



