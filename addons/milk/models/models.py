# -*- coding: utf-8 -*-

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

class type_transport(models.Model):
    _name = 'milk.type_transport'
    
    name = fields.Char(string=u"Name", required=True)


class transport(models.Model):
	_name = 'milk.transport'

	name = fields.Char(string=u"Name", default='New', required=True, copy=False, readonly=True, compute='_update_name', store=True)
	mark = fields.Char(string=u"Mark", required=True)
	gos_nomer = fields.Char(string=u"Gos nomer", required=True)
	type_transport_id = fields.Many2one('milk.type_transport', string=u"type_transport", default=None)
	max_value = fields.Integer(string=u"Грузоподъемность, кг") 
	# @api.one
	# @api.onchange('mark', 'gos_nomer')
	@api.depends('mark', 'gos_nomer')
	def _update_name(self):
		if self.mark and self.gos_nomer:
			self.name = self.mark + ' ' + self.gos_nomer


class pricep(models.Model):
	_name = 'milk.pricep'

	name = fields.Char(string=u"Name", default='New', required=True, copy=False, readonly=True, compute='_update_name', store=True)
	type_transport_id = fields.Many2one('milk.type_transport', string=u"type_transport", default=None)
	gos_nomer = fields.Char(string=u"Gos nomer", required=True)

	# @api.onchange('gos_nomer')
	@api.depends('gos_nomer')
	def _update_name(self):
		if self.gos_nomer:
			self.name = self.gos_nomer



class tanker(models.Model):
	_name = 'milk.tanker'

	name = fields.Char(string=u"Name", required=True)
	max_size = fields.Integer(string=u"max size", required=True)
	is_meter = fields.Boolean(string=u"is meter", default=True)
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
	avg_jir = fields.Float(digits=(3, 1), string=u"Среднее жир", default=0, 
										readonly=True, compute='_amount_all', store=True, group_operator="avg")
	avg_belok = fields.Float(digits=(3, 2), string=u"Среднее белок", default=0, 
										readonly=True, compute='_amount_all', store=True, group_operator="avg")
	avg_plotnost = fields.Float(digits=(4, 2), string=u"Среднее плотность", default=0, 
										readonly=True, compute='_amount_all', store=True, group_operator="avg")
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
	@api.depends('sale_milk_line.tanker_id','sale_milk_line.meter_value',
				'sale_milk_line.jir','sale_milk_line.belok','sale_milk_line.plotnost', 'sale_milk_line.ves_natura')
	def _amount_all(self):
		"""
		Compute the total amounts of the SO.
		"""
		
		self.amount_ves_natura = 0
		self.amount_ves_zachet = 0
		self.avg_jir = 0
		self.avg_belok = 0
		self.avg_plotnost = 0
		_sum_jir = 0
		_sum_belok = 0
		_sum_plotnost = 0
		
		for line in self.sale_milk_line:
			self.amount_ves_natura += line.ves_natura
			self.amount_ves_zachet += line.ves_zachet
			_sum_jir += line.jir * line.ves_natura
			_sum_belok += line.belok * line.ves_natura
			_sum_plotnost += line.plotnost * line.ves_natura
		
		if self.amount_ves_natura>0:
			self.avg_jir = _sum_jir / self.amount_ves_natura
			self.avg_belok = _sum_belok / self.amount_ves_natura	
			self.avg_plotnost = _sum_plotnost / self.amount_ves_natura	


	def create_ttn(self, cr, uid, ids, context=None):
		
		s_m = self.browse(cr, uid, ids[0], context=context)
		
		if s_m.split_line:
			s_m_line = s_m.sale_milk_line
		else:
			s_m_line = [{"jir": s_m.avg_jir, "belok": s_m.avg_belok, "plotnost": s_m.avg_plotnost, "ves_natura": s_m.amount_ves_natura},]

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
		cmd = 'libreoffice5.1 --headless --convert-to pdf --outdir '+tmp_dir+' '+ output_filename
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
	jir = fields.Float(digits=(3, 1))
	belok = fields.Float(digits=(3, 2))
	plotnost = fields.Float(digits=(4, 2))
	ves_natura = fields.Integer(string=u"natura",  store=True)
	ves_zachet = fields.Integer(string=u"zachetniy ves", compute='_raschet', store=True)
	som_kletki = fields.Integer(string=u"somaticheskie kletki")
	somo = fields.Float(digits=(4, 2))
	
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
			if self.tanker_id.is_meter == True:
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


	is_meter = fields.Char(string=u"Meter", compute='_is_meter', readonly=True, default='')
	


	@api.one
