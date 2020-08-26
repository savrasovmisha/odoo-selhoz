# odoo-selhoz
Odoo для сельскохозяйственного предприятия
Зависимость только от базовых модулей 'base', 'report', 'board'



##Необходимые пакеты
pandas =>16 
xlsxwriter







# API СЕРВЕР
Предназначен для обеспечения загрузки данных из баз Сулекс и ЮниформАгри


## ЗАПУСК Python как сервиса

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



##  Настройка API сервера

Переименовать файл "config (копия).py"  в "config.py"
Изменить в файле параметры подключения к базам.

