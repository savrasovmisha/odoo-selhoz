# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _
from openerp.exceptions import ValidationError
from datetime import datetime, timedelta
from itertools import groupby


class CustomPopMessage(models.TransientModel):
	_name = "custom.pop.message"

	name = fields.Char('Message')


#Загрузка отелов
class KRSLoadWiz(models.TransientModel):
	_name = 'multi.krs_load_wiz'


	date_start = fields.Date(string='Дата начала', required=True, default=fields.Datetime.now)
	date_end = fields.Date(string='Дата окончания', required=True, default=fields.Datetime.now)

	description = fields.Text(string=u"Коментарии")
	

	@api.multi
	def load_otel(self):
		print ")))))))))))))))))))))))))))))))))))"
		
		import requests as r
		import json
		err=''
		conf = self.env['ir.config_parameter']
		ip = conf.get_param('ip_server_api')
	
		kod_otel = conf.get_param('kod_otel')
		
		print '>>>>>>>>>>>>>>>>> connect to ', ip
		
		dt_start = datetime.strptime(self.date_start,'%Y-%m-%d')
		
		date_start = dt_start.date().strftime('%d.%m.%Y')

		dt_end = datetime.strptime(self.date_end,'%Y-%m-%d')
		
		date_end = dt_end.date().strftime('%d.%m.%Y')



		url = 'http://'+ip+'/api/krs_load_otel/'+date_start+'/'+date_end+'/'+str(kod_otel)
		print '>>>>>>>>>>>>>>>>> connect to ', url
		try:
			response=r.get(url)
		except:
			err=u'НЕ удалось соединиться с сервером'

		
		self.description = ''
		
		if len(err)==0:

			if response.status_code == 200:
				err=''
				otels = json.loads(response.text)
				#self.description = otels
				if len(otels)>0:

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
				else:
					err = u"Нет данных для загрузки"
							
		#print err
		if len(err)>0:
			
			self.description = u'Не возможно загрузить данные по причине: \n' + err
			# return exceptions.UserError(_(u"При загрузки произошли ошибки: %s" % (err,)))
		else:
			self.description += u'Данные загружены' 

		#print '0000000000000000000000000000000000000000'
		return {
				'name': 'Message',
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'multi.krs_load_wiz',
				'target':'new',
				'context':{'default_description':self.description} 
				}