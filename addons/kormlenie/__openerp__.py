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
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'selhoz_base', 'sklad', 'milk','report'],
    # "external_dependencies": {
    #         'python': ['pandas']
    #    },

    # always loaded
    'data': [
        
        #'views/resources.xml',
        
        'views/korm_pit_standart.xml',
        'views/korm_analiz_pit.xml',
        # 'views/stado_vid_fiz_group.xml',
        # 'views/stado_podvid_fiz_group.xml',
        # 'views/stado_fiz_group.xml',
        # 'views/stado_zagon.xml',
        'views/korm_receptura.xml',
        'views/korm_racion.xml',
        'views/korm_racion_report.xml',
        'views/korm_norm.xml',
        'views/korm_korm.xml',
        'views/korm_korm_report.xml',
        'views/seq_korm_korm.xml',
        'views/korm_korm_ostatok.xml',
        'views/korm_korm_ostatok_report.xml',
        'views/seq_korm_korm_ostatok.xml',
        'reports/korm_svod_report_view.xml',
        'reports/korm_receptura_report_view.xml',
        'reports/korm_ostatok_report_view.xml',
        'reports/korm_rashod_kormov_report_view.xml',
        'reports/korm_plan_fakt_report_view.xml',
        'views/korm_potrebnost.xml',
        'views/korm_potrebnost_report.xml',
        'views/seq_korm_potrebnost.xml',
        'views/stado_struktura.xml',
        'views/seq_stado_struktura.xml',
        'views/korm_rashod_kormov.xml',
        'views/seq_korm_rashod_kormov.xml',
        'views/korm_plan.xml',
        'views/seq_korm_plan.xml',
        #'views/korm_korm_view.xml',
        'wizard/korm_korm_wiz_view.xml',
        'reports/korm_buh_report.xml',
        'reports/korm_buh_report_view.xml',

        'security/korm_security.xml',
        'security/ir.model.access.csv',
        
        'views/menu.xml',
        #'report/sale_milk_report_view.xml',
        
        #'views/templates.xml',
    ],
    #'update_xml': ["update.sql",],
    #'css': ['static/css/style.css'],
   

}
