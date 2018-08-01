# -*- coding: utf-8 -*-

from __future__ import division #при делении будет возвращаться float
from openerp import models, fields, api
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError
from work_date import week_magic, last_day_of_month



# class milk(models.Model):
#     _name = 'milk.milk'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

# class type_transport(models.Model):
# 	_name = 'milk.type_transport'
	
# 	name = fields.Char(string=u"Name", required=True)


# class transport(models.Model):
# 	_name = 'milk.transport'

# 	name = fields.Char(string=u"Name", default='New', required=True, copy=False, readonly=True, compute='_update_name', store=True)
# 	mark = fields.Char(string=u"Mark", required=True)
# 	gos_nomer = fields.Char(string=u"Gos nomer", required=True)
# 	type_transport_id = fields.Many2one('milk.type_transport', string=u"type_transport", default=None)
# 	max_value = fields.Integer(string=u"Грузоподъемность, кг") 
# 	# @api.one
# 	# @api.onchange('mark', 'gos_nomer')
# 	@api.depends('mark', 'gos_nomer')
# 	def _update_name(self):
# 		if self.mark and self.gos_nomer:
# 			self.name = self.mark + ' ' + self.gos_nomer


# class pricep(models.Model):
# 	_name = 'milk.pricep'

# 	name = fields.Char(string=u"Name", default='New', required=True, copy=False, readonly=True, compute='_update_name', store=True)
# 	type_transport_id = fields.Many2one('milk.type_transport', string=u"type_transport", default=None)
# 	gos_nomer = fields.Char(string=u"Gos nomer", required=True)

# 	# @api.onchange('gos_nomer')
# 	@api.depends('gos_nomer')
# 	def _update_name(self):
# 		if self.gos_nomer:
# 			self.name = self.gos_nomer



class tanker(models.Model):
	_name = 'milk.tanker'

	name = fields.Char(string=u"Name", required=True)
	max_size = fields.Integer(string=u"max size", required=True)
	#is_meter = fields.Boolean(string=u"is meter", default=False)
	#is_ves = fields.Boolean(string=u"Есть весы?", default=True)
	merilo = fields.Selection([
		(u'Весы', "Весы"),
		(u'Счетчик', "Счетчик"),
		(u'Линейка', "Линейка"),
	], default=u'Весы', string="Тип мерила")
	scale_tanker_id = fields.Many2one('milk.scale_tanker', string=u"scale_tanker", default=None)


class sale_milk(models.Model):
	_name = 'milk.sale_milk'
	_order = 'date_doc desc, id desc'
	
	#name = fields.Text(string=u"Name", required=True)
	name = fields.Char(string='Номер', required=True, copy=False, 
						readonly=True,  
						index=True, default='New')
	
	date_doc = fields.Datetime(string='Дата документа', required=True,  
						index=True, copy=False, default=fields.Datetime.now)
	is_next_day = fields.Boolean(string=u"Зачесть следующим днем?", default=False)
	date_ucheta = fields.Date(string='Дата учета', required=True,  
						index=True, copy=False, default=fields.Datetime.now,
						compute='_next_day', store=True)

	partner_id = fields.Many2one('res.partner', string='Партнер')
	voditel_id = fields.Many2one('res.partner', string='Водитель')
	transport_id = fields.Many2one('milk.transport', string='Транспорт')
	pricep_id = fields.Many2one('milk.pricep', string='Прицеп')
	split_line = fields.Boolean(string=u"Разбивать строки?", default=False)
	otpustil_id = fields.Many2one('res.partner', string='Отпустил')

	sale_milk_line = fields.One2many('milk.sale_milk_line', 'sale_milk_id', string=u"Строка Реализация молока")

	amount_ves_natura = fields.Integer( string=u"Вес натура", default=0, 
										readonly=True, compute='_amount_all', store=True, group_operator="sum")
	amount_ves_zachet = fields.Integer(string=u"Зачетный вес", default=0, 
										readonly=True, compute='_amount_all', store=True, group_operator="sum")
	avg_jir = fields.Float(digits=(3, 2), string=u"Среднее жир", default=0, 
										readonly=True, compute='_amount_all', store=True, group_operator="avg")
	avg_belok = fields.Float(digits=(3, 2), string=u"Среднее белок", default=0, 
										readonly=True, compute='_amount_all', store=True, group_operator="avg")
	avg_plotnost = fields.Float(digits=(4, 2), string=u"Среднее плотность", default=0, 
										readonly=True, compute='_amount_all', store=True, group_operator="avg")
	
	avg_som_kletki = fields.Integer(string=u"Сом. клетки", compute='_amount_all', store=True, group_operator="avg")
	avg_somo = fields.Float(digits=(4, 2), string=u"СОМО, %", compute='_amount_all', store=True, group_operator="avg")
	avg_antibiotik = fields.Char(string=u"Антиб.", default=u'отр.')
	avg_kislotnost = fields.Integer(string=u"Кислот- ность", default=u'17', compute='_amount_all', store=True, group_operator="avg")
	avg_temperatura = fields.Integer(string=u"Темпе- ратура", default=u'4', compute='_amount_all', store=True, group_operator="avg")

	description = fields.Text(string=u"Коментарии")

	@api.one
	@api.depends('date_doc','is_next_day')
	def _next_day(self):
		"""Если стоит Зачесть следующим днем то расчитаем дату учета как Дата документа + 1 день
			Иначе = Дата учета
		"""
		if self.date_doc and self.is_next_day==False:
			self.date_ucheta = self.date_doc
		if self.date_doc and self.is_next_day==True:
			d = datetime.strptime(self.date_doc, "%Y-%m-%d %H:%M:%S")
			self.date_ucheta = d + timedelta(days=1)





	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New' or vals.get('name', 'New') == None:
			vals['name'] = self.env['ir.sequence'].next_by_code('milk.sale_milk') or 'New'

		#if not self.amount_ves_natura:
		#	self.amount_ves_natura = 0
		#if not self.amount_ves_zachet:
		#	self.amount_ves_zachet = 0	

		result = super(sale_milk, self).create(vals)
		return result

	#@api.one
	#@api.onchange('sale_milk_line.ves_natura', 'sale_milk_line.ves_zachet')
	@api.depends(	'sale_milk_line.tanker_id',
					'sale_milk_line.meter_value',
					'sale_milk_line.jir',
					'sale_milk_line.belok',
					'sale_milk_line.plotnost', 
					'sale_milk_line.ves_natura',
					'sale_milk_line.som_kletki',
					'sale_milk_line.somo',
					'sale_milk_line.kislotnost',
					'sale_milk_line.temperatura'
					)
	def _amount_all(self):
		"""
		Compute the total amounts of the SO.
		"""
		
		self.amount_ves_natura = 0
		self.amount_ves_zachet = 0
		self.avg_jir = 0
		self.avg_belok = 0
		self.avg_plotnost = 0
		self.avg_som_kletki = 0
		self.avg_somo = 0
		self.avg_kislotnost = 0
		self.avg_temperatura = 0
		_sum_jir = 0.00
		_sum_belok = 0.00
		_sum_plotnost = 0.00
		_sum_som_kletki = 0.0
		_sum_somo = 0.00
		_sum_kislotnost = 0.0
		_sum_temperatura = 0.0
		
		for line in self.sale_milk_line:
			self.amount_ves_natura += line.ves_natura
			self.amount_ves_zachet += line.ves_zachet
			_sum_jir += line.jir * line.ves_natura
			_sum_belok += line.belok * line.ves_natura
			_sum_plotnost += line.plotnost * line.ves_natura
			_sum_som_kletki += line.som_kletki * line.ves_natura
			_sum_somo += line.somo * line.ves_natura
			_sum_kislotnost += line.kislotnost * line.ves_natura
			_sum_temperatura += line.temperatura * line.ves_natura
		
		if self.amount_ves_natura>0:
			self.avg_jir = _sum_jir / self.amount_ves_natura
			self.avg_belok = _sum_belok / self.amount_ves_natura	
			self.avg_plotnost = _sum_plotnost / self.amount_ves_natura	
			self.avg_som_kletki = round(_sum_som_kletki / self.amount_ves_natura)	
			self.avg_somo = _sum_somo / self.amount_ves_natura	
			self.avg_kislotnost = round(_sum_kislotnost / self.amount_ves_natura)	
			self.avg_temperatura = round(_sum_temperatura / self.amount_ves_natura)	


	def create_ttn(self, cr, uid, ids, context=None):
		s_m = self.browse(cr, uid, ids[0], context=context)
		
		#print "жжжжжжжжжжж===",s_m.date_doc
		if s_m.split_line:
			s_m_line = s_m.sale_milk_line
		else:
			s_m_line = [{"jir": s_m.avg_jir,
						 "belok": s_m.avg_belok, 
						 "plotnost": s_m.avg_plotnost, 
						 "ves_natura": s_m.amount_ves_natura, 
						 "antibiotik": s_m.avg_antibiotik,
						 "som_kletki": s_m.avg_som_kletki,
						 "somo": s_m.avg_somo,
						 "kislotnost": s_m.avg_kislotnost,
						 "temperatura": s_m.avg_temperatura
						 },]

		import sys
		import os
		import base64
		import zipfile
		import tempfile

		reload(sys)
		sys.setdefaultencoding("utf-8")
		
		dir_name = os.path.dirname(__file__)
		
		shablon_name = dir_name+'/ttnShablon.ods'

		tmp_dir = tempfile.mkdtemp()

		file_name = 'TTN'

		output_filename = tmp_dir + '/TTN.ods'
		pdf_output_filename = tmp_dir + '/TTN.pdf'

		
		def write_and_close_docx (self, xml_content, output_filename):
			""" Create a temp directory, expand the original docx zip.
			Write the modified xml to word/document.xml
			Zip it up as the new docx
			"""

			tmp_dir = tempfile.mkdtemp()

			self.extractall(tmp_dir)
			
			with open(os.path.join(tmp_dir,'content.xml'), 'w') as f:
				#xmlstr = etree.tostring (xml_content, pretty_print=True)
				f.write(xml_content)

			# Get a list of all the files in the original docx zipfile
			filenames = self.namelist()
			# Now, create the new zip file and add all the filex into the archive
			zip_copy_filename = output_filename
			with zipfile.ZipFile(zip_copy_filename, "w") as docx:
				for filename in filenames:
					docx.write(os.path.join(tmp_dir,filename), filename)
			import shutil
			# Clean up the temp dir
			shutil.rmtree(tmp_dir)
			#return tmp_dir+'/'+output_filename

		z = zipfile.ZipFile(shablon_name)
		data = z.read('content.xml')
		# data = data.replace('"{{', '{{')
		# data = data.replace('}}"', '}}')



		from bottle import jinja2_template as template

		
		f = template(data, s_m=s_m, sale_milk_line=s_m_line)

		write_and_close_docx(z, f, output_filename)
		import subprocess
		cmd = 'libreoffice --headless --convert-to pdf --outdir '+tmp_dir+' '+ output_filename
		print 'Generate ODS to PGF..........................', cmd
		
		p = subprocess.Popen(cmd, shell = True)
		p.wait()
		#export_id = self.pool.get('excel.extended').create(cr, uid, {'excel_file': base64.encodestring(open(output_filename,"rb").read()), 'file_name': 'TTN.ods'}, context=context)
		export_id = self.pool.get('excel.extended').create(cr, uid, 
					{'excel_file': base64.encodestring(open(output_filename,"rb").read()), 'file_name': 'TTN.ods',
					'pdf_file': base64.encodestring(open(pdf_output_filename,"rb").read()), 'pdf_file_name': 'TTN.pdf'}, context=context)

		return{

			'view_mode': 'form',

		'res_id': export_id,

		'res_model': 'excel.extended',

		'view_type': 'form',

		'type': 'ir.actions.act_window',

		'context': context,

		'target': 'new',

		}   

	

