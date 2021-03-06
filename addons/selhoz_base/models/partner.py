# -*- coding: utf-8 -*-
from openerp import api, fields, models

class Partner(models.Model):
	_inherit = 'res.partner'

	@api.one
	@api.depends('zip','country_id','state_id','city','street','street2')
	def _format_address(self):
		address = [self.zip, self.country_id.name, self.state_id.name, self.city, self.street, self.street2]
		address = filter(bool, address)
		address = filter(None, address)
		self.address_formatted = ', '.join(address) if address else ""
		
	
	name_official = fields.Char('Полное наименование')
	#name_print_doc = fields.Char('Наименование для печати')
	
	inn = fields.Char(u'ИНН', size=12)
	kpp = fields.Char(u'КПП', size=9)
	okpo = fields.Char(u'ОКПО', size=14)
	contract_num = fields.Char(u'Номер договора', size=64)
	contract_date = fields.Date(u'Дата договора')
	ceo = fields.Char(u'ФИО руководителя', size=200, help="Example: Lenin V.I.")
	ceo_function = fields.Char(u'Должность руководителя', size=200)
	accountant = fields.Char(u'ФИО гл.бухгалтера', size=200)
	address_formatted = fields.Char(compute="_format_address", string=u'Полный адрес', store=False)
	

Partner()

# from openerp.osv import fields,osv

# class res_partner(osv.osv):

# 	""" Inherits partner and adds Tasks information in the partner form """
# 	_inherit = 'res.partner'
# 	_columns = {
# 		'full_name': fields.Char(string='Полное наименование'),
		
# 	}