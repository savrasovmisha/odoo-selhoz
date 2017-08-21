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

		return self.return_form_wizard()


	
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
				spisok_hoz_full.append(line['kod_hoz'])
				spisok_result_full.append(line['result'])

			#Группируем список, по уникальым значениям
			spisok_hoz = [el for el, _ in groupby(spisok_hoz_full)]
			spisok_result = [el for el, _ in groupby(spisok_result_full)]
			#print spisok_result
			#Проверяем существуют ли справочники
			for line in spisok_result:
				result_otel = self.env['krs.result_otel'].search([('name', '=', line)],limit=1)
				if len(result_otel) == 0:
					err += u"Для Результата отела: %s нет соответствия в справочники Результатов отела. \n " % (line,)
	
	
			for line in spisok_hoz:
				result_hoz = self.env['krs.hoz'].search([('kod', '=', line)],limit=1)
				if len(result_hoz) == 0:
					err += u"Для № хозяйства: %s нет соответствия в справочники Хозяйства. \n " % (line,)

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
									'kod_hoz': int(line['kod_hoz']),
									'date': line['date'],
									'nomer_lakt': int(line['nomer_lakt']),
									'result': line['result']
								
								})
					new_otel._raschet()
				
		#print err
		if len(res['err']) or len(err)>0:
			
			self.description += u'Не возможно загрузить данные по причине: \n' + res['err'] + err
			# return exceptions.UserError(_(u"При загрузки произошли ошибки: %s" % (err,)))
		else:
			self.description += u'Данные загружены. \n' 

		



	
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