class shkala_tanker5(models.Model):
	_name = 'milk.shkala_tanker5'
	name = fields.Float(digits=(5, 1), string=u"Pokazanie", required=True)
	value = fields.Integer(string=u"Value", required=True)

class scale_tanker(models.Model):
	_name = 'milk.scale_tanker'
	name = fields.Char(string='Name', required=True, copy=False, 
						readonly=False,  
						index=True, default='New')
	scale_tanker_line = fields.One2many('milk.scale_tanker_line', 'scale_tanker_id', string=u"Scale tanker line")	

class scale_tanker_line(models.Model):
	_name = 'milk.scale_tanker_line'
	def return_name(self):
		self.name = self.scale_tanker_id.name
	name = fields.Text(string='Description', required=True, default='New', compute='return_name', store=True)
	value = fields.Float(digits=(5, 1), string=u"Value", required=True)
	result = fields.Integer(string=u"Result", required=True)
	scale_tanker_id = fields.Many2one('milk.scale_tanker',
		ondelete='cascade', string=u"scale_tanker", required=True)


class sale_milk_line(models.Model):
	_name = 'milk.sale_milk_line'
	
	def return_name(self):
		self.name = self.tanker_id.name
	name = fields.Text(string='Description', required=True, default='New', compute='return_name', store=True)
	tanker_id = fields.Many2one('milk.tanker', string=u"tanker", required=True)
	meter_value = fields.Integer(string=u"meter value", required=True)
	jir = fields.Float(digits=(3, 2))
	belok = fields.Float(digits=(3, 2))
	plotnost = fields.Float(digits=(4, 2))
	ves_natura = fields.Integer(string=u"В натуре",  store=True)
	ves_zachet = fields.Integer(string=u"Зачетный вес", compute='_raschet', store=True)
	som_kletki = fields.Integer(string=u"Сом. клетки")
	somo = fields.Float(digits=(4, 2))
	antibiotik = fields.Char(string=u"Антиб.", default=u'отр.')
	kislotnost = fields.Integer(string=u"Кислот- ность", default=u'17')
	temperatura = fields.Integer(string=u"Темпе- ратура", default=u'4')

	
	sale_milk_id = fields.Many2one('milk.sale_milk',
		ondelete='cascade', string=u"Sale milk", required=True)

	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New' or vals.get('name', 'New') == None:
			vals['name'] = self.env['ir.sequence'].next_by_code('milk.sale_milk_line') or 'New'

		result = super(sale_milk_line, self).create(vals)
		return result

	@api.one
	#@api.onchange('tanker_id','meter_value','jir','belok','plotnost', 'ves_natura')
	@api.depends('tanker_id','meter_value','jir','belok','plotnost')
	def _raschet(self):
		if self.meter_value and self.jir and self.belok and self.plotnost:
			if self.tanker_id.merilo == u'Весы':
				self.ves_natura = self.meter_value
			elif self.tanker_id.merilo == u'Счетчик':
				self.ves_natura = round(self.meter_value * (1+self.plotnost/1000))
			else:
				pok = self.env['milk.scale_tanker_line'].search([('value', '=', self.meter_value),
														('scale_tanker_id', '=', self.tanker_id.scale_tanker_id.id)], 
														limit=1).result

				self.ves_natura = round(pok * (1+self.plotnost/1000))
			self.ves_zachet = round(self.ves_natura * (self.jir*0.5/3.4 + self.belok*0.5/3))
	
	@api.one
	#@api.onchange('tanker_id','meter_value','jir','belok','plotnost', 'ves_natura')
	@api.onchange('ves_natura')
	def _raschet1(self):
		if self.meter_value and self.jir and self.belok and self.plotnost:
			self.ves_zachet = round(self.ves_natura * (self.jir*0.5/3.4 + self.belok*0.5/3))


	merilo = fields.Char(string=u"Meter", compute='_is_meter', readonly=True, default='')
	


	@api.one
#	@api.onchange('tanker_id')
	@api.depends('tanker_id')
	def _is_meter(self):
		if self.tanker_id:
			self.merilo = self.tanker_id.merilo
		else:
			self.merilo = ''









class inventory_excel_extended(models.Model):

	_name= "excel.extended"

	excel_file = fields.Binary('Скачать отчет в Excel')

	file_name = fields.Char('Excel файл', size=64)

	pdf_file = fields.Binary('Скачать отчет в PDF')

	pdf_file_name = fields.Char('PDF файл', size=64)



class control_sale_milk(models.Model):
	_name = 'milk.control_sale_milk'
	
	@api.one
	@api.depends('month', 'year')
	def return_name(self):
		self.name = self.year + '-' + self.month
	name = fields.Char(string='Номер', required=True, default='New', compute='return_name', store=True)
	# date_doc = fields.Datetime(string='Дата документа', required=True,  
	# 					index=True, copy=False, default=fields.Datetime.now)
	
	month = fields.Selection([
		('1', "Январь"),
		('2', "Февряль"),
		('3', "Март"),
		('4', "Апрель"),
		('5', "Май"),
		('6', "Июнь"),
		('7', "Июль"),
		('8', "Август"),
		('9', "Сентябрь"),
		('10', "Октябрь"),
		('11', "Ноябрь"),
		('12', "Декабрь"),
	], default=str(datetime.today().month), required=True)
	
	year = fields.Char(string=u"Год", required=True, default=str(datetime.today().year))
	
	partner_id = fields.Many2one('res.partner', string='Партнер')

	control_sale_milk_line = fields.One2many('milk.control_sale_milk_line', 'control_sale_milk_id', string=u"Строка Сверка реализации молока")

	amount_ot_ves_natura = fields.Integer( string=u"От. Вес натура", default=0, 
										readonly=True, compute='_amount_all', store=True, group_operator="sum")
	amount_pt_ves_natura = fields.Integer( string=u"Пр. Вес натура", default=0, 
										readonly=True, compute='_amount_all', store=True, group_operator="sum")
	amount_ot_ves_zachet = fields.Integer( string=u"От. Зачет", default=0, 
										readonly=True, compute='_amount_all', store=True, group_operator="sum")
	amount_pr_ves_zachet = fields.Integer( string=u"Пр. Зачет", default=0, 
										readonly=True, compute='_amount_all', store=True, group_operator="sum")

	otklonene_ves_natura = fields.Integer( string=u"Отклонение Вес натура", default=0, 
										readonly=True, compute='_amount_all', store=True, group_operator="sum")
	otklonene_ves_zachet = fields.Integer( string=u"Отклонение Зачет", default=0, 
										readonly=True, compute='_amount_all', store=True, group_operator="sum")

	description = fields.Text(string=u"Коментарии")

	@api.depends(	'control_sale_milk_line.day', 
					'control_sale_milk_line.pr_ves_natura', 
					'control_sale_milk_line.pr_ves_zachet',
					'control_sale_milk_line.sale_milk_id' )
	def _amount_all(self):
		"""
		Compute the total amounts of the SO.
		"""
		
		self.amount_ot_ves_natura = 0
		self.amount_pt_ves_natura = 0
		self.amount_ot_ves_zachet = 0
		self.amount_pr_ves_zachet = 0
				
		for line in self.control_sale_milk_line:
			self.amount_ot_ves_natura += line.ot_ves_natura
			self.amount_pt_ves_natura += line.pr_ves_natura
			self.amount_ot_ves_zachet += line.ot_ves_zachet
			self.amount_pr_ves_zachet += line.pr_ves_zachet

		self.otklonene_ves_natura = self.amount_pt_ves_natura - self.amount_ot_ves_natura
		self.otklonene_ves_zachet = self.amount_pr_ves_zachet - self.amount_ot_ves_zachet

	

