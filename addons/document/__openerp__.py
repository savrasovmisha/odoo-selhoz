# -*- coding: utf-8 -*-
{
    'name': "Документооборот",

    'summary': """
        Документооборот
    """,

    'description': """
        Документооборот
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
        # 'security/ir.model.access.csv',
        
        'views/dogovor.xml',
     
                
        
        'views/menu.xml',

        'data/dogovor_vid_data.xml'

    ],
    #'update_xml': ["update.sql",],
    #'css': ['static/css/style.css'],
   

}
