# -*- coding: utf-8 -*-
from odoo import fields, api, models,_
from dateutil.relativedelta import relativedelta
import datetime
import re
from odoo.exceptions import ValidationError
from datetime import datetime

class SchoolEnrollment(models.Model):
    _name = "school.enrollment"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Program Enrollment"


    name = fields.Char(string="Reference", required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    parent_id = fields.Many2one('school.parent', string='Parent name', required=True)
    subject_id = fields.Many2one('school.subject', string="Subject")
    program_id = fields.Many2one('school.program', string='Program name', required=True,
                              domain="[('subject_id', '=', subject_id)]")
    
    total_hours = fields.Float(related='program_id.duration_hours', string="Hours", store=True)
    total_sessions = fields.Integer(related='program_id.total_sessions', string="Sessions", store=True)
    price = fields.Float(related='program_id.unit_price', store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
    ], default='draft', string="Status", tracking=True)






    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_paid(self):
        for rec in self:
            rec.state = 'paid'
    