class control_sale_milk_line(models.Model):
	_name = 'milk.control_sale_milk_line'
	
	
	def return_name(self):
		self.name = self.day

	name = fields.Char(string='Description', required=True, default='New', compute='return_name', store=True)
	
	day = fields.Char(string='День', #required=True,  
						index=True, copy=False)
	sale_milk_id = fields.Many2one('milk.sale_milk', string='Док-т реал-и')

	control_sale_milk_id = fields.Many2one('milk.control_sale_milk',
		ondelete='cascade', string=u"Control Sale milk", required=True)

	ot_jir = fields.Float(digits=(3, 1), readonly=True,  store=True, compute='_result')
	ot_belok = fields.Float(digits=(3, 2), readonly=True,  store=True, compute='_result')
	
	ot_ves_natura = fields.Integer(string=u"От. натура", readonly=True,  store=True, compute='_result')
	ot_ves_zachet = fields.Integer(string=u"От. зачет", readonly=True,  store=True, compute='_result')

	pr_jir = fields.Float(digits=(3, 1))
	pr_belok = fields.Float(digits=(3, 2))
	
	pr_ves_natura = fields.Integer(string=u"Пр. натура", store=True)
	pr_ves_zachet = fields.Integer(string=u"Пр. зачет", store=True)

	# @api.onchange('day')
	# def _verify_valid_day(self):
	# 	print 'dddddddddddddddddddddddddddddddd'
	# 	if self.day <= 0 or self.day > 31 :
	# 		return {
	# 			'warning': {
	# 			'title': "Неверное значение поля День",
	# 			'message': "День не может быть меньше или равным 0, а также больше 31",
	# 			},
	# 		}


	@api.one
	#@api.onchange('sale_milk_id')
	@api.depends('day', 'sale_milk_id')
	def _result(self):
		
		self.ot_ves_natura = 0
		self.ot_ves_zachet = 0
		self.ot_jir = 0
		self.ot_belok = 0

		if self.sale_milk_id:
			#print 'fffffffffffffffffffffffffffffffffffffffff', self.sale_milk_id.partner_id.name
			#sm = self.sale_milk_id
			self.ot_ves_natura = self.sale_milk_id.amount_ves_natura
			self.ot_ves_zachet = self.sale_milk_id.amount_ves_zachet
			self.ot_jir = self.sale_milk_id.avg_jir
			self.ot_belok = self.sale_milk_id.avg_belok

		if self.day and not self.sale_milk_id:
			d = datetime.strptime(self.control_sale_milk_id.year+'-'+self.control_sale_milk_id.month+'-'+self.day, "%Y-%m-%d")
			#print d
			#Convert date type from datetime.date type into string
			d1 = datetime.strftime(d, "%Y-%m-%d 0:0:0")
			d2 = datetime.strftime(d, "%Y-%m-%d 23:59:59")
			
			_sum_ot_ves_natura = 0
			_sum_ot_ves_zachet = 0
			_sum_ot_jir = 0 	#Для расчета средневзвешенного
			_sum_ot_belok = 0
			list_sm = self.env['milk.sale_milk'].search_read([('date_doc', '>=', d1), ('date_doc', '<=', d2)])
			#print 'dddddddddddddddd======',list_sm
			for sm in list_sm:
				#print list_sm[sm].name
				_sum_ot_ves_natura += sm['amount_ves_natura']
				_sum_ot_ves_zachet += sm['amount_ves_zachet']
				_sum_ot_jir += sm['avg_jir']*sm['amount_ves_natura'] 	#Для расчета средневзвешенного
				_sum_ot_belok += sm['avg_belok']*sm['amount_ves_natura']
			
			self.ot_ves_natura = _sum_ot_ves_natura
			self.ot_ves_zachet = _sum_ot_ves_zachet
			if _sum_ot_ves_natura>0:
				self.ot_jir = _sum_ot_jir/_sum_ot_ves_natura
				self.ot_belok =_sum_ot_belok/_sum_ot_ves_natura

		
			

class trace_milk(models.Model):
	_name = 'milk.trace_milk'		
	"""Учет движения молока"""
	@api.one
	@api.depends('date_doc')
	def return_name(self):
		self.name = self.date_doc
		self.date = self.date_doc

		
	name = fields.Char(string='Description', required=True, default='New', store=True, compute='return_name')
	
	date_doc = fields.Date(string='Дата документа', required=True,  
						index=True, copy=False, default=fields.Datetime.now)
	date = fields.Date(string='Дата документа', required=True,  
						index=True, copy=False)

	doyarka_id = fields.Many2one('res.partner', string='Доярка')
	
	parabone = fields.Integer(string=u"Получено с parabone", store=True, help=u'Молоко полученное с PARABONE, необходимо для распределения молока на загоны с маститными коровами')
	vipoyka = fields.Integer(string=u"На выпойку", store=True, compute='_raschet_vipoyka')
	utilizaciya = fields.Integer(string=u"Утилизированно", store=True)
	sale_natura = fields.Integer(string=u"Реализованно", store=True, compute='_sale_result')
	sale_zachet = fields.Integer(string=u"Зачетный вес", store=True, compute='_sale_result')
	ostatok_today = fields.Integer(string=u"Остаток, сегодня", store=True, compute='_raschet_ostatok')
	ostatok_lastday = fields.Integer(string=u"Остаток, вчера", store=True, compute='_sale_result')
	
	sale_jir = fields.Float(digits=(3, 1), string=u"Жир", store=True, compute='_sale_result', group_operator="avg")
	sale_belok = fields.Float(digits=(3, 2), string=u"Белок", store=True, compute='_sale_result', group_operator="avg")
	
	valoviy_nadoy = fields.Integer(string=u"Валовый надой, кг", store=True, compute='_valoviy_nadoy_result')
	otk_valoviy_nadoy = fields.Float(digits=(3, 3), string=u"Откл-е Валовый надой от предыд. дня, кг", compute='_otk_result', store=False)

	sale_peresdali_natura = fields.Integer(string=u"Пересдали натура", store=True, compute='_sale_result')
	sale_peresdali_zachet = fields.Integer(string=u"Пересдали зачет", store=True, compute='_sale_result')

	cow_doy = fields.Integer(string=u"Дойные", store=True, group_operator="avg")
	cow_zapusk = fields.Integer(string=u"В запуске", store=True, group_operator="avg")
	cow_fur = fields.Integer(string=u"Фуражные", store=True, compute='_nadoy_result', group_operator="avg")
	cow_netel = fields.Integer(string=u"Нетели", store=True, group_operator="avg")
	cow_total = fields.Integer(string=u"Общее поголовье", store=True, group_operator="avg")

	nadoy_doy = fields.Float(digits=(3, 1), string=u"Надой на дойную, кг", store=True, compute='_nadoy_result', group_operator="avg")
	nadoy_fur = fields.Float(digits=(3, 1), string=u"Надой на фуражную, кг", store=True, compute='_nadoy_result', group_operator="avg")
	otk_nadoy_doy = fields.Float(digits=(3, 1), string=u"Откл-е от предыд. дня, кг", compute='_otk_result', store=False)
	otk_nadoy_fur = fields.Float(digits=(3, 1), string=u"Откл-е от предыд. дня, кг", compute='_otk_result', store=False)

	nadoy_0_40 = fields.Float(digits=(3, 2), string=u"Надой 0-40", store=True, group_operator="avg")
	nadoy_40_150 = fields.Float(digits=(3, 2), string=u"Надой 40-150", store=True, group_operator="avg")
	nadoy_150_300 = fields.Float(digits=(3, 2), string=u"Надой 150-300", store=True, group_operator="avg")
	nadoy_300 = fields.Float(digits=(3, 2), string=u"Надой >300", store=True, group_operator="avg")

	otk_0_40 = fields.Float(digits=(3, 2), string=u"Откл-е Надой 0-40", compute='_otk_nadoy_result', store=False, group_operator="avg")
	otk_40_150 = fields.Float(digits=(3, 2), string=u"Откл-е 40-150", compute='_otk_nadoy_result', store=False, group_operator="avg")
	otk_150_300 = fields.Float(digits=(3, 2), string=u"Откл-е 150-300", compute='_otk_nadoy_result', store=False, group_operator="avg")
	otk_300 = fields.Float(digits=(3, 2), string=u"Откл-е >300", compute='_otk_nadoy_result', store=False, group_operator="avg")

	description = fields.Text(string=u"Коментарии")
	trace_milk_ostatok_line = fields.One2many('milk.trace_milk_ostatok_line', 'trace_milk_id', string=u"Строка Учет движения молока Остотки в танкерах")
	trace_milk_vipoyka_line = fields.One2many('milk.trace_milk_vipoyka_line', 'trace_milk_id', string=u"Строка Учет движения молока На выпойку")
	state = fields.Selection([
		('create', "Создан"),
		('draft', "Черновик"),
		('confirmed', "Проведен"),
		('done', "Отменен"),
		
	], default='create')

	@api.one
	def action_update(self):
		"""Действие при нажати на кнопку обновить. Пересчитаем"""
		self._sale_result()
		self._raschet_ostatok()
		self._valoviy_nadoy_result()
		self._nadoy_result()
		self._otk_result()
		self._otk_nadoy_result()
		self._raschet_vipoyka()

	
	@api.one
	@api.constrains('date_doc')
	def constrains_name(self):
		"""Проверяем есть ли документ с такой же датой, если есть то выдаем ошибку"""
		kol_doc = self.search_count([('date_doc', '=', self.date_doc)])
		if kol_doc>1:
			raise ValidationError(('Документ с датой %s уже существует'% self.date_doc))
	

	@api.one
	@api.depends('date_doc')
	def _sale_result(self):
		
		self.sale_natura = 0
		self.sale_zachet = 0
		self.sale_jir = 0
		self.sale_belok = 0

		if self.date_doc:
			_sum_natura = 0
			_sum_zachet = 0
			_sum_jir = 0 	#Для расчета средневзвешенного
			_sum_belok = 0
			
			#Выборка по Дате учета
			list_sm = self.env['milk.sale_milk'].search_read([('date_ucheta', '=', self.date_doc)])
			
			for sm in list_sm:
				#print list_sm[sm].name
				_sum_natura += sm['amount_ves_natura']
				_sum_zachet += sm['amount_ves_zachet']
				_sum_jir += sm['avg_jir']*sm['amount_ves_natura'] 	#Для расчета средневзвешенного
				_sum_belok += sm['avg_belok']*sm['amount_ves_natura']
			
			self.sale_natura = _sum_natura
			self.sale_zachet = _sum_zachet
			
			if _sum_natura>0:
				self.sale_jir = _sum_jir/_sum_natura
				self.sale_belok =_sum_belok/_sum_natura

			#Расчет Пересдали
			
			d = datetime.strptime(self.date_doc, "%Y-%m-%d")
			date_ucheta = d + timedelta(days=1)
			
			list_sm = self.env['milk.sale_milk'].search_read([('is_next_day', '=', True),('date_ucheta', '=', date_ucheta)])
			
			_sum_natura = 0
			_sum_zachet = 0

			for sm in list_sm:
				#print list_sm[sm].name
				_sum_natura += sm['amount_ves_natura']
				_sum_zachet += sm['amount_ves_zachet']
			
			self.sale_peresdali_natura = _sum_natura
			self.sale_peresdali_zachet = _sum_zachet


			#Остаток с предыдущего дня
			prev_date = d - timedelta(days=1)
			
			cm = self.env['milk.trace_milk'].search([('date_doc', '=', prev_date)], limit=1)
			if len(cm)>0:
				self.ostatok_lastday = cm.ostatok_today

			#Получаем структуру стада на текущий день
			ss = self.env['krs.struktura'].search([('date', '=', self.date_doc)], limit=1)
			if len(ss)>0:
				self.cow_doy = ss.cow_itog_lakt
				self.cow_zapusk = ss.cow_zapusk
				self.cow_fur = self.cow_doy + self.cow_zapusk


			
	@api.one
	@api.depends('vipoyka','utilizaciya','date_doc', 'ostatok_today', 'ostatok_lastday')
	def _valoviy_nadoy_result(self):
		self.valoviy_nadoy = self.vipoyka + self.utilizaciya + self.sale_natura + self.ostatok_today - self.ostatok_lastday

	@api.one
	@api.depends('cow_doy','cow_zapusk','cow_netel','date_doc', 'vipoyka', 'utilizaciya', 'ostatok_today', 'ostatok_lastday')
	def _nadoy_result(self):
		
		self.cow_fur = self.cow_doy + self.cow_zapusk
		
		if self.cow_doy>0:
			self.nadoy_doy = round(self.valoviy_nadoy, 1)/round(self.cow_doy, 1)
			
		if self.cow_fur>0:
			self.nadoy_fur = round(self.valoviy_nadoy, 1)/round(self.cow_fur, 1)

	@api.one
	@api.depends('cow_doy','cow_fur')
	def _otk_result(self):
		d = datetime.strptime(self.date_doc, "%Y-%m-%d")
		prev_date = d - timedelta(days=1)
		
		cm = self.env['milk.trace_milk'].search([('date_doc', '=', prev_date)], limit=1)
		if len(cm)>0:
			self.otk_nadoy_doy = self.nadoy_doy - cm[0].nadoy_doy
			self.otk_nadoy_fur = self.nadoy_fur - cm[0].nadoy_fur
			self.otk_valoviy_nadoy = self.valoviy_nadoy - cm[0].valoviy_nadoy


	@api.one
	@api.depends('nadoy_0_40','nadoy_40_150','nadoy_150_300','nadoy_300')
	def _otk_nadoy_result(self):
		d = datetime.strptime(self.date_doc, "%Y-%m-%d")
		prev_date = d - timedelta(days=1)
		
		cm = self.env['milk.trace_milk'].search([('date_doc', '=', prev_date)], limit=1)
		if len(cm)>0:
			self.otk_0_40 = self.nadoy_0_40 - cm[0].nadoy_0_40
			self.otk_40_150 = self.nadoy_40_150 - cm[0].nadoy_40_150
			self.otk_150_300 = self.nadoy_150_300 - cm[0].nadoy_150_300
			self.otk_300 = self.nadoy_300 - cm[0].nadoy_300
		
	@api.one
	def action_load_uniform(self):
		self.nadoy_0_40 = 30

	@api.one
	@api.depends('trace_milk_ostatok_line.tanker_id','trace_milk_ostatok_line.meter_value', 'trace_milk_ostatok_line.plotnost')
	def _raschet_ostatok(self):
		self.ostatok_today = 0
		for line in self.trace_milk_ostatok_line:
			self.ostatok_today += line.ves_natura
		#self.action_update()

	@api.one
	@api.depends('trace_milk_vipoyka_line.kol')
	def _raschet_vipoyka(self):
		self.vipoyka = 0
		for line in self.trace_milk_vipoyka_line:
			self.vipoyka += line.kol
		#self.action_update()
		#self.env['purchase.order'].method_b()


	@api.multi
	def unlink(self):
		for pp in self:
			if pp.state != 'done':
				raise exceptions.ValidationError(_(u"Документ №%s Проведен и не может быть удален!" % (pp.name)))

		return super(trace_milk, self).unlink()


	@api.multi
	def action_draft(self):
		for doc in self:
							
			if self.env['reg.rashod_kormov'].move(self, [], 'unlink')==True:
				self.state = 'draft'
			else:
				raise exceptions.ValidationError(_(u"Ошибка. Не может быть отменено проведение!"))


	@api.multi
	def action_confirm(self):
		conf = self.env['ir.config_parameter']
		nomen_nomen_id = conf.get_param('milk_nomen_default')
		if nomen_nomen_id:
			nomen_name = self.env['nomen.nomen'].search([('id', '=', nomen_nomen_id)], 
															limit=1).name

			for doc in self:
				doc.date = doc.date_doc
				doc.action_update()
				vals = []
				for line in doc.trace_milk_vipoyka_line:
					vals.append({
								'name': nomen_name, 
								'nomen_nomen_id': nomen_nomen_id, 
								'stado_zagon_id': line.stado_zagon_id.id, 
								'stado_fiz_group_id': line.stado_zagon_id.stado_fiz_group_id.id, 
								'kol': line.kol, 
								})

					
				if len(vals)>0:	
					if self.env['reg.rashod_kormov'].move(doc, vals, 'create')==True:
						doc.state = 'confirmed'
					else:
						raise exceptions.ValidationError(_(u"Ошибка. Не проведен. Невозможно создать движение расхода кормов и добавок!"))
				else:
					doc.state = 'confirmed'

		else:
			raise exceptions.ValidationError(_(u"Ошибка. Не назначена номенклатура молока!"))
			self.state = 'draft'






	@api.multi
	def action_done(self):
		self.state = 'done'


