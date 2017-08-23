# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _
from openerp.exceptions import ValidationError
from datetime import datetime, timedelta
from itertools import groupby
import requests as r
import json


class CustomPopMessage(models.TransientModel):
	_name = "custom.pop.message"

	name = fields.Char('Message')


def connect_server(self, url_name):

	"""Функция отправляет запрос на Сервер API и возвращает результат или ошибку
		url_name - имя функции сервера api. напр. /api/load_milk/
	"""


	err=''
	data=''
	conf = self.env['ir.config_parameter']
	ip = conf.get_param('ip_server_api')

	url = 'http://'+ip+url_name

	try:
		response=r.get(url)
		if response.text=='error':
			err = u'Сервер вернул ошибку, возможно не верно указаны данные. \n'
		if response.status_code == 200:
			data = json.loads(response.text)
			if len(data) == 0:
				err = u"Нет данных для загрузки. \n"


	except:
		err=u'НЕ удалось соединиться с сервером. \n'

	if err=='' and len(data) == 0:
		err=u'Сервер не вернул данные. Ошибка сервера API \n'

	return {
			'err' : err,
			'data' : data
			}





class KRSLoadWiz(models.TransientModel):

	""" Загрузка данных от сервера апи """


	_name = 'multi.krs_load_wiz'


	date_start = fields.Date(string='Дата начала', required=True, default=fields.Datetime.now)
	date_end = fields.Date(string='Дата окончания', required=True, default=fields.Datetime.now)

	otel = fields.Boolean(string=u"Отелы", default=False)
	hoz = fields.Boolean(string=u"Хозяйства рождения", default=False)
	spv = fields.Boolean(string=u"Причины выбытия", default=False)
	srashod = fields.Boolean(string=u"Виды расхода", default=False)
	cow_vibitiya = fields.Boolean(string=u"Выбытия коров", default=False)
	tel_vibitiya = fields.Boolean(string=u"Выбытия телят", default=False)
	osemeneniya = fields.Boolean(string=u"Осеменения", default=False)

	description = fields.Text(string=u"Коментарии", default=u'Результат:\n ')


	

	def return_form_wizard(self):

		"""Возвращает форму визарда. 
			Используется для того, что бы после выполнения действия не закрывался визард,
			 и отображались результат работы
		"""

		return {
				'name': 'Message',
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'multi.krs_load_wiz',
				'target':'new',
				'context':{
							'default_description':self.description,
							'default_date_start':self.date_start,
							'default_date_end':self.date_end
							} 
				}


	@api.multi
	def loads(self):

		"""Загрузка данных. В зависимости от выбранных параметров загружаются данные"""

		if self.otel == True:
			self.load_otel()

		if self.hoz == True:
			self.sync_hoz()

		if self.spv == True:
			self.sync_spv()

		if self.srashod == True:
			self.sync_srashod()

		if self.cow_vibitiya == True:
			self.load_cow_vibitiya()

		if self.tel_vibitiya == True:
			self.load_tel_vibitiya()

		if self.osemeneniya == True:
			self.load_osemeneniya()

		return self.return_form_wizard()


	
	


	
	def sync_hoz(self):
		"""
			Синхронизация справочника Хозяйства
		"""
		
		self.description += u'.... Синхронизация справочника Хозяйства .... \n' 
		err=''
		url_name = '/api/krs_sync_hoz/'
		
		res = connect_server(self, url_name)
		
		if len(res['err'])==0:

			for line in res['data']:
				krs_hoz = self.env['krs.hoz']
				hoz_line = krs_hoz.search([ ('selex_id',  '=',    int(line['selex_id'])) ],limit=1)

				if hoz_line:
					hoz_line.write({  
									'name': line['name'],
									'kod': line['kod']
									
								  })
				else:
					hoz_line.create({
								'name':line['name'],
								'kod': int(line['kod']),
								'selex_id': int(line['selex_id']),
							})

							
		#print err
		if len(res['err'])>0:
			
			self.description += u'Не возможно загрузить данные по причине: \n' + res['err']
			# return exceptions.UserError(_(u"При загрузки произошли ошибки: %s" % (err,)))
		else:
			self.description += u'Синхронизация прошла успешна. \n' 

		
		

	def sync_spv(self):
		"""
			Синхронизация справочника Причины выбытия
		"""
		
		self.description += u'.... Синхронизация справочника Причины выбытия .... \n' 
		err=''
		
		url_name = '/api/krs_sync_spv/'
				
		res = connect_server(self, url_name)
		
		if len(res['err'])==0:

			for line in res['data']:
				krs_spv = self.env['krs.spv']
				spv_line = krs_spv.search([ ('kod',  '=',    int(line['kod'])) ],limit=1)

				if spv_line:
					spv_line.write(  
									{'name': line['name']}
								  )
				else:
					krs_spv.create({
								'name':line['name'],
								'kod': int(line['kod']),
							
							
							})

				
							
		#print err
		if len(res['err'])>0:
			
			self.description += u'Не возможно загрузить данные по причине: \n' + res['err']
			# return exceptions.UserError(_(u"При загрузки произошли ошибки: %s" % (err,)))
		else:
			self.description += u'Синхронизация прошла успешна. \n' 

	

	def sync_srashod(self):
		"""
			Синхронизация справочника Виды расхода
		"""
		
		self.description += u'.... Синхронизация справочника Виды расхода .... \n' 
		err=''
		
		url_name = '/api/krs_sync_srashod/'
				
		res = connect_server(self, url_name)
		
		if len(res['err'])==0:

			for line in res['data']:
				krs_srashod = self.env['krs.srashod']
				srashod_line = krs_srashod.search([ ('kod',  '=',    int(line['kod'])) ],limit=1)

				if srashod_line:
					srashod_line.write(  
									{'name': line['name']}
								  )
				else:
					krs_srashod.create({
								'name':line['name'],
								'kod': int(line['kod']),
							
							
							})

				
							
		#print err
		if len(res['err'])>0:
			
			self.description += u'Не возможно загрузить данные по причине: \n' + res['err']
			# return exceptions.UserError(_(u"При загрузки произошли ошибки: %s" % (err,)))
		else:
			self.description += u'Синхронизация прошла успешна. \n'







	def load_otel(self):
		"""
			Загрузка Отелов
		"""
		
		self.description += u'.... Загрузка Отелов .... \n' 
		err=''
		conf = self.env['ir.config_parameter']
		
		kod_otel = conf.get_param('kod_otel')
		
		
		
		dt_start = datetime.strptime(self.date_start,'%Y-%m-%d')
		
		date_start = dt_start.date().strftime('%d.%m.%Y')

		dt_end = datetime.strptime(self.date_end,'%Y-%m-%d')
		
		date_end = dt_end.date().strftime('%d.%m.%Y')



		url_name = '/api/krs_load_otel/'+date_start+'/'+date_end+'/'+str(kod_otel)
		
		
		res = connect_server(self, url_name)
		
		if len(res['err'])==0:

			otels = res['data']
			
			#ПРОВЕРКА данных
			spisok_hoz_full = []
			spisok_result_full = []
			for line in otels:
				spisok_hoz_full.append(line['hoz_selex_id'])
				spisok_result_full.append([line['result']])

			#Группируем список, по уникальым значениям
			# spisok_hoz = [el for el, _ in groupby(spisok_hoz_full)]
			# spisok_result = [el for el, _ in groupby(spisok_result_full)]
			#print spisok_result
			#Проверяем существуют ли справочники
			for line, ob in groupby( sorted(spisok_result_full, key=lambda x:x[0]), key=lambda x:x[0] ):
				result_otel = self.env['krs.result_otel'].search([('name', '=', line)],limit=1)
				if len(result_otel) == 0:
					err += u"Для Результата отела: %s нет соответствия в справочники Результатов отела. \n " % (line,)
	
	
			for line in groupby( sorted(spisok_hoz_full) ):
				result_hoz = self.env['krs.hoz'].search([('selex_id', '=', line[0])],limit=1)
				if len(result_hoz) == 0:
					err += u"Для № хозяйства: %s нет соответствия в справочники Хозяйства. \n " % (line[0],)

			if len(err) == 0:
				
				krs_otel = self.env['krs.otel']
				del_line = krs_otel.search([ ('date',  '>=',    self.date_start),
											 ('date',  '<=',    self.date_end)
										   ])
				del_line.unlink()
				
				
				otel_ids = []
				for line in otels:
					

					new_otel = krs_otel.create({
									'inv_nomer':line['inv_nomer'],
									'date': line['date'],
									'nomer_lakt': int(line['nomer_lakt'])
								
								})
					new_otel._raschet_load(	 hoz_selex_id = int(line['hoz_selex_id']),
											 result = line['result']

											 )
				
		#print err
		if len(res['err'])>0 or len(err)>0:
			
			self.description += u'Не возможно загрузить данные по причине: \n' + res['err'] + err
			# return exceptions.UserError(_(u"При загрузки произошли ошибки: %s" % (err,)))
		else:
			self.description += u'Данные загружены. \n' 



	def load_cow_vibitiya(self):
		"""
			Загрузка Выбытия коров
		"""
		
		self.description += u'.... Загрузка Выбытия коров .... \n' 
		err=''
				
		
		dt_start = datetime.strptime(self.date_start,'%Y-%m-%d')
		
		date_start = dt_start.date().strftime('%d.%m.%Y')

		dt_end = datetime.strptime(self.date_end,'%Y-%m-%d')
		
		date_end = dt_end.date().strftime('%d.%m.%Y')



		url_name = '/api/krs_load_cow_vibitiya/'+date_start+'/'+date_end+'/'
		
		
		res = connect_server(self, url_name)
		
		if len(res['err'])==0:

			data = res['data']
			
			#ПРОВЕРКА данных
			spisok_hoz_full = []
			spisok_spv_full = []
			spisok_srashod_full = []
			for line in data:
				spisok_hoz_full.append(line['hoz_selex_id'])
				spisok_spv_full.append(line['kod_spv'])
				spisok_srashod_full.append(line['kod_srashod'])
				
			#print spisok_hoz_full
			#Группируем список, по уникальым значениям
			
			for line in groupby( sorted(spisok_hoz_full) ):

				result = self.env['krs.hoz'].search([('selex_id', '=', line[0])],limit=1)
				if len(result) == 0:
					err += u"Для № хозяйства: %s нет соответствия в справочники Хозяйства. \n " % (line[0],)


			for line in groupby( sorted(spisok_spv_full) ):

				result = self.env['krs.spv'].search([('kod', '=', line[0])],limit=1)
				if len(result) == 0:
					err += u"Для № %s нет соответствия в справочники Причины выбития. \n " % (line[0],)

			for line in groupby( sorted(spisok_srashod_full) ):

				result = self.env['krs.srashod'].search([('kod', '=', line[0])],limit=1)
				if len(result) == 0:
					err += u"Для № %s нет соответствия в справочники Вид расхода. \n " % (line[0],)



			if len(err) == 0:
				
				krs_cow_vibitiya = self.env['krs.cow_vibitiya']
				del_line = krs_cow_vibitiya.search([ ('date',  '>=',    self.date_start),
													 ('date',  '<=',    self.date_end)
												   ])
				del_line.unlink()
				
				
				cow_vibitiya_ids = []

				for line in data:
					
					new_cow_vibitiya = krs_cow_vibitiya.create({
									'inv_nomer':line['inv_nomer'],
									'date_rogd': line['date_rogd'],
									'date': line['date'],
									'nomer_lakt': int(line['nomer_lakt'])								
								})

					new_cow_vibitiya._raschet(	 hoz_selex_id = int(line['hoz_selex_id']),
												 kod_spv = int(line['kod_spv']), 
												 kod_srashod = int(line['kod_srashod'])
												 )
				
		#print err
		if len(res['err'])>0 or len(err)>0:
			
			self.description += u'Не возможно загрузить данные по причине: \n' + res['err'] + err
			# return exceptions.UserError(_(u"При загрузки произошли ошибки: %s" % (err,)))
		else:
			self.description += u'Данные загружены. \n' 



	def load_tel_vibitiya(self):
		"""
			Загрузка Выбытия телят
		"""
		
		self.description += u'.... Загрузка Выбытия телят .... \n' 
		err=''
				
		
		dt_start = datetime.strptime(self.date_start,'%Y-%m-%d')
		
		date_start = dt_start.date().strftime('%d.%m.%Y')

		dt_end = datetime.strptime(self.date_end,'%Y-%m-%d')
		
		date_end = dt_end.date().strftime('%d.%m.%Y')



		url_name = '/api/krs_load_tel_vibitiya/'+date_start+'/'+date_end+'/'
		
		
		res = connect_server(self, url_name)
		
		if len(res['err'])==0:

			data = res['data']
			
			#ПРОВЕРКА данных
			spisok_hoz_full = []
			spisok_spv_full = []
			spisok_srashod_full = []
			for line in data:
				spisok_hoz_full.append(line['hoz_selex_id'])
				spisok_spv_full.append(line['kod_spv'])
				spisok_srashod_full.append(line['kod_srashod'])
				
			#print spisok_hoz_full
			#Группируем список, по уникальым значениям
			
			for line in groupby( sorted(spisok_hoz_full) ):

				result = self.env['krs.hoz'].search([('selex_id', '=', line[0])],limit=1)
				if len(result) == 0:
					err += u"Для № хозяйства: %s нет соответствия в справочники Хозяйства. \n " % (line[0],)


			for line in groupby( sorted(spisok_spv_full) ):

				result = self.env['krs.spv'].search([('kod', '=', line[0])],limit=1)
				if len(result) == 0:
					err += u"Для № %s нет соответствия в справочники Причины выбития. \n " % (line[0],)

			for line in groupby( sorted(spisok_srashod_full) ):

				result = self.env['krs.srashod'].search([('kod', '=', line[0])],limit=1)
				if len(result) == 0:
					err += u"Для № %s нет соответствия в справочники Вид расхода. \n " % (line[0],)



			if len(err) == 0:
				
				krs_tel_vibitiya = self.env['krs.tel_vibitiya']
				del_line = krs_tel_vibitiya.search([ ('date',  '>=',    self.date_start),
													 ('date',  '<=',    self.date_end)
												   ])
				del_line.unlink()
				
				
				tel_vibitiya_ids = []

				for line in data:
					
					new_tel_vibitiya = krs_tel_vibitiya.create({
									'inv_nomer':line['inv_nomer'],
									'status':line['status'],
									'date_rogd': line['date_rogd'],
									'date': line['date']
																
								})

					new_tel_vibitiya._raschet(	 hoz_selex_id = int(line['hoz_selex_id']),
												 kod_spv = int(line['kod_spv']), 
												 kod_srashod = int(line['kod_srashod'])
												 )
				
		#print err
		if len(res['err'])>0 or len(err)>0:
			
			self.description += u'Не возможно загрузить данные по причине: \n' + res['err'] + err
			# return exceptions.UserError(_(u"При загрузки произошли ошибки: %s" % (err,)))
		else:
			self.description += u'Данные загружены. \n'



	def load_osemeneniya(self):
		"""
			Загрузка Осеменения
		"""
		
		self.description += u'.... Загрузка Осеменения .... \n' 
		err=''
				
		
		dt_start = datetime.strptime(self.date_start,'%Y-%m-%d')
		
		date_start = dt_start.date().strftime('%d.%m.%Y')

		dt_end = datetime.strptime(self.date_end,'%Y-%m-%d')
		
		date_end = dt_end.date().strftime('%d.%m.%Y')

		conf = self.env['ir.config_parameter']
		
		kod_osemeneniya = conf.get_param('kod_osemeneniya')

		url_name = '/api/krs_load_osemeneniya/'+date_start+'/'+date_end+'/'+str(kod_osemeneniya)
		
		
		res = connect_server(self, url_name)
		
		if len(res['err'])==0:

			data = res['data']
			
			if len(err) == 0:
				
				krs_osemeneniya = self.env['krs.osemeneniya']
				del_line = krs_osemeneniya.search([ ('date',  '>=',    self.date_start),
													 ('date',  '<=',    self.date_end)
												   ])
				del_line.unlink()
				
				
				osemeneniya_ids = []

				for line in data:
					
					new_osemeneniya = krs_osemeneniya.create({
									'inv_nomer':line['inv_nomer'],
									'status':line['status'],
									'date': line['date'],
									'fio': line['fio'],
									'bik': line['bik'],
									'doz': int(line['doz']),
																
								})

					new_osemeneniya._get_name()
				
		#print err
		if len(res['err'])>0 or len(err)>0:
			
			self.description += u'Не возможно загрузить данные по причине: \n' + res['err'] + err
			# return exceptions.UserError(_(u"При загрузки произошли ошибки: %s" % (err,)))
		else:
			self.description += u'Данные загружены. \n'