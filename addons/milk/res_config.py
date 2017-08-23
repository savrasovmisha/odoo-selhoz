# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from openerp import api, fields, models
#from openerp.osv import fields, osv

class milk_config_settings(models.TransientModel):
#class milk_config(osv.osv_memory):
	_name = 'milk.config.settings'
	_inherit = 'res.config.settings'

	ip_server_api = fields.Char(string=u'IP адрес сервера API')
	dsn_selex = fields.Char(string=u'DNS Селекс')
	user_selex = fields.Char(string=u'Пользователь Селекс')
	password_selex = fields.Char(string=u'Пароль Селекс')
	dsn_uniform = fields.Char(string=u'DNS uniform')
	user_uniform = fields.Char(string=u'Пользователь uniform')
	password_uniform = fields.Char(string=u'Пароль uniform')
	kod_otel = fields.Integer(string=u'Код события Отелов в Селекс')
	kod_osemeneniya = fields.Integer(string=u'Код события Осеменения в Селекс')

	# #@api.one
	# def get_default_dsn_selex(self, cr, uid, ids, context=None):
	# 	#mc = self.search([('create_date', '>', '01.07.2016')],limit=1)
	# 	# for l in mc:
	# 	# 	print 'lllllllllllllllll==============', l.dsn_selex
	# 	#ff, = mc
	# 	#mc_pool = self.pool.get('milk.config.settings')
	# 	#mc = mc_pool.browse(cr, uid, uid, context=context)
	# 	#print 'ssssssssssssssssssssssssssssss=========',mc
	# 	#dsn_selex = "mc.dsn_selex"
	# 	self.pool.get('ir.values').set_default(cr, uid, 'milk.config.settings', 'dsn_selex', '1213123')
	# 	# self.user_selex = "mc[0].user_selex"
	# 	# self.password_selex = "mc[0].password_selex"
	# 	# if len(mc)>0: 
	# 	# 	self.dsn_selex = mc.dsn_selex
	# 		# self.user_selex = mc[0].user_selex
	# 		# self.password_selex = mc[0].password_selex
	@api.model
	def get_default_values(self, fields):
		"""
		Method argument "fields" is a list of names
		of all available fields.
		"""
		# mc = self.pool.get('milk.config.settings').browse(cr, uid, uid, context=context)
		# print 'ddddddddddddddddddd====', mc.dsn_selex
		conf = self.env['ir.config_parameter']
		#company = self.env.user.company_id
		return {
			'ip_server_api': conf.get_param('ip_server_api'),
			'dsn_selex': conf.get_param('dsn_selex'),
			'user_selex': conf.get_param('user_selex'),
			'password_selex': conf.get_param('password_selex'),
			'dsn_uniform': conf.get_param('dsn_uniform'),
			'user_uniform': conf.get_param('user_uniform'),
			'password_uniform': conf.get_param('password_uniform'),
			'kod_otel': int(conf.get_param('kod_otel')),
			'kod_osemeneniya': int(conf.get_param('kod_osemeneniya'))
			
		}
	@api.one
	def set_values(self):
		conf = self.env['ir.config_parameter']
		conf.set_param('ip_server_api', str(self.ip_server_api))
		conf.set_param('dsn_selex', str(self.dsn_selex))
		conf.set_param('user_selex', str(self.user_selex))
		conf.set_param('password_selex', str(self.password_selex))
		conf.set_param('dsn_uniform', str(self.dsn_uniform))
		conf.set_param('user_uniform', str(self.user_uniform))
		conf.set_param('password_uniform', str(self.password_uniform))
		conf.set_param('kod_otel', int(self.kod_otel))
		conf.set_param('kod_osemeneniya', int(self.kod_osemeneniya))