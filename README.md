# odoo-selhoz
Odoo для сельскохозяйственного предприятия


##########################################################
##############  Необходимые пакеты #################################

pandas =>16 
xlsxwriter


#####  instal pandas 19 Если в репозитарии старый пакет
загрузить и установить http://ftp.br.debian.org/debian/pool/main/p/python-numpy/python-numpy_1.12.1-3_amd64.deb
sudo dpkg -i путь_до python-numpy_1.12.1-3_amd64.deb

Add the following line to /etc/apt/sources.list:
deb http://neurodebian.ovgu.de/debian/ xenial main contrib non-free
Install GPG key of the repository:
# sudo apt-key adv --recv-keys --keyserver pgp.mit.edu 2649A5A9
Update the package index:
# sudo apt-get update
Install python-pandas deb package:
# sudo apt-get install python-pandas

##########################################################

Загрузка изменений на github

git add %file_path%
git commit -m "%commit_message%"
git push origin master

Скачать изменения на комп
git pull


Восстановить удалённый файл
Сначала нужно найти последний коммит, где файл еще существовал:

git rev-list -n 1 HEAD -- имя_файла

Потом восстановить этот файл:

git checkout найденный_коммит^ -- имя_файла


В случае внесения локальных изменений, при попытки обновить данные с сервера будет ошибка 
error: Your local changes to the following files would be overwritten by merge:
  addons/kormlenie/models/models.py
  addons/kormlenie/security/ir.model.access.csv
Please, commit your changes or stash them before you can merge.

Для исправления нужно сбросить как не нужные локальные изменения
git reset --hard
а затем уже обновить git pull


Инструкция: https://github.com/andreiled/mipt-cs-4sem/wiki/%D0%9F%D0%BE%D1%88%D0%B0%D0%B3%D0%BE%D0%B2%D0%B0%D1%8F-%D0%B8%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%86%D0%B8%D1%8F-%D0%BF%D0%BE-%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%B5-%D1%81-git-%D0%B8-github-%D0%B4%D0%BB%D1%8F-%D1%81%D1%82%D1%83%D0%B4%D0%B5%D0%BD%D1%82%D0%BE%D0%B2


use domain =[('field1_date','&lt;',date1)]
for > use &gt;
    < use &lt;
   <= use &lt;=
   >= use &gt;=
   Если нужно приверить значение на Null тогда использовать = False

List of Domain operators: ! (Not), | (Or), & (And)

	List of Term operators: '=', '!=', '<=', '<', '>', '>=', '=?', '=like', '=ilike', 'like', 'not like', 'ilike', 'not ilike', 'in', 'not in', 'child_of'
	'child_of': parent_id = '1' #Agrolait 'child_of': [('partner_id', 'child_of', parent_id)] - return left and right list of partner_id for given parent_id



Уникальное значение для поля "name"
_sql_constraints = [
						    ('name_unique', 'unique(name)', u'Такая физиологическая группа уже существует!')
						]




Если не отображаются свойства css при формировании отчета, например table-bordered не выводит линии и т.п, то необходимо в режиме debug зайти в Настройки - Структура БД - Вложения
Найти web_editor.assets_editor.js и удалить его

Если не помогла смотрим ошибки в логах:
2017-07-20 17:12:47,917 10155 INFO db openerp.addons.base.ir.ir_attachment: _read_file reading /var/lib/odoo/.local/share/Odoo/filestore/evikaagro/7d/7d7ddab2ebe
efedcf8be9e6b4fa5663529e619de
Выполняем в БД:
delete FROM "public"."ir_attachment" WHERE "public"."ir_attachment"."store_fname" LIKE '%efedcf8be9e6b4fa5663529e619de%'




@api.depends('line_ids.value')
def _compute_total(self):
    for record in self:
        record.total = sum(line.value for line in record.line_ids)





Добавления нулей перед
>>> str(333).rjust(10, ‘0’)
‘0000000333’



##########################################################
##############  ПРО API СЕРВЕР #################################



#####   ЗАПУСК Python как сервиса   #########

sudo apt-get install supervisor

Создать файл /etc/supervisor/conf.d/server-api.conf
[program:server-api]
command = python2.7 /home/smv/odoo-selhoz/server-api/server.py
autorestart = true
stderr_logfile = /var/log/server-api.err.log
stdout_logfile = /dev/null

Обновить конфигурацию
sudo service supervisor reload
sudo service supervisor restart

Запуск скрипта сервиса
sudo supervisorctl start server-api



##########  Настройка API сервера ######################

Переименовать файл "config (копия).py"  в "config.py"
Изменить в файле параметры подключения к базам.



##############  ПРО API СЕРВЕР #################################
################################################################






Reserved field names
A few field names are reserved to be used by the ORM:
•  id is an automatic number uniquely identifying each record, and used as the
database primary key. It's automatically added to every model.
The following fields are automatically created on new models, unless the _log_
access=False model attribute is set:
• 
• 
• 
• 
create_uid for the user that created the record
create_date for the date and time when the record is created
write_uid for the last user to modify the record
write_date for the last date and time when the record was modified
This information is available from the web client, using the Developer Mode menu
and selecting the View Metadata option.
There some built-in effects that expect specific field names. We should avoid using
them for purposes other than the intended ones. Some of them are even reserved and
can't be used for other purposes at all:
•  name is used by default as the display name for the record. Usually it is a
Char , but other field types are also allowed. It can be overridden by setting
the _rec_name model attribute.
[ 77 ]Models – Structuring the Application Data
•  active (type Boolean ) allows inactivating records. Records with
active==False will automatically be excluded from queries. To access them
an ('active','=',False) condition must be added to the search domain,
or 'active_test': False should be added to the current context.
•  sequence (type Integer ) if present in a list view, allows to manually
define the order of the records. To work properly it should also be in the
model's _order .
•  state (type Selection ) represents basic states of the record's life cycle, and
can be used by the state's field attribute to dynamically modify the view:
some form fields can be made read only, required or invisible in specific
record states.
•  parent_id , parent_left , and parent_right have special meaning for
parent/child hierarchical relations. We will shortly discuss them in detail.
So far we've discussed scalar value fields. But a good part of an application data
structure is about describing the relationships between entities. Let's look at that now.




DATE
To facilitate conversion between formats, both fields.Date and fields.Datetime
objects provide these functions:
•  from_string(value) : This converts a string into a date or datetime object.
•  to_string(value) : This converts a date or datetime object into a string in
the format expected by the server.


####################################################################3
###       PgAdmin 4  #############################33
ЗАпуск
перейти в папку установки cd pgadmin4/
source bin/activate
python lib/python2.7/site-packages/pgadmin4/pgAdmin4.py
################################################################