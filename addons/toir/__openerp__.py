# -*- coding: utf-8 -*-
{
    'name': "TOiR",

    'summary': """
        Техническое обслуживание и ремонты
    """,

    'description': """
        Техническое обслуживание и ремонты
    """,

    'author': "Savrasov Mikhail",
    'website': "http://www.savrasov.ru",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Selskoe hozyaystvo',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'report', 'selhoz_base'],
    # "external_dependencies": {
    #         'python': ['pandas']
    #    },

    # always loaded
    'data': [
        'security/base_security.xml',
        'security/ir.model.access.csv',
        
        'views/aktiv_categ.xml',
        'views/aktiv_type.xml',
        'views/aktiv_status.xml',
        'views/aktiv_aktiv.xml',
        'views/aktiv_vid_rabot.xml',
        'views/aktiv_vid_remonta.xml',
        'views/aktiv_tr.xml',
        'views/aktiv_gr.xml',
        'views/res_currency.xml',
                
        
        'views/menu.xml',

        'data/aktiv_status_data.xml'

    ],
    #'update_xml': ["update.sql",],
    #'css': ['static/css/style.css'],
   

}
