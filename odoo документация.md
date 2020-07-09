odoo doc



####################################################################

inverse - применяется когда необходимо изменить значение которое расчитывется автоматически через метод compute 

Напимер

ed_izm_id = fields.Many2one('nomen.ed_izm', string=u"Ед.изм.", compute='_get_ed_izm', inverse='_set_ed_izm',  store=True)

def _get_ed_izm(self):
    for record in self:
        if record.nomen_nomen_id:
            self.ed_izm_id = self.nomen_nomen_id.ed_izm_id


def _set_ed_izm(self):
    for record in self:
        if not record.ed_izm_id: continue
        


#########################################################################