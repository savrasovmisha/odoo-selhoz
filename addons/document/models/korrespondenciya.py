# -*- coding: utf-8 -*-

from __future__ import division #при делении будет возвращаться float
from openerp import models, fields, api, exceptions, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
