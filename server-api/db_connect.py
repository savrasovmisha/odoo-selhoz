# -*- coding: utf-8 -*-
import psycopg2
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
from config import dsn_selex, user_selex, password_selex
from config import dsn_uniform, user_uniform, password_uniform

#######################################################
#######---ПОДКЛЮЧЕНИЕ К БАЗАМ-----###############################
####################################################### 


# Параметр vid = 
#               1 - добавление или изменение данных (INSERT, UPDATE, DALETE)
#               2 - получение результата запроса, возвращает все данные (SELECT)
#               3 - получение ID новой записи при INSERT ... RETURNING ID
#               4 - получение результата запроса, возвращает только одну, первую запись


# Параметр zapros - текст запроса к БД

# Параметр param - содержит значения для подставления в запрос. тип лист


#         Пример: 
#                   zapros='SELECT * FROM KORMA WHERE ID=?' 
#                   param=(id,)
#                   vid=2

###### База данных SELEX  ##################        
def con_selex(zapros, param,vid):
    #try:
        con=fdb.connect(dsn=dsn_selex,user=user_selex,password=password_selex, charset='UTF8')
        
        cur = con.cursor()
    
        cur.execute(zapros, param)
        if vid==4:
            result=cur.fetchone()   #возвращаем первую запись
        if vid>1:
            result=cur.fetchall()
        
        con.commit()
        cur.close()
        con.close()
        
        if vid>1:
            return result
    #except:
    #    print r'Ошибка при работе с базой SELEX'
    #    redirect('/error_bd')


###### База данных UNUFORM  ##################        
def con_uniform(zapros, param,vid):
    #try:
        con=fdb.connect(dsn=dsn_uniform,user=user_uniform,password=password_uniform, charset='UTF8')
        
        cur = con.cursor()
    
        cur.execute(zapros, param)
        if vid==4:
            result=cur.fetchone()   #возвращаем первую запись
        if vid>1:
            result=cur.fetchall()
        
        con.commit()
        cur.close()
        con.close()
        
        if vid>1:
            return result
