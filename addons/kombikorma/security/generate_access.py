spisok = []
spisok.append(['kombikorma.proizvodstvo',''])
spisok.append(['kombikorma.proizvodstvo_line',''])



print "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink"
for name in spisok:
	class_name = name[0].replace('.','_')
	modul_name = ''
	if len(name[1])>0:
		modul_name = name[1] + '.'
	print 'access_%(class_name)s_manager,%(name)s,%(modul_name)smodel_%(class_name)s,group_kombikorma_manager,1,1,1,1' % {'name':name[0], 'class_name': class_name, 'modul_name': modul_name}
	print 'access_%(class_name)s_users,%(name)s,%(modul_name)smodel_%(class_name)s,group_kombikorma_users,1,0,0,0'  % {'name':name[0], 'class_name': class_name, 'modul_name': modul_name}

