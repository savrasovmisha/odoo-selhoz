# -*- coding: utf-8 -*-

import requests, json

url_connect = "http://192.168.1.22:8069/web/session/authenticate"
url = "http://192.168.1.22:8069:8069/web/session/get_session_info"

headers = {'Content-Type': 'application/json'}

data_connect = {
    "params": {
        "db": "ea_20190611",
        "login": "savrasov_misha@mail.ru",
        "password": "gfhjkm",
    }
}


session = requests.Session()

r = session.post(url=url_connect, data=json.dumps(data_connect), headers=headers)
print "rrr", r
if r.ok:
    result = r.json()['result']
    print "rrr", result

    if result.get('session_id'):
        session.cookies['session_id'] = result.get('session_id')
        print "sss", result.get('session_id')
     
# data = {}
# r = session.post(url=url, data=json.dumps(data), headers=headers)
# print(r)
# print(r.json())


data = {
    "params": {
    	
    	#"session_id" : 'f4322002-8c03-11e9-a42e-485b39d43545',
        "name":"prakashsharma",
        "email":"prakashsharmacs24@gmail.com",
        "phone":"+917859884833"
    }
}
t = requests.post('http://192.168.1.22:8069/web/test', headers=headers, data=json.dumps(data))
print t.text