class trace_milk_ostatok_line(models.Model):
	_name = 'milk.trace_milk_ostatok_line'		
	"""Учет движения молока остатки в танкерах"""
	@api.one
	@api.depends('tanker_id')
	def _is_meter(self):
		if self.tanker_id:
			self.name = self.tanker_id.name
			self.merilo = self.tanker_id.merilo
		else:
			self.merilo = ''

	@api.one
	@api.depends('tanker_id','meter_value', 'plotnost')
	def _raschet(self):
		if self.meter_value:
			if self.tanker_id.merilo == u'Весы':
				self.ves_natura = self.meter_value
			elif self.tanker_id.merilo == u'Счетчик':
				self.ves_natura = round(self.meter_value * (1+self.plotnost/1000))
			else:
				pok = self.env['milk.scale_tanker_line'].search([('value', '<=', self.meter_value),
														('scale_tanker_id', '=', self.tanker_id.scale_tanker_id.id)], 
														limit=1, order ='value desc').result

				self.ves_natura = round(pok * (1+self.plotnost/1000))


			
	

	name = fields.Text(string='Description', required=True, default='New', compute='_is_meter', store=True)
	tanker_id = fields.Many2one('milk.tanker', string=u"Танкер", required=True)
	merilo = fields.Char(string=u"Meter", compute='_is_meter', readonly=True, default='')
	meter_value = fields.Integer(string=u"Показания", required=True)
	ves_natura = fields.Integer(string=u"В натуре",  store=True, compute='_raschet')
	plotnost = fields.Float(digits=(4, 2))
	trace_milk_id = fields.Many2one('milk.trace_milk',
		ondelete='cascade', string=u"Учет движения молока", required=True)
	

	
class trace_milk_vipoyka_line(models.Model):
	_name = 'milk.trace_milk_vipoyka_line'		
	"""Учет движения молока на выпойку по загонам"""
	@api.one
	@api.depends('stado_zagon_id')
	def return_name(self):
		if self.stado_zagon_id:
			self.name = self.stado_zagon_id.name
			self.stado_fiz_group_id = self.stado_zagon_id.stado_fiz_group_id
			
		
	
	#, related='stado_zagon_id.stado_fiz_group_id'
	name = fields.Char(string='Наименование', default='New', compute='return_name', store=True)
	stado_zagon_id = fields.Many2one('stado.zagon', string=u'Загон', required=True)
	stado_fiz_group_id = fields.Many2one('stado.fiz_group', string=u'Физиологическая группа', related='stado_zagon_id.stado_fiz_group_id', readonly=True,  store=True)
	
	kol = fields.Integer(string=u"Кол-во, кг",  store=True, default=0)
	
	trace_milk_id = fields.Many2one('milk.trace_milk',
		ondelete='cascade', string=u"Учет движения молока", required=True)	


	


