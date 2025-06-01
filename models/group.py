# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SchoolGroup(models.Model):
    _name = "school.group"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "School Group"


    name = fields.Char(string="Name", required=True)
    subject_id = fields.Many2one('school.subject', string="Subject")