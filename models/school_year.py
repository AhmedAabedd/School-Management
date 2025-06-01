# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SchoolYear(models.Model):
    _name = "school.year"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "School Year"


    name = fields.Char(string="Name", required=True)
    start_date= fields.Date(string="Start Date")
    end_date= fields.Date(string="End Date")