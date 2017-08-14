# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

#Проведение документов
class MultiKormKormWiz(models.TransientModel):
    _name = 'multi.korm_korm_wiz'

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
