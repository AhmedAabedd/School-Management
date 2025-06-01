# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SchoolSubject(models.Model):
    _name = "school.subject"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "School Subject"


    name = fields.Char(string="Name", required=True)