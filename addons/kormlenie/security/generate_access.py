spisok = []
spisok.append(['korm.pit_standart',''])
spisok.append(['stado.vid_fiz_group',''])
spisok.append(['stado.fiz_group',''])
spisok.append(['stado.zagon',''])
spisok.append(['korm.analiz_pit',''])
spisok.append(['korm.receptura',''])
spisok.append(['korm.receptura_line',''])
spisok.append(['korm.norm',''])
spisok.append(['korm.racion',''])
spisok.append(['korm.racion_line',''])
spisok.append(['korm.korm',''])
spisok.append(['korm.korm_line',''])
spisok.append(['korm.korm_svod_line',''])
spisok.append(['korm.korm_detail_line',''])
spisok.append(['korm.korm_ostatok',''])
spisok.append(['korm.korm_ostatok_line',''])
spisok.append(['korm.korm_ostatok_svod_line',''])
spisok.append(['korm.potrebnost',''])
spisok.append(['korm.potrebnost_zagon_line',''])
spisok.append(['korm.potrebnost_korm_line',''])
spisok.append(['korm.potrebnost_kombikorm_line',''])
spisok.append(['korm.korm_svod_report',''])
spisok.append(['korm.korm_receptura_report',''])
spisok.append(['nomen.ed_izm_categ','sklad'])
spisok.append(['nomen.ed_izm','sklad'])
spisok.append(['nomen.categ','sklad'])
spisok.append(['nomen.group','sklad'])
spisok.append(['nomen.nomen','sklad'])
spisok.append(['sklad.sklad','sklad'])
spisok.append(['milk.type_transport','milk'])
spisok.append(['milk.transport','milk'])
spisok.append(['milk.pricep','milk'])
spisok.append(['stado.struktura',''])
spisok.append(['stado.struktura_line',''])
spisok.append(['korm.korm_ostatok_report',''])
spisok.append(['korm.rashod_kormov',''])
spisok.append(['korm.rashod_kormov_line',''])
spisok.append(['korm.rashod_kormov_report',''])
spisok.append(['reg.rashod_kormov',''])
spisok.append(['korm.plan',''])
spisok.append(['korm.plan_line',''])
spisok.append(['korm.plan_fakt_report',''])
spisok.append(['stado.podvid_fiz_group',''])
spisok.append(['korm.buh_report',''])

spisok.append(['stado.fiz_group',''])
spisok.append(['stado.zagon',''])
spisok.append(['korm.analiz_potrebleniya_kormov_report',''])
spisok.append(['korm.analiz_efekt_korm_report',''])


print "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink"
for name in spisok:
	class_name = name[0].replace('.','_')
	modul_name = ''
	if len(name[1])>0:
		modul_name = name[1] + '.'
	print 'access_%(class_name)s_manager,%(name)s,%(modul_name)smodel_%(class_name)s,group_korm_manager,1,1,1,1' % {'name':name[0], 'class_name': class_name, 'modul_name': modul_name}
	print 'access_%(class_name)s_users,%(name)s,%(modul_name)smodel_%(class_name)s,group_korm_users,1,0,0,0'  % {'name':name[0], 'class_name': class_name, 'modul_name': modul_name}

