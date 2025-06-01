# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SchoolClasse(models.Model):
    _name = "school.classe"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "School Classe"


    name = fields.Char(string="Name", required=True)
    level_id = fields.Many2one('school.level', string="Level")