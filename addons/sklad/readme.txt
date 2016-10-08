sudo su - odoo -s /bin/bash
openerp-server --addons-path=/home/smv/odoo/addons
--auto-reload

Формулы

Если счетчик есть
Натура = Счетчик * (1+Плотность/1000)

Если линейка
Натура = по таблице значений

Коэффициент = Жир*0,5/3,4 + Белок*0,5/3

Яачетный вес = Натура * Коэффициент

////////////////////////////////////////////
Преобразования текста в число
=VALUE("{{line.ves_zachet}}")
////////////////////////////////////////////

Утилизация, На выпойку телятам, Остоток молока (см и кг), Пересдал (см и кг)

Валовый надой = Реализованно + Утил + На выпойку + Остаток - Пересдал

Пересдал идет на следующий день


////////////////////////////////////////////
Для импорта Реализации молока из М13
DELETE FROM milk_sale_milk
  WHERE create_date<'18.07.2016';
copy milk_sale_milk(create_uid,	write_uid, create_date,	write_date, date_doc, name, partner_id, 
amount_ves_natura, amount_ves_zachet, avg_jir, avg_belok, avg_plotnost) 
FROM '/home/smv/Загрузки/М13.csv' DELIMITER ',' CSV HEADER
//////////////////////////////////////////////////////////////