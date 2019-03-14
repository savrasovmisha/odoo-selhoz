# -*- coding: utf-8 -*-
{
    'name': "kombikorma",

    'summary': """
        Модуль предназначен для учета производства комбикормов
    """,

    'description': """
        Модуль предназначен для учета производства комбикормов
    """,

    'author': "Savrasov Mikhail",
    'website': "http://www.savrasov.ru",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Selskoe hozyaystvo',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','report', 'selhoz_base','sklad', 'kormlenie'],

    # always loaded
    'data': [
        'security/kombikorma_security.xml',
           
        'views/kombikorma_proizvodstvo.xml',

        
        'views/menu.xml',
        'security/ir.model.access.csv',

    ],
   

}
