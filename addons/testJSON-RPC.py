import json
import urllib2

db = 'ea_20190611'
user = 'savrasov_misha@mail.ru'
password = 'gfhjkm'
request = urllib2.Request(
				 'http://192.168.1.22:8069/web/session/authenticate',
				 json.dumps({
				 'jsonrpc': '2.0',
				 'params': {
				 'db': db,
				 'login': user,
				 'password': password,
				 },
				 }),
				 {'Content-type': 'application/json'})

result = urllib2.urlopen(request).read()

print 'r111', result
result = json.loads(result)

session_id = result['result']['session_id']
request = urllib2.Request(
			 'http://localhost:8069/web/dataset/call_kw',
			 json.dumps({
			 'jsonrpc': '2.0',
			 'params': {
			 'model': 'nomen.nomen',
			 'method': 'search_read',
			 'args': [
			 [('is_proizvodim', '=', 'True')],
			 ['name'],
			 ],
			 'kwargs': {'context': {}},
			 },
			 }),
			 {
			 'X-Openerp-Session-Id': session_id,
			 'Content-type': 'application/json',
			 })

result = urllib2.urlopen(request).read()
result = json.loads(result)
for module in result['result']:
	print module['name']



request = urllib2.Request(
				 'http://localhost:8069/web/dataset/call_kw',
				 json.dumps({
					 'jsonrpc': '2.0',
					 'params': {
								 'model': 'nomen.nomen',
								 'method': 'create',
								 'args': [{
							 			'name': '1111111',
							 			#'ed_izm_id': '1'
							 			}],
					 			'kwargs': {'context': {'lang': 'fr_FR'}},
					 			},
					 }),
			 {
			 'X-Openerp-Session-Id': session_id,
			 'Content-type': 'application/json',
			 })

result = urllib2.urlopen(request).read()
result = json.loads(result)
print 'rrrr', result
for module in result['result']:
	print module['name']