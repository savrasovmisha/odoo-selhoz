--Замена значений NULL на 0
update korm_korm_detail_line 
set kol_fakt = 0
where kol_fakt is NULL;