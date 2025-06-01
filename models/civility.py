# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ResponsibleCivility(models.Model):
    _name = "responsible.civility"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Responsible Civility"


    name = fields.Char(string="Name", required=True)