class plan_sale_milk(models.Model):
	_name = 'milk.plan_sale_milk'
	"""План производства/реализации молока"""
	_order = 'date_doc desc, id desc'
	
	@api.one
	@api.depends('month', 'year')
	def return_name(self):
		if self.month and self.year:
			self.name = self.year + '-' + self.month
			self.date_start = datetime.strptime(self.year+'-'+self.month+'-01', "%Y-%m-%d").date()
			last_day = last_day_of_month(self.date_start)
			self.date_end = last_day
			self.count_day = last_day.day

	name = fields.Char(string='Номер', required=True, default='New', compute='return_name', store=True)
	# date_doc = fields.Datetime(string='Дата документа', required=True,  
	# 					index=True, copy=False, default=fields.Datetime.now)
	
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
	], default=str(datetime.today().month).rjust(2, '0'), required=True)
	
	year = fields.Char(string=u"Год", required=True, default=str(datetime.today().year))

	date_start = fields.Date(string='Дата начала', required=True, index=True, copy=False, compute='return_name')
	date_end = fields.Date(string='Дата окончания', required=True, index=True, copy=False, compute='return_name')
	count_day = fields.Integer(string='Кол-во дней в месяце', store=True, copy=False, compute='return_name')
	
	date_doc = fields.Date(string='Дата документа', required=True,  
						index=True, copy=False, default=fields.Datetime.now)

	@api.one
	@api.depends('valoviy_nadoy', 'vipoyka', 'utilizaciya','jir', 'belok', 'price')
	def _raschet(self):
		self.natura = self.valoviy_nadoy - self.vipoyka - self.utilizaciya
		self.zachet = round(self.natura * (self.jir*0.5/3.4 + self.belok*0.5/3), 3)
		self.amount_nds = self.zachet * self.price
		self.amount = self.amount_nds / 1.1


	valoviy_nadoy = fields.Float(digits=(10, 3), string=u"Валовый надой, тн.", store=True)

	vipoyka = fields.Float(digits=(10, 3), string=u"На выпойку, тн.", store=True)
	utilizaciya = fields.Float(digits=(10, 3), string=u"Утилизированно, тн.", store=True)
	natura = fields.Float(digits=(10, 3), string=u"Реализованно, тн.", store=True, compute='_raschet')
	zachet = fields.Float(digits=(10, 3), string=u"Зачетный вес, тн.", store=True, compute='_raschet')
	jir = fields.Float(digits=(3, 1), string=u"Жир, %", store=True, group_operator="avg")
	belok = fields.Float(digits=(3, 2), string=u"Белок, %", store=True, group_operator="avg")
	
	
	price = fields.Float(digits=(3, 2), string=u"Цена с НДС(10%), руб/кг", store=True)

	amount = fields.Float(digits=(10, 2), string=u"Выручка (без НДС), тыс.руб.", store=True, compute='_raschet')
	amount_nds = fields.Float(digits=(10, 2), string=u"Выручка (с учетом НДС), тыс.руб.", store=True, compute='_raschet')
	
	plan_sale_milk_line = fields.One2many('milk.plan_sale_milk_line', 'plan_sale_milk_id', string=u"Строка Плана производства/реализации молока")

	@api.one
	def action_generate(self):
		line = self.env['milk.plan_sale_milk_line']
		del_line = line.search([('plan_sale_milk_id',	'=',	self.id)])
		del_line.unlink()

		date_start = ''

		last_day = last_day_of_month(self.date_start)
		begin_day = last_day.replace(day=1)
		date_end = begin_day
		kol_day_month = last_day.day
		while date_end<last_day:
			
			if date_start == '' :
				date_start = begin_day
			else:
				date_start = date_end + timedelta(days=1)
			
			date_end = week_magic(date_start)[1]
			if date_end>last_day:
				date_end = last_day

			kol_day_week = date_end.day - date_start.day + 1

			#print "kkkkkkkkk===", kol_day_week
			if kol_day_month > 0:

				new_line = 	line.create({'plan_sale_milk_id':	self.id,
										'name':	self.year+'-'+self.month+'-1',
										'year':	self.year,
										'month':	self.month,
										'week':	week_magic(date_start)[2],
										'date_start':	date_start,
										'date_end':	date_end,
										'valoviy_nadoy': round(self.valoviy_nadoy/kol_day_month*kol_day_week, 3),
										'vipoyka':	self.vipoyka/kol_day_month*kol_day_week,
										'utilizaciya':	self.utilizaciya/kol_day_month*kol_day_week,
										# 'natura':	self.natura/kol_day_month*kol_day_week,
										# 'zachet':	self.zachet/kol_day_month*kol_day_week,
										'jir':	self.jir,
										'belok':	self.belok,
										# 'amount':	self.amount/kol_day_month*kol_day_week,
										# 'amount_nds':	self.amount_nds/kol_day_month*kol_day_week,
										
										})




class plan_sale_milk_line(models.Model):
	_name = 'milk.plan_sale_milk_line'
	"""Строка Плана производства/реализации молока"""

	def return_name(self):
		self.name = self.year+'-'+self.month+'-'+self.week
	name = fields.Char(string='Номер', required=True, default='New', compute='return_name', store=True)
	# date_doc = fields.Datetime(string='Дата документа', required=True,  
	# 					index=True, copy=False, default=fields.Datetime.now)
	
	plan_sale_milk_id = fields.Many2one('milk.plan_sale_milk',
		ondelete='cascade', string=u"План производства/реализации молока", required=True)

	year = fields.Char(string=u"Год", required=True, store=True)

	month = fields.Char(string=u"Месяц", required=True, store=True)
	
	week = fields.Char(string=u"Неделя", required=True, store=True)

	
	

	date_start = fields.Date(string='Дата начала', required=True, index=True, copy=False)
	date_end = fields.Date(string='Дата окончания', required=True, index=True, copy=False)


	@api.one
	@api.depends('valoviy_nadoy', 'vipoyka', 'utilizaciya','jir', 'belok')
	def _raschet(self):
		self.natura = self.valoviy_nadoy - self.vipoyka - self.utilizaciya
		self.zachet = round(self.natura * (self.jir*0.5/3.4 + self.belok*0.5/3), 3)
		self.amount_nds = round(self.zachet * self.plan_sale_milk_id.price, 2)
		self.amount = round(self.amount_nds / 1.1, 2)

	valoviy_nadoy = fields.Float(digits=(10, 3), string=u"Валовый надой, тн.", store=True)

	vipoyka = fields.Float(digits=(10, 3), string=u"На выпойку, тн.", store=True)
	utilizaciya = fields.Float(digits=(10, 3), string=u"Утил-но, тн.", store=True)
	natura = fields.Float(digits=(10, 3), string=u"Реал-но, тн.", store=True, compute='_raschet')
	zachet = fields.Float(digits=(10, 3), string=u"Зачетный вес, тн.", store=True, compute='_raschet')
	jir = fields.Float(digits=(3, 1), string=u"Жир, %", store=True, group_operator="avg")
	belok = fields.Float(digits=(3, 2), string=u"Белок, %", store=True, group_operator="avg")
		
	amount = fields.Float(digits=(10, 2), string=u"Выручка (без НДС), тыс.руб.", store=True, compute='_raschet')
	amount_nds = fields.Float(digits=(10, 2), string=u"Выручка (с учетом НДС), тыс.руб.", store=True, compute='_raschet')




class milk_price(models.Model):
	_name = 'milk.price'
	_description = u'Установка цен на молоко'
	_order = 'date desc'

	@api.one
	@api.depends('date')
	def return_name(self):
		self.name = self.date



	name = fields.Char(string=u"Номер", store=True, copy=False, index=True, default=fields.Datetime.now)
	date = fields.Date(string='Дата', required=True, default=fields.Datetime.now)
	metod = fields.Selection([
		(u'Цана на базисный белок/жир', "Цана на базисный белок/жир"),
		(u'Расчетная с 2017г.', "Расчетная с 2017г."),

	], default=u'Расчетная с 2017г.', required=True, string=u'Метод расчета')

	price = fields.Float(digits=(10, 2), string=u"Базовая цена (без НДС)", required=True)
	nds = fields.Float(digits=(10, 2), string=u"НДС, %", required=True, oldname='NDS')
	bb = fields.Float(digits=(10, 2), string=u"Базовый белок, %", required=True, oldname='BB')
	bj = fields.Float(digits=(10, 2), string=u"Базовый жир, %", required=True, oldname='BJ')
	ko = fields.Float(digits=(10, 2), string=u"Коэффициент объема", default=0, oldname='KO')
	kss = fields.Float(digits=(10, 2), string=u"Коэффициент Собственное стадо", default=0, oldname='KSS')
	pb = fields.Float(digits=(10, 3), string=u"Поправка на белок", default=0, oldname='PB')
	pj = fields.Float(digits=(10, 3), string=u"Поправка на жир", default=0, oldname='PJ')
	kk = fields.Float(digits=(10, 2), string=u"Коэффициент качеста", default=0, oldname='KK')
	h = fields.Float(digits=(10, 2), string=u"Надбавка за термо-е и сыроприг. молоко", default=0, oldname='H')


def connect_server(self, url_name):

	"""Функция отправляет запрос на Сервер API и возвращает результат или ошибку
		url_name - имя функции сервера api. напр. /api/load_milk/
	"""
	import requests as r
	import json

	err=u''
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


