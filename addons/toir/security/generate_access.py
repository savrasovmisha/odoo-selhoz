spisok = []
spisok.append(['aktiv.categ',''])
spisok.append(['aktiv.aktiv',''])
spisok.append(['aktiv.type',''])
spisok.append(['aktiv.status',''])

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
	print 'access_%(class_name)s_users,%(name)s,%(modul_name)smodel_%(class_name)s,group_toir_users,1,0,0,0'  % {'name':name[0], 'class_name': class_name, 'modul_name': modul_name}

# #REad only
# for name in spisok_read:
# 	class_name = name[0].replace('.','_')
# 	modul_name = ''
	
# 	if len(name[1])>0:
# 		modul_name = name[1] + '.'
# 	#print 'access_%(class_name)s_manager,%(name)s,%(modul_name)smodel_%(class_name)s,group_milk_manager,1,0,0,0' % {'name':name[0], 'class_name': class_name, 'modul_name': modul_name}
# 	print 'access_%(class_name)s_users,%(name)s,%(modul_name)smodel_%(class_name)s,base.group_user,1,0,0,0'  % {'name':name[0], 'class_name': class_name, 'modul_name': modul_name}
