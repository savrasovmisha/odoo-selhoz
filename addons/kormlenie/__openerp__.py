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
    'depends': ['base', 'sklad', 'milk','report'],

    # always loaded
    'data': [
        'security/korm_security.xml',
        'security/ir.model.access.csv',
        
        'views/korm_pit_standart.xml',
        'views/korm_analiz_pit.xml',
        'views/stado_fiz_group.xml',
        'views/stado_zagon.xml',
        'views/korm_receptura.xml',
        'views/korm_racion.xml',
        'views/korm_norm.xml',
        'views/korm_korm.xml',
        'views/korm_korm_report.xml',
        'views/seq_korm_korm.xml',
        'views/menu.xml',
        'views/resources.xml',
        
        #'report/sale_milk_report_view.xml',
        
        #'views/templates.xml',
    ],
    'css': ['static/css/style.css'],
   

}
