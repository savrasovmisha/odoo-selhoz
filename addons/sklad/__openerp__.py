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
    'depends': ['base','report'],

    # always loaded
    'data': [
        'security/sklad_security.xml',
        
        'views/buh_nomen_group.xml',
        'views/buh_stati_zatrat.xml',
        'views/ed_izm_categ.xml',
        'views/ed_izm.xml',
        'views/nalog_nds.xml',
        'views/nomen_group.xml',
        'views/nomen_categ.xml',
        'views/nomen_nomen.xml',
        'views/sklad_sklad.xml',
        'views/pokupka_pokupka.xml',
        #'views/pokupka_pokupka_workflow.xml',
        'views/seq_pokupka_pokupka.xml',
        'views/prodaja_prodaja.xml',
        'views/seq_prodaja_prodaja.xml',
        'views/sklad_peremeshenie.xml',
        'views/seq_sklad_peremeshenie.xml',
        'views/sklad_spisanie.xml',
        'views/sklad_spisanie_report.xml',
        'views/seq_sklad_spisanie.xml',
        'views/sklad_trebovanie_nakladnaya.xml',
        'views/sklad_trebovanie_nakladnaya_report.xml',
        'views/seq_sklad_trebovanie_nakladnaya.xml',
        'views/sklad_inventarizaciya.xml',
        'views/seq_sklad_inventarizaciya.xml',
        'views/nomen_price.xml',
        'views/seq_nomen_price.xml',
        'views/menu.xml',
        'security/ir.model.access.csv',
        
        #'report/sale_milk_report_view.xml',
        
        #'views/templates.xml',
    ],
   

}