class milk_nadoy_group(models.Model):
	_name = 'milk.nadoy_group'
	_description = u'Надой молока по группам'
	_order = 'date desc'

	@api.one
	@api.depends('date')
	def return_name(self):
		self.name = self.date

	@api.one
	@api.depends('milk_nadoy_group_line.kol_golov')
	def return_kol_golov(self):
		self.kol_golov = self.nadoy_itog = 0
		kol = 0
		for line in self.milk_nadoy_group_line:
			self.kol_golov += line.kol_golov
			kol += line.kol_golov * line.kol
			self.nadoy_itog += line.kol_golov * line.kol
		if self.kol_golov>0:
			self.nadoy_golova = kol / self.kol_golov

	@api.one
	def action_load(self):

		conf = self.env['ir.config_parameter']
		hm_programms = conf.get_param('hm_programms')

		if hm_programms == 'DC305':
			self.load_dc305()

		if hm_programms == 'UNIFORM':
			self.load_uniform()




	def load_uniform(self):
		
		err=''
			
		dt = datetime.strptime(self.date,'%Y-%m-%d')
		
		date = dt.date().strftime('%d.%m.%Y')
		url_name = '/api/milk_nadoy_group/'+date
		
		
		res = connect_server(self, url_name)
		self.massage = ''
		if len(res['err'])==0:
			stado_zagon = self.env['stado.zagon']
			data = res['data']

			if self.kol_golov>data['kol_golov']:
				self.massage = u'Обновление данных не требуется'

			else:
				
				self.milk_nadoy_group_line.unlink()

				for line in data['zagons']:
					#print line['kol']
				
					zagon_id = stado_zagon.search([
													('uniform_id',   '=',    line['GROEPNR']),
													('date_start', '<=', self.date),'|',
													('date_end', '>=', self.date),
													('date_end', '=', False)

													], 
													limit=1)
					if len(zagon_id)>0:
						#print line['kol_golov'], line['kol'],line['sko']
						self.milk_nadoy_group_line.create({
									'milk_nadoy_group_id':   self.id,
									'name':   zagon_id.name,
									'stado_zagon_id':   zagon_id.id,
									#'stado_fiz_group_id':   zagon_id.stado_fiz_group_id.id,
									'kol_golov':  line['kol_golov'],
									'kol':  line['kol'],
									'sko':  line['sko'],
									'procent_0_15': line['procent_0_15'],		
									'procent_15_20': line['procent_15_20'],		
									'procent_20_25': line['procent_20_25'],		
									'procent_25_30': line['procent_25_30'],		
									'procent_30_35': line['procent_30_35'],		
									'procent_35_40': line['procent_35_40'],		
									'procent_40_45': line['procent_40_45'],	
									'procent_45': line['procent_45']	

									
									})
					else:
						self.description += u'Не найден загон с номером: %s \n' %  (line['GROEPNR'])

				#data = res['data'][1]
				procent = data['procent']		
				self.procent_0_15 = procent['procent_0_15']		
				self.procent_15_20 = procent['procent_15_20']		
				self.procent_20_25 = procent['procent_20_25']		
				self.procent_25_30 = procent['procent_25_30']		
				self.procent_30_35 = procent['procent_30_35']		
				self.procent_35_40 = procent['procent_35_40']		
				self.procent_40_45 = procent['procent_40_45']		
				self.procent_45 = procent['procent_45']	


				procent = data['nadoy']		
				self.nadoy_l1 = procent['nadoy_l1']		
				self.nadoy_l2 = procent['nadoy_l2']		
				self.nadoy_l3 = procent['nadoy_l3']		
				self.nadoy_0_40 = procent['nadoy_0_40']		
				self.nadoy_40_150 = procent['nadoy_40_150']		
				self.nadoy_150_300 = procent['nadoy_150_300']		
				self.nadoy_300 = procent['nadoy_300']		
				self.nadoy_l1_0_40 = procent['nadoy_l1_0_40']		
				self.nadoy_l1_40_150 = procent['nadoy_l1_40_150']		
				self.nadoy_l1_150_300 = procent['nadoy_l1_150_300']		
				self.nadoy_l1_300 = procent['nadoy_l1_300']		
				self.nadoy_l2_0_40 = procent['nadoy_l2_0_40']		
				self.nadoy_l2_40_150 = procent['nadoy_l2_40_150']		
				self.nadoy_l2_150_300 = procent['nadoy_l2_150_300']		
				self.nadoy_l2_300 = procent['nadoy_l2_300']		
				self.nadoy_l3_0_40 = procent['nadoy_l3_0_40']		
				self.nadoy_l3_40_150 = procent['nadoy_l3_40_150']		
				self.nadoy_l3_150_300 = procent['nadoy_l3_150_300']		
				self.nadoy_l3_300 = procent['nadoy_l3_300']		
					
					
					# for z in self.stado_struktura_line:
					# 	if z.stado_zagon_id.uniform_id == line['GROEPNR']:
					# 		z.sred_kol_milk = line['sred_kol_milk']

						
					
		if len(res['err'])>0:
			
			self.description += u'Не возможно загрузить данные по причине: \n' + res['err']
			self.massage = u'Ошибка загрузки'
			# return exceptions.UserError(_(u"При загрузки произошли ошибки: %s" % (err,)))
		else:
			self.description += u'Синхронизация прошла успешна. \n' 
			if not self.massage == u'Обновление данных не требуется':
				self.massage = u'Данные загружены'

			tm = self.env['milk.trace_milk'].search([('date_doc', '=', self.date),], limit=1)
			if len(tm)>0:
				cow_doy = tm.cow_doy
				otk = (cow_doy - self.kol_golov)/cow_doy
				if otk>0 and otk<0.10:
					self.dostovernost = True
				else:
					self.dostovernost = False


					
	def load_dc305(self):
		
		err = ''
		import pandas as pd
		import numpy as np
		import base64
		data_file_p = open('/tmp/milk_load.csv','w')

		data_file_p.write((base64.b64decode(self.file_milk)))

		data_file_p.close()
		
		try:

			frame = pd.read_csv('/tmp/milk_load.csv', 
			                sep=';', 
			                header=0, 
			                usecols=[u"ИД", u"ГРУПА", u"ДОМИК", u"ДДНИ", u"ЛАКТ", u"МОЛ1"], 
			                encoding='cp1251')
		except:
			err += u"Ошибка чтения файла."
		frame = frame.drop(frame.index[len(frame)-1])

		self.kol_golov = frame[u"ИД"].count()

		frame[u"kol_milk"] = frame[u"МОЛ1"].astype(int)
		frame = frame[frame[u'kol_milk']!=0] #Удаляем записи где надой молока =0
		frame[u"GROEPNR"] = frame[u"ГРУПА"].astype(int)
		frame[u"ДДНИ"] = frame[u"ДДНИ"].astype(int)
		frame[u"ЛАКТ"] = frame[u"ЛАКТ"].astype(int)
		frame[u"nomer_lakt"] = np.where(frame[u'ЛАКТ']>2, 3, frame[u'ЛАКТ'])

		#frame[u"МОЛ2"] = frame[u"МОЛ1"]/2
		frame['n015'] = np.where((frame[u'kol_milk']>0) & (frame[u'kol_milk']<15), 1, 0)
		frame['n1520'] = np.where((frame[u'kol_milk']>=15) & (frame[u'kol_milk']<20), 1, 0)
		frame['n2025'] = np.where((frame[u'kol_milk']>=20) & (frame[u'kol_milk']<25), 1, 0)
		frame['n2530'] = np.where((frame[u'kol_milk']>=25) & (frame[u'kol_milk']<30), 1, 0)
		frame['n3035'] = np.where((frame[u'kol_milk']>=30) & (frame[u'kol_milk']<35), 1, 0)
		frame['n3540'] = np.where((frame[u'kol_milk']>=35) & (frame[u'kol_milk']<40), 1, 0)
		frame['n4045'] = np.where((frame[u'kol_milk']>=40) & (frame[u'kol_milk']<45), 1, 0)
		frame['n45'] = np.where(frame[u'kol_milk']>=45, 1, 0)


		table = pd.pivot_table(
                    frame, 
                    values=[
                        'kol_milk', 
                        'n015',
                        'n1520',
                        'n2025',
                        'n2530',
                        'n3035',
                        'n3540',
                        'n4045',
                        'n45',
                    ], 
                    index=['GROEPNR'], 
                    aggfunc={
                        'kol_milk':[np.mean, np.std, len],
                        'n015':[np.sum],
                        'n1520':[np.sum],
                        'n2025':[np.sum],
                        'n2530':[np.sum],
                        'n3035':[np.sum],
                        'n3540':[np.sum],
                        'n4045':[np.sum],
                        'n45':[np.sum]
                        
                        
                    }, 
                    fill_value=0
    
        )


		stado_zagon = self.env['stado.zagon']
		#data = res['data']
		self.milk_nadoy_group_line.unlink()
		
		#print table[:10]
		for line in table.index:
			#print line, table.ix[line, u'МОЛ1']

			zagon_id = stado_zagon.search([
											('dc305_id',   '=',    line),
											('date_start', '<=', self.date),'|',
											('date_end', '>=', self.date),
											('date_end', '=', False)

											], 
											limit=1)
			if len(zagon_id)>0:
				#print line['kol_golov'], line['kol'],line['sko']
				self.milk_nadoy_group_line.create({
							'milk_nadoy_group_id':   self.id,
							'name':   zagon_id.name,
							'stado_zagon_id':   zagon_id.id,
							#'stado_fiz_group_id':   zagon_id.stado_fiz_group_id.id,
							'kol_golov':  table.ix[line,('kol_milk', 'len')],
							'kol':  table.ix[line,('kol_milk', 'mean')],
							'sko':  table.ix[line,('kol_milk', 'std')],
							'procent_0_15': table.ix[line, ('n015', 'sum')]/table.ix[line,('kol_milk', 'len')]*100.0,		
							'procent_15_20': table.ix[line, ('n1520', 'sum')]/table.ix[line,('kol_milk', 'len')]*100.0,	
							'procent_20_25': table.ix[line, ('n2025', 'sum')]/table.ix[line,('kol_milk', 'len')]*100.0,	
							'procent_25_30': table.ix[line, ('n2530', 'sum')]/table.ix[line,('kol_milk', 'len')]*100.0,	
							'procent_30_35': table.ix[line, ('n3035', 'sum')]/table.ix[line,('kol_milk', 'len')]*100.0,		
							'procent_35_40': table.ix[line, ('n3540', 'sum')]/table.ix[line,('kol_milk', 'len')]*100.0,		
							'procent_40_45': table.ix[line, ('n4045', 'sum')]/table.ix[line,('kol_milk', 'len')]*100.0,	
							'procent_45': table.ix[line, ('n45', 'sum')]/table.ix[line,('kol_milk', 'len')]*100	

							
							})
			else:
				self.description += u'Не найден загон с номером: %s \n' %  (line)
			
		frame_lakt = frame[frame.nomer_lakt==1]
		self.nadoy_l1 = frame_lakt[u"kol_milk"].mean()		
		frame_lakt = frame[frame.nomer_lakt==2]
		self.nadoy_l2 = frame_lakt[u"kol_milk"].mean()	
		frame_lakt = frame[frame.nomer_lakt==3]
		self.nadoy_l3 = frame_lakt[u"kol_milk"].mean()	


		if self.kol_golov>0:
			kol_golov = frame[u"ИД"].count()
			self.procent_0_15 = frame['n015'].sum()*100/kol_golov		
			self.procent_15_20 = frame['n1520'].sum()*100/kol_golov
			self.procent_20_25 = frame['n2025'].sum()*100/kol_golov
			self.procent_25_30 = frame['n2530'].sum()*100/kol_golov
			self.procent_30_35 = frame['n3035'].sum()*100/kol_golov
			self.procent_35_40 = frame['n3540'].sum()*100/kol_golov
			self.procent_40_45 = frame['n4045'].sum()*100/kol_golov
			self.procent_45 = frame['n45'].sum()*100/kol_golov

		self.nadoy_0_21 = frame[frame[u'ДДНИ']<22].kol_milk.mean()		
		self.nadoy_22_100 = frame[(frame[u'ДДНИ']>=22) & (frame[u'ДДНИ']<=100)].kol_milk.mean()		
		self.nadoy_101_300 = frame[(frame[u'ДДНИ']>=101) & (frame[u'ДДНИ']<=300)].kol_milk.mean()	
		self.nadoy_300 = frame[frame[u'ДДНИ']>300].kol_milk.mean()

		self.nadoy_l1_0_21 = frame[(frame[u'ДДНИ']<22) & (frame[u'nomer_lakt']==1)].kol_milk.mean()
		self.nadoy_l1_22_100 = frame[(frame[u'ДДНИ']>=22) & (frame[u'ДДНИ']<=100) & (frame[u'nomer_lakt']==1)].kol_milk.mean()
		self.nadoy_l1_101_300 = frame[(frame[u'ДДНИ']>=101) & (frame[u'ДДНИ']<=300) & (frame[u'nomer_lakt']==1)].kol_milk.mean()
		self.nadoy_l1_300 = frame[(frame[u'ДДНИ']>300) & (frame[u'nomer_lakt']==1)].kol_milk.mean()
		self.nadoy_l2_0_21 = frame[(frame[u'ДДНИ']<22) & (frame[u'nomer_lakt']==2)].kol_milk.mean()
		self.nadoy_l2_22_100 = frame[(frame[u'ДДНИ']>=22) & (frame[u'ДДНИ']<=100) & (frame[u'nomer_lakt']==2)].kol_milk.mean()
		self.nadoy_l2_101_300 = frame[(frame[u'ДДНИ']>=101) & (frame[u'ДДНИ']<=300) & (frame[u'nomer_lakt']==2)].kol_milk.mean()
		self.nadoy_l2_300 = frame[(frame[u'ДДНИ']>300) & (frame[u'nomer_lakt']==2)].kol_milk.mean()
		self.nadoy_l3_0_21 = frame[(frame[u'ДДНИ']<22) & (frame[u'nomer_lakt']==3)].kol_milk.mean()
		self.nadoy_l3_22_100 = frame[(frame[u'ДДНИ']>=22) & (frame[u'ДДНИ']<=100) & (frame[u'nomer_lakt']==3)].kol_milk.mean()
		self.nadoy_l3_101_300 = frame[(frame[u'ДДНИ']>=101) & (frame[u'ДДНИ']<=300) & (frame[u'nomer_lakt']==3)].kol_milk.mean()
		self.nadoy_l3_300 = frame[(frame[u'ДДНИ']>300) & (frame[u'nomer_lakt']==3)].kol_milk.mean()


		if len(err)>0:
			
			self.description += u'Не возможно загрузить данные по причине: \n' + err
			self.massage = u'Ошибка загрузки'
			# return exceptions.UserError(_(u"При загрузки произошли ошибки: %s" % (err,)))
		else:
			self.description += u'Синхронизация прошла успешна. \n' 
			if not self.massage == u'Обновление данных не требуется':
				self.massage = u'Данные загружены'

			tm = self.env['milk.trace_milk'].search([('date_doc', '=', self.date),], limit=1)
			if len(tm)>0:
				cow_doy = tm.cow_doy
				otk = (cow_doy - self.kol_golov)/cow_doy
				if otk>0 and otk<0.10:
					self.dostovernost = True
				else:
					self.dostovernost = False



	
	@api.one
	def action_raschet(self):
		
		"""Распределяет считанное молоко по молокосчетчикам на фактический надой"""
		
		line = self.env['milk.nadoy_group_fakt_line']
		del_line = line.search([('milk_nadoy_group_id',	'=',	self.id)])
		del_line.unlink()
		zapros = """SELECT
						sz.id,
						sz.name,
						case
							when sz.doynie = True and (sz.mastit = False or sz.mastit is Null) then 'Карусель'
							when sz.doynie = True and sz.mastit = True then 'Парабона'
						end as zal_doeniya,
						ssl.kol_golov_zagon
					FROM stado_zagon sz
					left join stado_struktura_line ssl on (ssl.stado_zagon_id = sz.id)
					WHERE sz.date_start<='%(date)s' and 
							(sz.date_end>='%(date)s' or sz.date_end is Null) and
							ssl.date::date = '%(date)s' and
							sz.doynie = True 

				""" % {'date': self.date}
		#print zapros
		self._cr.execute(zapros,)
		zagons = self._cr.fetchall()
		
		self.kol_golov_karusel = self.kol_golov_parabone = 0

		for zagon in zagons:
			zal_doeniya = zagon[2]
			kol_golov_zagon = zagon[3]
			self.milk_nadoy_group_fakt_line.create({
									'milk_nadoy_group_id':   self.id,
									
									'stado_zagon_id':   zagon[0],
									'name':   zal_doeniya,
									'kol_golov_zagon':   kol_golov_zagon,
									
									})

			if zal_doeniya == u'Карусель':
				self.kol_golov_karusel += kol_golov_zagon
			else:
				self.kol_golov_parabone += kol_golov_zagon

		#Подставляем значения считанного молока, если нет загруженного молока то загружаем из предыдущего дня
		for line in self.milk_nadoy_group_fakt_line:
			zapros = """select
								mnl.kol_golov,
								mnl.kol
						from milk_nadoy_group_line mnl, milk_nadoy_group mn 
						where mn.id=mnl.milk_nadoy_group_id and 
							  mnl.stado_zagon_id=%(id)s and
							  mn.date<='%(date)s'
						Order by mn.date desc
						LIMIT 1 

				""" % {'date': self.date, 'id': line.stado_zagon_id.id}
			
			self._cr.execute(zapros,)
			schitanno = self._cr.fetchone()
			if len(schitanno)>0:
				line.kol_golov = schitanno[0]
				line.nadoy_golova = schitanno[1]

		
		self.nadoy_parabone=self.nadoy_karusel=self.valoviy_nadoy=0
		
		tm = self.env['milk.trace_milk'].search([('date_doc', '=', self.date),], limit=1)
		if len(tm)>0:
			self.valoviy_nadoy = tm.valoviy_nadoy
			self.nadoy_parabone = tm.parabone
			self.nadoy_karusel = self.valoviy_nadoy - self.nadoy_parabone
			

			nadoy_karusel_zagon_itog = 0

			for line in self.milk_nadoy_group_fakt_line:
				if line.name == u'Карусель':
					if line.kol_golov>0 and line.kol_golov_zagon>0:
							line.procent_neschitannih_golov = 100 - line.kol_golov*100/line.kol_golov_zagon

					line.nadoy_zagon = line.kol_golov_zagon * line.nadoy_golova

					nadoy_karusel_zagon_itog += line.nadoy_zagon
				

			karusel_nadoy_zagon_fakt_itog = parabone_nadoy_zagon_fakt_itog = 0
			if nadoy_karusel_zagon_itog>0:
				
				for line in self.milk_nadoy_group_fakt_line:
					
					if line.name == u'Карусель' and line.kol_golov_zagon>0:
						line.nadoy_zagon_fakt = line.nadoy_zagon/nadoy_karusel_zagon_itog * self.nadoy_karusel
						line.nadoy_golova_fakt = line.nadoy_zagon_fakt/line.kol_golov_zagon
						karusel_nadoy_zagon_fakt_itog += line.nadoy_zagon_fakt
					else:
						line.nadoy_zagon_fakt = line.kol_golov_zagon / self.kol_golov_parabone * self.nadoy_parabone
						line.nadoy_golova_fakt = line.nadoy_zagon_fakt/line.kol_golov_zagon
						parabone_nadoy_zagon_fakt_itog += line.nadoy_zagon_fakt

					line.procent_nadoy = line.nadoy_zagon_fakt/self.valoviy_nadoy*100

			#Если есть отклонение, то распределяем погрешность на загоны
			#Ограничить кол-во циклов n=10
			otk_karusel = self.nadoy_karusel - karusel_nadoy_zagon_fakt_itog
			if otk_karusel != 0:
				n = 0
				while otk_karusel!=0 and n<10:
					n += 1
					k = 1 if otk_karusel>0 else -1
					
					for line in self.milk_nadoy_group_fakt_line:
					
						if line.name == u'Карусель' and line.nadoy_zagon_fakt>0:
							line.nadoy_zagon_fakt += k
							otk_karusel -= k
						if otk_karusel == 0:
							break

			otk_parabone = self.nadoy_parabone - parabone_nadoy_zagon_fakt_itog
			if otk_parabone != 0:
				n = 0
				while otk_parabone!=0 and n<10:
					n += 1
					
					k = 1 if otk_parabone>0 else -1
					
					for line in self.milk_nadoy_group_fakt_line:
					
						if line.name == u'Парабона' and line.nadoy_zagon_fakt>0:
							line.nadoy_zagon_fakt += k
							otk_parabone -= k
						if otk_parabone == 0:
							break

	


	name = fields.Char(string=u"Номер", store=False, copy=False, index=True, compute='return_name')
	date = fields.Date(string='Дата', required=True, default=fields.Datetime.now)
	
	file_milk = fields.Binary('Импортировать файл')

	kol_golov = fields.Integer(string=u"Считано голов", compute='return_kol_golov', store=True, group_operator="avg", default=0)
	nadoy_golova = fields.Float(digits=(3, 2), string=u"Надой на голову, л", compute='return_kol_golov', store=True, group_operator="avg")
	nadoy_itog = fields.Integer(string=u"Надой всего, л", compute='return_kol_golov', store=True, group_operator="sum", default=0)
	
	kol_golov_parabone = fields.Integer(string=u"Голов парабона", store=True, group_operator="avg", default=0)
	kol_golov_karusel = fields.Integer(string=u"Голов карусель", store=True, group_operator="avg", default=0)
	valoviy_nadoy = fields.Integer(string=u"Валовый надой, кг", store=True, group_operator="sum", default=0)
	nadoy_parabone = fields.Integer(string=u"Надой парабона, кг", store=True, group_operator="sum", default=0)
	nadoy_karusel = fields.Integer(string=u"Надой карусель, кг", store=True, group_operator="sum", default=0)


	#dd = fields.Float(digits=(10, 2), string=u"Базовая цена (без НДС)", required=True)

	### 1-й вариант разреза (устаревший)
	nadoy_0_40 = fields.Float(digits=(3, 2), string=u"Надой 0-40", store=True, group_operator="avg")
	nadoy_40_150 = fields.Float(digits=(3, 2), string=u"Надой 40-150", store=True, group_operator="avg")
	nadoy_150_300 = fields.Float(digits=(3, 2), string=u"Надой 150-300", store=True, group_operator="avg")
	#nadoy_300 = fields.Float(digits=(3, 2), string=u"Надой >300", store=True, group_operator="avg")

	nadoy_l1_0_40 = fields.Float(digits=(3, 2), string=u"1-я л. Надой 0-40", store=True, group_operator="avg")
	nadoy_l1_40_150 = fields.Float(digits=(3, 2), string=u"1-я л. Надой 40-150", store=True, group_operator="avg")
	nadoy_l1_150_300 = fields.Float(digits=(3, 2), string=u"1-я л. Надой 150-300", store=True, group_operator="avg")
	#nadoy_l1_300 = fields.Float(digits=(3, 2), string=u"1-я л. Надой >300", store=True, group_operator="avg")

	nadoy_l2_0_40 = fields.Float(digits=(3, 2), string=u"2-я л. Надой 0-40", store=True, group_operator="avg")
	nadoy_l2_40_150 = fields.Float(digits=(3, 2), string=u"2-я л. Надой 40-150", store=True, group_operator="avg")
	nadoy_l2_150_300 = fields.Float(digits=(3, 2), string=u"2-я л. Надой 150-300", store=True, group_operator="avg")
	#nadoy_l2_300 = fields.Float(digits=(3, 2), string=u"2-я л. Надой >300", store=True, group_operator="avg")

	nadoy_l3_0_40 = fields.Float(digits=(3, 2), string=u">=3-я л. Надой 0-40", store=True, group_operator="avg")
	nadoy_l3_40_150 = fields.Float(digits=(3, 2), string=u">=3-я л. Надой 40-150", store=True, group_operator="avg")
	nadoy_l3_150_300 = fields.Float(digits=(3, 2), string=u">=3-я л. Надой 150-300", store=True, group_operator="avg")
	#nadoy_l3_300 = fields.Float(digits=(3, 2), string=u">=3-я л. Надой >300", store=True, group_operator="avg")
	###############

	### 2-й вариант разреза
	nadoy_0_21 = fields.Float(digits=(3, 2), string=u"Надой 0-21", store=True, group_operator="avg")
	nadoy_22_100 = fields.Float(digits=(3, 2), string=u"Надой 22-100", store=True, group_operator="avg")
	nadoy_101_300 = fields.Float(digits=(3, 2), string=u"Надой 101-300", store=True, group_operator="avg")
	nadoy_300 = fields.Float(digits=(3, 2), string=u"Надой >300", store=True, group_operator="avg")


	nadoy_l1_0_21 = fields.Float(digits=(3, 2), string=u"1-я л. Надой 0-21", store=True, group_operator="avg")
	nadoy_l1_22_100 = fields.Float(digits=(3, 2), string=u"1-я л. Надой 22-100", store=True, group_operator="avg")
	nadoy_l1_101_300 = fields.Float(digits=(3, 2), string=u"1-я л. Надой 101-300", store=True, group_operator="avg")
	nadoy_l1_300 = fields.Float(digits=(3, 2), string=u"1-я л. Надой >300", store=True, group_operator="avg")

	nadoy_l2_0_21 = fields.Float(digits=(3, 2), string=u"2-я л. Надой 0-21", store=True, group_operator="avg")
	nadoy_l2_22_100 = fields.Float(digits=(3, 2), string=u"2-я л. Надой 22-100", store=True, group_operator="avg")
	nadoy_l2_101_300 = fields.Float(digits=(3, 2), string=u"2-я л. Надой 101-300", store=True, group_operator="avg")
	nadoy_l2_300 = fields.Float(digits=(3, 2), string=u"2-я л. Надой >300", store=True, group_operator="avg")

	nadoy_l3_0_21 = fields.Float(digits=(3, 2), string=u">=3-я л. Надой 0-21", store=True, group_operator="avg")
	nadoy_l3_22_100 = fields.Float(digits=(3, 2), string=u">=3-я л. Надой 22-100", store=True, group_operator="avg")
	nadoy_l3_101_300 = fields.Float(digits=(3, 2), string=u">=3-я л. Надой 101-300", store=True, group_operator="avg")
	nadoy_l3_300 = fields.Float(digits=(3, 2), string=u">=3-я л. Надой >300", store=True, group_operator="avg")
	##################




	nadoy_l1 = fields.Float(digits=(3, 2), string=u"Надой 1-я л.", store=True, group_operator="avg")
	nadoy_l2 = fields.Float(digits=(3, 2), string=u"Надой 2-я л.", store=True, group_operator="avg")
	nadoy_l3 = fields.Float(digits=(3, 2), string=u"Надой 3-я л. и более", store=True, group_operator="avg")
	
	procent_0_15 = fields.Float(digits=(3, 1), string=u"% голов с надоями 0-15л", store=True, group_operator="avg")
	procent_15_20 = fields.Float(digits=(3, 1), string=u"% голов с надоями 15-20л", store=True, group_operator="avg")
	procent_20_25 = fields.Float(digits=(3, 1), string=u"% голов с надоями 20-25л", store=True, group_operator="avg")
	procent_25_30 = fields.Float(digits=(3, 1), string=u"% голов с надоями 25-30л", store=True, group_operator="avg")
	procent_30_35 = fields.Float(digits=(3, 1), string=u"% голов с надоями 30-35л", store=True, group_operator="avg")
	procent_35_40 = fields.Float(digits=(3, 1), string=u"% голов с надоями 35-40л", store=True, group_operator="avg")
	procent_40_45 = fields.Float(digits=(3, 1), string=u"% голов с надоями 40-45л", store=True, group_operator="avg")
	procent_45 = fields.Float(digits=(3, 1), string=u"% голов с надоями >45л", store=True, group_operator="avg")

	massage = fields.Char(string=u"Результат загрузки", readonly=True)
	dostovernost = fields.Boolean(string=u"Достоверность", readonly=True)
	description = fields.Text(string=u"Коментарии", default=u' ')
	procent_graph = fields.Binary(string = u"График")

	milk_nadoy_group_line = fields.One2many('milk.nadoy_group_line', 'milk_nadoy_group_id', string=u"Строка надоя по группам")
	milk_nadoy_group_fakt_line = fields.One2many('milk.nadoy_group_fakt_line', 'milk_nadoy_group_id', string=u"Строка Фактический надоя по группам")

	

