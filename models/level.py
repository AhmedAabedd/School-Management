# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SchoolLevel(models.Model):
    _name = "school.level"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "School Level"


    name = fields.Char(string="Name", required=True)
    academic_year_id = fields.Many2one('school.year', string="School Year")