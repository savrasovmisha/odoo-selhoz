Небольшая шпаргалка по git.

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




Файлы измененные с момента последнего коммита, т.е. текущие изменения, можно вывести командой


git status
1
git status
Вы увидите два списка изменений — файлы, которые добавлены в commit и список unstaged changes (файлов, что в последующий коммит не войдут).

Как посмотреть список файлы, измененных в каком либо прошлом обновлении проекта? Здесь пригодится команда log со специальным флагом:


git log --name-only
1
git log --name-only
Кроме commit message в логе будут показаны списки обновленных файлов.