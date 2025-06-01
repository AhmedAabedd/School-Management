# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SchoolFamilySituation(models.Model):
    _name = "school.familysituation"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "School Family Situation"


    name = fields.Char(string="Name", required=True)