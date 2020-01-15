# -*- coding: utf-8 -*-


err = ''
import pandas as pd
import numpy as np
import base64


try:

	frame = pd.read_csv('/home/savrasov/temp/milk.nadoy_group-580-file_milk', 
	                sep=';', 
	                header=0, 
	                usecols=[u"ИД", u"ГРУПА", u"ДОМИК", u"ДДНИ", u"ЛАКТ", u"МОЛ1"], 
	                encoding='cp1251')
except:
	err += u"Ошибка чтения файла."
	break
	
print err
frame = frame.drop(frame.index[len(frame)-1])

self.kol_golov = frame[u"ИД"].count()

frame[u"kol_milk"] = frame[u"МОЛ1"].astype(int)
frame = frame[frame[u'kol_milk']!=0] #Удаляем записи где надой молока =0
frame[u"GROEPNR"] = frame[u"ГРУПА"].astype(int)
frame[u"ДДНИ"] = frame[u"ДДНИ"].astype(int)
frame[u"ЛАКТ"] = frame[u"ЛАКТ"].astype(int)
frame[u"nomer_lakt"] = np.where(frame[u'ЛАКТ']>2, 3, frame[u'ЛАКТ'])

#frame[u"МОЛ2"] = frame[u"МОЛ1"]/2
frame['n015'] = np.where((frame[u'kol_milk']>0) & (frame[u'kol_milk']<15), 1, 0)
frame['n1520'] = np.where((frame[u'kol_milk']>=15) & (frame[u'kol_milk']<20), 1, 0)
frame['n2025'] = np.where((frame[u'kol_milk']>=20) & (frame[u'kol_milk']<25), 1, 0)
frame['n2530'] = np.where((frame[u'kol_milk']>=25) & (frame[u'kol_milk']<30), 1, 0)
frame['n3035'] = np.where((frame[u'kol_milk']>=30) & (frame[u'kol_milk']<35), 1, 0)
frame['n3540'] = np.where((frame[u'kol_milk']>=35) & (frame[u'kol_milk']<40), 1, 0)
frame['n4045'] = np.where((frame[u'kol_milk']>=40) & (frame[u'kol_milk']<45), 1, 0)
frame['n45'] = np.where(frame[u'kol_milk']>=45, 1, 0)

