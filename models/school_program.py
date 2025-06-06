# -*- coding: utf-8 -*-
from odoo import fields, api, models,_
from dateutil.relativedelta import relativedelta
import datetime
import re
from odoo.exceptions import ValidationError
from datetime import datetime

class SchoolProgram(models.Model):
    _name = "school.program"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "School Program"
    


    name = fields.Char(string="Name", required=True)
    reference = fields.Char(string="Reference", required=True)
    image = fields.Binary(string="Program Image")

    subject_id = fields.Many2one('school.subject', string="Subject")

    unit_price = fields.Float(string="Price")
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)
    
    duration_hours = fields.Float(string="Total hours")
    duration_weeks = fields.Integer(string="Total weeks")
    total_sessions = fields.Integer(string="Number of sessions")