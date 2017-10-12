# -*- coding: utf-8 -*-
{
    'name': "selhoz_base",

    'summary': """
        Базовый модель по Сельскохозяйственному учету
    """,

    'description': """
        Базовый модель по Сельскохозяйственному учету
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
        'views/res_config.xml',
        'views/paperformat.xml',
        'views/partner.xml',

        'views/stado_vid_fiz_group.xml',
        'views/stado_podvid_fiz_group.xml',
        'views/stado_fiz_group.xml',
        'views/stado_zagon.xml',

        'views/pricep.xml',
        'views/type_transport.xml',
        'views/transport.xml',

        'views/buh_nomen_group.xml',
        'views/buh_stati_zatrat.xml',
        'views/ed_izm_categ.xml',
        'views/ed_izm.xml',
        'views/nalog_nds.xml',
        'views/nomen_group.xml',
        'views/nomen_categ.xml',
        'views/nomen_nomen.xml',
        'views/sklad_sklad.xml',


        
        'security/base_security.xml',
        'security/ir.model.access.csv',
        
        
        # 'views/krs_hoz_view.xml',
        # 'views/krs_result_otel_view.xml',
        # 'views/krs_otel_view.xml',
        # 'views/krs_spv_view.xml',
        # 'views/krs_srashod_view.xml',
        # 'views/krs_cow_vibitiya_view.xml',
        # 'views/krs_tel_vibitiya_view.xml',
        # 'views/krs_osemeneniya_view.xml',
        # 'views/krs_abort_view.xml',
        # 'views/krs_struktura_view.xml',
        # 'views/krs_otchet_day_view.xml',
        # 'views/krs_otchet_day_report.xml',

        # 'wizard/krs_load_wiz_view.xml',
        # 'wizard/message_view.xml',
       
        
        # 'views/menu.xml',
        
        #'report/sale_milk_report_view.xml',
        
        #'views/templates.xml',
    ],
    #'update_xml': ["update.sql",],
    #'css': ['static/css/style.css'],
   

}
