# -*- coding: utf-8 -*-
{
    'name': "kormlenie",

    'summary': """
        Modul prednaznachen dlya processa kormleniya korov
    """,

    'description': """
        Modul prednaznachen dlya processa kormleniya korov
    """,

    'author': "Savrasov Mikhail",
    'website': "http://www.savrasov.ru",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Selskoe hozyaystvo',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/kormlenie_security.xml',
        'security/ir.model.access.csv',
        
        'views/ed_izm_categ.xml',
        'views/ed_izm.xml',
        'views/menu.xml',
        
        #'report/sale_milk_report_view.xml',
        
        #'views/templates.xml',
    ],
   

}
