# odoo-selhoz
Odoo для сельскохозяйственного предприятия


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