# -*- coding: utf-8 -*-
from odoo import fields, api, models,_
from dateutil.relativedelta import relativedelta
import datetime
import re
from odoo.exceptions import ValidationError
from datetime import datetime

class SchoolInvoice(models.Model):
    _inherit = 'account.move'



    #@api.model
    #def default_get(self, fields_list):
    #    defaults = super().default_get(fields_list)
    #    if self.env.context.get('from_parent'):
    #        defaults['partner_id'] = 
    #    return defaults