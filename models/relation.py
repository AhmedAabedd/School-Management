# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ResponsibleRelation(models.Model):
    _name = "responsible.relation"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Responsible Relation"


    name = fields.Char(string="Name", required=True)