class milk_nadoy_group_line(models.Model):
	_name = 'milk.nadoy_group_line'		
	"""Строка надоя по группам. Надой в разрезе загонов"""
	@api.one
	@api.depends('stado_zagon_id')
	def return_name(self):
		if self.stado_zagon_id:
			self.name = self.stado_zagon_id.name
			self.stado_fiz_group_id = self.stado_zagon_id.stado_fiz_group_id
			
		
	
	#, related='stado_zagon_id.stado_fiz_group_id'
	name = fields.Char(string='Наименование', default='New', compute='return_name', store=True)
	stado_zagon_id = fields.Many2one('stado.zagon', string=u'Загон', required=True)
	stado_fiz_group_id = fields.Many2one('stado.fiz_group', string=u'Физиологическая группа', related='stado_zagon_id.stado_fiz_group_id', readonly=True,  store=True)
	
	kol_golov = fields.Integer(string=u"Считано голов", store=True, group_operator="avg", default=0)
	kol = fields.Float(digits=(3, 2), string=u"Ср. надой на голову, л.", store=True, group_operator="avg", default=0)
	sko = fields.Float(digits=(3, 2), string=u"СКО, л", store=True, group_operator="avg", default=0, help=u"Среднеквадратическое отклонение")
	procent_0_15 = fields.Float(digits=(3, 1), string=u"% гол. 0-15л", store=True, group_operator="avg")
	procent_15_20 = fields.Float(digits=(3, 1), string=u"% гол. 15-20л", store=True, group_operator="avg")
	procent_20_25 = fields.Float(digits=(3, 1), string=u"% гол. 20-25л", store=True, group_operator="avg")
	procent_25_30 = fields.Float(digits=(3, 1), string=u"% гол. 25-30л", store=True, group_operator="avg")
	procent_30_35 = fields.Float(digits=(3, 1), string=u"% гол. 30-35л", store=True, group_operator="avg")
	procent_35_40 = fields.Float(digits=(3, 1), string=u"% гол. 35-40л", store=True, group_operator="avg")
	procent_40_45 = fields.Float(digits=(3, 1), string=u"% гол. 40-45л", store=True, group_operator="avg")
	procent_45 = fields.Float(digits=(3, 1), string=u"% гол. >45л", store=True, group_operator="avg")

	
	
	milk_nadoy_group_id = fields.Many2one('milk.nadoy_group',
		ondelete='cascade', string=u"Надой молока по группам", required=True)	