#	@api.onchange('tanker_id')
	@api.depends('tanker_id')
	def _is_meter(self):
		if self.tanker_id:
			if self.tanker_id.is_meter == True:
				self.is_meter = u'Счетчик'
			else:
				self.is_meter = u'Линейка'
		else:
			self.is_meter = ''









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

		
	name = fields.Char(string='Description', required=True, default='New', store=True, compute='return_name')
	
	date_doc = fields.Date(string='Дата документа', required=True,  
						index=True, copy=False, default=fields.Datetime.now)

	vipoyka = fields.Integer(string=u"На выпойку", store=True)
	utilizaciya = fields.Integer(string=u"Утилизированно", store=True)
	sale_natura = fields.Integer(string=u"Реализованно", store=True, compute='_sale_result')
	sale_zachet = fields.Integer(string=u"Зачетный вес", store=True, compute='_sale_result')
	sale_jir = fields.Float(digits=(3, 1), string=u"Жир", store=True, compute='_sale_result', group_operator="avg")
	sale_belok = fields.Float(digits=(3, 2), string=u"Белок", store=True, compute='_sale_result', group_operator="avg")
	
	valoviy_nadoy = fields.Integer(string=u"Валовый надой", store=True, compute='_valoviy_nadoy_result')
	otk_valoviy_nadoy = fields.Float(digits=(3, 3), string=u"Откл-е Валовый надой от предыд. дня", compute='_otk_result', store=False)

	sale_peresdali_natura = fields.Integer(string=u"Пересдали натура", store=True, compute='_sale_result')
	sale_peresdali_zachet = fields.Integer(string=u"Пересдали зачет", store=True, compute='_sale_result')

	cow_doy = fields.Integer(string=u"Дойные", store=True, group_operator="avg")
	cow_zapusk = fields.Integer(string=u"В запуске", store=True, group_operator="avg")
	cow_fur = fields.Integer(string=u"Фуражные", store=True, compute='_nadoy_result', group_operator="avg")
	cow_netel = fields.Integer(string=u"Нетели", store=True, group_operator="avg")
	cow_total = fields.Integer(string=u"Общее поголовье", store=True, group_operator="avg")

	nadoy_doy = fields.Float(digits=(3, 1), string=u"Надой на дойную", store=True, compute='_nadoy_result', group_operator="avg")
	nadoy_fur = fields.Float(digits=(3, 1), string=u"Надой на фуражную", store=True, compute='_nadoy_result', group_operator="avg")
	otk_nadoy_doy = fields.Float(digits=(3, 1), string=u"Откл-е от предыд. дня", compute='_otk_result', store=False)
	otk_nadoy_fur = fields.Float(digits=(3, 1), string=u"Откл-е от предыд. дня", compute='_otk_result', store=False)

	nadoy_0_40 = fields.Float(digits=(3, 2), string=u"Надой 0-40", store=True, group_operator="avg")
	nadoy_40_150 = fields.Float(digits=(3, 2), string=u"Надой 40-150", store=True, group_operator="avg")
	nadoy_150_300 = fields.Float(digits=(3, 2), string=u"Надой 150-300", store=True, group_operator="avg")
	nadoy_300 = fields.Float(digits=(3, 2), string=u"Надой >300", store=True, group_operator="avg")

	otk_0_40 = fields.Float(digits=(3, 2), string=u"Откл-е Надой 0-40", compute='_otk_nadoy_result', store=False, group_operator="avg")
	otk_40_150 = fields.Float(digits=(3, 2), string=u"Откл-е 40-150", compute='_otk_nadoy_result', store=False, group_operator="avg")
	otk_150_300 = fields.Float(digits=(3, 2), string=u"Откл-е 150-300", compute='_otk_nadoy_result', store=False, group_operator="avg")
	otk_300 = fields.Float(digits=(3, 2), string=u"Откл-е >300", compute='_otk_nadoy_result', store=False, group_operator="avg")

	description = fields.Text(string=u"Коментарии")

	
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



			
	@api.one
	@api.depends('vipoyka','utilizaciya','date_doc')
	def _valoviy_nadoy_result(self):
		self.valoviy_nadoy = self.vipoyka + self.utilizaciya + self.sale_natura

	@api.one
	@api.depends('cow_doy','cow_zapusk','cow_netel','date_doc', 'vipoyka', 'utilizaciya')
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
    ], default=str(datetime.today().month), required=True)
	
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

