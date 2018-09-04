spisok = []
spisok.append(['aktiv.categ','', 1])
spisok.append(['aktiv.aktiv','', 1])
spisok.append(['aktiv.type','', 1])
spisok.append(['aktiv.status','', 1])
spisok.append(['aktiv.vid_rabot','', 1])
spisok.append(['aktiv.vid_rabot_price_line','', 1])
spisok.append(['aktiv.vid_remonta','', 1])
spisok.append(['aktiv.tr','', 1])
spisok.append(['aktiv.tr_raboti_line','', 1])
spisok.append(['aktiv.tr_nomen_line','', 1])
spisok.append(['aktiv.gr','', 1])
spisok.append(['aktiv.gr_line','', 1])
spisok.append(['nomen.nomen','selhoz_base', 0])
spisok.append(['nomen.nomen_price_line','selhoz_base', 0])


# access_nomen_nomen_manager,nomen.nomen,selhoz_base.model_nomen_nomen,group_sklad_manager,1,1,1,1
# access_nomen_nomen_price_line_manager,nomen.nomen_price_line,selhoz_base.model_nomen_nomen_price_line,group_sklad_manager,1,1,1,1
#access_aktiv_gr_line_manager,aktiv.gr_line,model_aktiv_gr_line,group_toir_manager,1,1,1,1
# spisok_read = []
# spisok_read.append(['buh.nomen_group',''])
# spisok_read.append(['buh.stati_zatrat',''])
# spisok_read.append(['nomen.ed_izm_categ',''])
# spisok_read.append(['nomen.ed_izm',''])
# spisok_read.append(['nomen.categ',''])
# spisok_read.append(['nomen.group',''])
# spisok_read.append(['nomen.nomen',''])
# spisok_read.append(['sklad.sklad',''])
# spisok_read.append(['dogovor',''])
# spisok_read.append(['nalog.nds',''])






print "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink"
for name in spisok:
	class_name = name[0].replace('.','_')
	modul_name = ''
	
	if len(name[1])>0:
		modul_name = name[1] + '.'
	print 'access_%(class_name)s_manager,%(name)s,%(modul_name)smodel_%(class_name)s,group_toir_manager,1,1,1,1' % {'name':name[0], 'class_name': class_name, 'modul_name': modul_name}
	
	if name[2] == 1:
		print 'access_%(class_name)s_users,%(name)s,%(modul_name)smodel_%(class_name)s,group_toir_users,1,0,0,0'  % {'name':name[0], 'class_name': class_name, 'modul_name': modul_name}

# #REad only
# for name in spisok_read:
# 	class_name = name[0].replace('.','_')
# 	modul_name = ''
	
# 	if len(name[1])>0:
# 		modul_name = name[1] + '.'
# 	#print 'access_%(class_name)s_manager,%(name)s,%(modul_name)smodel_%(class_name)s,group_milk_manager,1,0,0,0' % {'name':name[0], 'class_name': class_name, 'modul_name': modul_name}
# 	print 'access_%(class_name)s_users,%(name)s,%(modul_name)smodel_%(class_name)s,base.group_user,1,0,0,0'  % {'name':name[0], 'class_name': class_name, 'modul_name': modul_name}
