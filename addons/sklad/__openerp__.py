# -*- coding: utf-8 -*-
{
    'name': "sklad",

    'summary': """
        Modul prednaznachen dlya processa skladskogo ucheta
    """,

    'description': """
        Modul prednaznachen dlya processa skladskogo ucheta
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
        'security/sklad_security.xml',
        'security/ir.model.access.csv',
        
        'views/ed_izm_categ.xml',
        'views/ed_izm.xml',
        'views/nalog_nds.xml',
        'views/nomen_group.xml',
        'views/nomen_categ.xml',
        'views/nomen_nomen.xml',
        'views/sklad_sklad.xml',
        'views/pokupka_pokupka.xml',
        'views/pokupka_pokupka_workflow.xml',
        'views/seq_pokupka_pokupka.xml',
        'views/menu.xml',
        
        #'report/sale_milk_report_view.xml',
        
        #'views/templates.xml',
    ],
   

}
