# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

#Загрузка отелов
class KRSLoadWiz(models.TransientModel):
	_name = 'multi.krs_load_wiz'


	date_start = fields.Date(string='Дата начала', required=True, default=fields.Datetime.now)
	date_end = fields.Date(string='Дата окончания', required=True, default=fields.Datetime.now)

	description = fields.Text(string=u"Коментарии")
	

	@api.one
	def load_otel(self):
		print ")))))))))))))))))))))))))))))))))))"
		import requests as r
		import json
		err=''
		conf = self.env['ir.config_parameter']
		ip = conf.get_param('ip_server_api')
	
		kod_otel = conf.get_param('kod_otel')
		
		print '>>>>>>>>>>>>>>>>> connect to ', ip
		
		dt_start = datetime.strptime(self.date_start,'%Y-%m-%d %H:%M:%S')
		
		date_start = dt.date().strftime('%d.%m.%Y')

		dt_end = datetime.strptime(self.date_start,'%Y-%m-%d %H:%M:%S')
		
		date_end = dt.date().strftime('%d.%m.%Y')



		url = 'http://'+ip+'/api/krs_load_otel/'+date_start+'/'+date_end+'/'+str(kod_otel)
		try:
			response=r.get(url)
		except:
			err=u'НЕ удалось соединиться с сервером'

		
		self.description = ''
		
		if len(err)==0:

			if response.status_code == 200:
				err=''
				otels = json.loads(response.text)
				self.description = otels
				# stado_struktura_line = self.env['stado.struktura_line']
				# del_line = stado_struktura_line.search([('stado_struktura_id',  '=',    self.id)])
				# del_line.unlink()
				
				# stado_zagon = self.env['stado.zagon']
				# struktura = json.loads(response.text)
				# zagon_ids = []
				# for line in struktura:
				# 	#print line['name']
				# 	zagon_id = stado_zagon.search([('uniform_id',   '=',    line['GROEPNR'])], limit=1)
				# 	if len(zagon_id)>0:

				# 		stado_struktura_line.create({
				# 					'stado_struktura_id':   self.id,
				# 					'stado_zagon_id':   zagon_id.id,
				# 					'kol_golov_zagon':  line['kol_golov_zagon'],
									
				# 					})
				# 		zagon_ids.append(zagon_id.id)

				# 	else:

				# 		err += u"Загон не найден:"+line['name'] + '   '
				# #Дополняем список загонов которые не получены из Uniform
				# not_zagon_ids = stado_zagon.search([('id',  'not in',   zagon_ids)], )
				# for line in not_zagon_ids:
				# 	stado_struktura_line.create({
				# 					'stado_struktura_id':   self.id,
				# 					'stado_zagon_id':   line.id,
				# 					'kol_golov_zagon':  0,
									
				# 					})


					
		#print err
		if len(err)>0:
			
			self.description = err
			#print '0000000000000000000000000000000000000000'
			# return exceptions.UserError(_(u"При загрузки произошли ошибки: %s" % (err,)))
		else:
			self.description += 'OK' 

