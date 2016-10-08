# -*- coding: utf-8 -*-
from openerp import http

# class Milk(http.Controller):
#     @http.route('/milk/milk/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/milk/milk/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('milk.listing', {
#             'root': '/milk/milk',
#             'objects': http.request.env['milk.milk'].search([]),
#         })

#     @http.route('/milk/milk/objects/<model("milk.milk"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('milk.object', {
#             'object': obj
#         })