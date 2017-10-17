spisok = []
spisok.append(['milk.type_transport',''])
spisok.append(['milk.transport',''])
spisok.append(['milk.pricep',''])
spisok.append(['milk.tanker',''])
spisok.append(['milk.sale_milk',''])
spisok.append(['milk.shkala_tanker5',''])
spisok.append(['milk.scale_tanker',''])
spisok.append(['milk.scale_tanker_line',''])
spisok.append(['milk.sale_milk_line',''])
spisok.append(['excel.extended',''])
spisok.append(['milk.control_sale_milk',''])
spisok.append(['milk.control_sale_milk_line',''])
spisok.append(['milk.trace_milk',''])
spisok.append(['milk.plan_sale_milk',''])
spisok.append(['milk.plan_sale_milk_line',''])
spisok.append(['milk.sale_milk_report',''])
spisok.append(['milk.sale_milk_dashboard',''])
spisok.append(['res.partner',''])
spisok.append(['milk.trace_milk_ostatok_line',''])
spisok.append(['milk.buh_report',''])
spisok.append(['milk.price',''])
spisok.append(['milk.trace_milk_vipoyka_line',''])
spisok.append(['milk.nadoy_group',''])
spisok.append(['milk.nadoy_group_line',''])


spisok_read = []
spisok_read.append(['krs.struktura',''])






print "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink"
for name in spisok:
	class_name = name[0].replace('.','_')
	modul_name = ''
	
	if len(name[1])>0:
		modul_name = name[1] + '.'
	print 'access_%(class_name)s_manager,%(name)s,%(modul_name)smodel_%(class_name)s,group_milk_manager,1,1,1,1' % {'name':name[0], 'class_name': class_name, 'modul_name': modul_name}
	print 'access_%(class_name)s_users,%(name)s,%(modul_name)smodel_%(class_name)s,group_milk_users,1,0,0,0'  % {'name':name[0], 'class_name': class_name, 'modul_name': modul_name}

#REad only
# for name in spisok_read:
# 	class_name = name[0].replace('.','_')
# 	modul_name = ''
	
# 	if len(name[1])>0:
# 		modul_name = name[1] + '.'
# 	print 'access_%(class_name)s_manager,%(name)s,%(modul_name)smodel_%(class_name)s,group_milk_manager,1,0,0,0' % {'name':name[0], 'class_name': class_name, 'modul_name': modul_name}
# 	print 'access_%(class_name)s_users,%(name)s,%(modul_name)smodel_%(class_name)s,group_milk_users,1,0,0,0'  % {'name':name[0], 'class_name': class_name, 'modul_name': modul_name}
