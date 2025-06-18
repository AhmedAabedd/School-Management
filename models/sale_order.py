# -*- coding: utf-8 -*-
from odoo import fields, api, models,_
from dateutil.relativedelta import relativedelta
import datetime
import re
from odoo.exceptions import ValidationError
from datetime import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    mounir = fields.Char(string="fffff")