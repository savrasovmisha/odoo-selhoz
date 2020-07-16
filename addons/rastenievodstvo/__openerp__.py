# -*- coding: utf-8 -*-
{
    'name': "Растениеводство",

    'summary': """
        Модуль предназначен для учета в растениеводстве
    """,

    'description': """
        Модуль предназначен для учета в растениеводстве
    """,

    'author': "Savrasov Mikhail",
    'website': "http://www.savrasov.ru",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Selskoe hozyaystvo',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','report', 'selhoz_base','sklad'],

    # always loaded
    'data': [
        'security/rastenievodstvo_security.xml',
           
        'views/polya.xml',
        'views/kultura.xml',
        'views/spp.xml',
        'views/rashod.xml',

        
        'views/menu.xml',
        'security/ir.model.access.csv',

    ],
   

}
