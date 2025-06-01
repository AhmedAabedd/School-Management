# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ResponsibleJob(models.Model):
    _name = "responsible.job"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Responsible Job"


    name = fields.Char(string="Name", required=True)
    #date = fields.Date(default=fields.Date.today, string="DAAAAAAAAATE")