# -*- coding: utf-8 -*-
{
    'name': "KRS",

    'summary': """
        Modul prednaznachen dlya ucheta KRS v jivotnovodstve
    """,

    'description': """
        Modul prednaznachen dlya ucheta KRS v jivotnovodstve
    """,

    'author': "Savrasov Mikhail",
    'website': "http://www.savrasov.ru",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Selskoe hozyaystvo',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'report'],
    # "external_dependencies": {
    #         'python': ['pandas']
    #    },

    # always loaded
    'data': [
        'security/krs_security.xml',
        'security/ir.model.access.csv',
        #'views/resources.xml',
        
        'views/krs_hoz_view.xml',
        'views/krs_result_otel_view.xml',
        'views/krs_otel_view.xml',

        'wizard/krs_load_wiz_view.xml',
        'wizard/message_view.xml',
       
        
        'views/menu.xml',
        
        #'report/sale_milk_report_view.xml',
        
        #'views/templates.xml',
    ],
    #'update_xml': ["update.sql",],
    #'css': ['static/css/style.css'],
   

}
