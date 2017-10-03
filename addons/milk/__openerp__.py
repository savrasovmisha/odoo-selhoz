# -*- coding: utf-8 -*-
{
    'name': "milk",

    'summary': """
        Modul prednaznachen
    """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Savrasov Mikhail",
    'website': "http://www.savrasov.ru",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Selskoe hozyaystvo',
    'version': '0.24',

    # any module necessary for this one to work correctly
    'depends': ['base', 'report', 'board', 'krs'],

    # always loaded
    'data': [
        'security/milk_security.xml',
        'security/ir.model.access.csv',
        'views/partner.xml',
        'views/pricep.xml',
        'views/type_transport.xml',
        'views/transport.xml',
        'views/tanker.xml',
        'views/sale_milk.xml',
        #'report/sale_milk_report_view.xml',
        'views/report.xml',
        'views/seq_sale_milk.xml',
        'views/shkala_tanker5.xml',
        'views/scale_tanker.xml',
        'views/control_sale_milk.xml',
        'views/trace_milk.xml',
        'views/plan_sale_milk.xml',
        'views/milk_dashboard.xml',
        'views/res_config.xml',
        'views/milk_price.xml',
        'report/milk_buh_report_view.xml',
        
        'views/menu.xml',
        'views/resources.xml',
        
        #'views/templates.xml',
    ],
    
    'qweb': [
        "static/src/xml/sales_milk_dashboard.xml"],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