class milk_nadoy_group_fakt_line(models.Model):
	_name = 'milk.nadoy_group_fakt_line'		
	"""Строка Фактического надоя по группам. Надой в разрезе загонов"""
	
	@api.multi
	@api.depends('milk_nadoy_group_id.date')
	def return_date(self):
		if self.milk_nadoy_group_id.date:
			for line in self:
				line.date = self.milk_nadoy_group_id.date

	@api.multi
	#@api.depends('')
	def return_name(self):
		for line in self:
			if line.stado_zagon_id:
				if self.stado_zagon_id.doynie == True and (line.stado_zagon_id.mastit == False or line.stado_zagon_id.mastit is None):
					line.name = "Карусель"
				elif line.stado_zagon_id.doynie == True and line.stado_zagon_id.mastit == True:
					line.name = "Парабона"

				if line.kol_golov>0 and line.kol_golov_zagon>0:
					line.procent_neschitannih_golov = 100 - line.kol_golov*100/line.kol_golov_zagon

				line.nadoy_zagon = line.kol_golov_zagon * line.nadoy_golova


	
	#, related='stado_zagon_id.stado_fiz_group_id'
	name = fields.Char(string='Зал доения', default='New', compute='return_name', store=True)
	date = fields.Date(string='Дата', store=True, compute='return_date')
	stado_zagon_id = fields.Many2one('stado.zagon', string=u'Загон', required=True)
	stado_fiz_group_id = fields.Many2one('stado.fiz_group', string=u'Физиологическая группа', related='stado_zagon_id.stado_fiz_group_id', readonly=True,  store=True)
	
	kol_golov = fields.Integer(string=u"Считано голов", store=True, group_operator="avg", default=0)
	kol_golov_zagon = fields.Integer(string=u"Голов в загоне", store=True, group_operator="avg", default=0)
	procent_neschitannih_golov = fields.Float(digits=(3, 1), string=u"% несчитанных голов", compute='return_name', store=True, group_operator="avg", default=0)
	nadoy_golova = fields.Float(digits=(3, 2), string=u"Считано Ср. над/гол, л.", store=True, group_operator="avg", default=0)
	nadoy_golova_fakt = fields.Float(digits=(3, 2), string=u"Ср. над/гол, кг.", store=True, group_operator="avg", default=0)
	nadoy_zagon = fields.Integer( string=u"Считано Надой по загону, л.", compute='return_name', store=True, group_operator="sum", default=0)
	nadoy_zagon_fakt = fields.Integer( string=u"Надой по загону, кг.", store=True, group_operator="sum", default=0)
	procent_nadoy = fields.Float(digits=(3, 1), string=u"% надоя в группе", store=True, group_operator="avg", default=0)
	
	
	
	milk_nadoy_group_id = fields.Many2one('milk.nadoy_group',
		ondelete='cascade', string=u"Надой молока по группам", required=True)