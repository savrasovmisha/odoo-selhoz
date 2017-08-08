spisok = []
spisok.append(['milk.type_transport','',0])
spisok.append(['milk.transport','',0])
spisok.append(['milk.pricep','',0])
spisok.append(['milk.tanker','',0])
spisok.append(['milk.sale_milk','',0])
spisok.append(['milk.shkala_tanker5','',0])
spisok.append(['milk.scale_tanker','',0])
spisok.append(['milk.scale_tanker_line','',0])
spisok.append(['milk.sale_milk_line','',0])
spisok.append(['excel.extended','',0])
spisok.append(['milk.control_sale_milk','',0])
spisok.append(['milk.control_sale_milk_line','',0])
spisok.append(['milk.trace_milk','',0])
spisok.append(['milk.plan_sale_milk','',0])
spisok.append(['milk.plan_sale_milk_line','',0])
spisok.append(['milk.sale_milk_report','',0])
spisok.append(['milk.sale_milk_dashboard','',0])
spisok.append(['res.partner','',1])
# spisok.append(['milk.',''])
# spisok.append(['milk.',''])





print "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink"
for name in spisok:
	class_name = name[0].replace('.','_')
	modul_name = ''
	all_access = name[2]
	if len(name[1])>0:
		modul_name = name[1] + '.'
	print 'access_%(class_name)s_manager,%(name)s,%(modul_name)smodel_%(class_name)s,group_milk_manager,1,1,1,1' % {'name':name[0], 'class_name': class_name, 'modul_name': modul_name}
	if all_access == 0:
		print 'access_%(class_name)s_users,%(name)s,%(modul_name)smodel_%(class_name)s,group_milk_users,1,0,0,0'  % {'name':name[0], 'class_name': class_name, 'modul_name': modul_name}
	else:
		print 'access_%(class_name)s_users,%(name)s,%(modul_name)smodel_%(class_name)s,group_milk_users,1,1,1,0'  % {'name':name[0], 'class_name': class_name, 'modul_name': modul_name}

