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