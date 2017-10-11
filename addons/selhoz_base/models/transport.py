# -*- coding: utf-8 -*-

from openerp import api, fields, models

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
	# @api.onchange('mark', 'gos_nomer')
	@api.one
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
	@api.one
	@api.depends('gos_nomer')
	def _update_name(self):
		if self.gos_nomer:
			self.name = self.gos_nomer