# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

#Проведение документов
class MultiKormKormWiz(models.TransientModel):
	_name = 'multi.korm_korm_wiz'

	date_start = fields.Date(string='Дата начала', required=True, default=fields.Datetime.now)
	date_end = fields.Date(string='Дата окончания', required=True, default=fields.Datetime.now)

	@api.multi
	def confirm_multi_korm_korm(self):
		korm_korm_ids = self.env['korm.korm'].browse(self._context.get('active_ids'))
		for korm_korm in korm_korm_ids:
			if korm_korm.state == 'draft':
				korm_korm.action_confirm()

	@api.multi
	def draft_multi_korm_korm(self):
		korm_korm_ids = self.env['korm.korm'].browse(self._context.get('active_ids'))
		for korm_korm in korm_korm_ids:
			if korm_korm.state == 'confirmed':
				korm_korm.action_draft()

	@api.multi
	def err_multi_korm_korm(self):
		korm_korm_ids = self.env['korm.korm'].browse(self._context.get('active_ids'))
		for korm_korm in korm_korm_ids:
			if korm_korm.state == 'draft':
				korm_korm.action_raschet_err()

	@api.multi
	def all_multi_korm_korm(self):
		korm_korm_ids = self.env['korm.korm'].browse(self._context.get('active_ids'))
		for korm_korm in korm_korm_ids:
			if korm_korm.state == 'confirmed':
				korm_korm.action_draft()
			if korm_korm.state == 'draft':
				korm_korm.action_raschet_err()
				korm_korm.action_confirm()


	@api.multi
	def reconfirm_period_korm_korm(self):
		self.ensure_one()
		korm = self.env['korm.korm']
		korm_ids = korm.search([ ('date',  '>=',    self.date_start),
											   ('date',  '<=',    self.date_end)
											])
		
		for line in korm_ids:
			korm_korm = self.env['korm.korm'].browse(line.id)
			if korm_korm.state == 'confirmed':
				korm_korm.action_draft()
				korm_korm.action_confirm()

