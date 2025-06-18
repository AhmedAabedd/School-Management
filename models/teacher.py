# -*- coding: utf-8 -*-
from odoo import fields, api, models,_
from dateutil.relativedelta import relativedelta
import datetime
import re
from odoo.exceptions import ValidationError
from datetime import datetime


class SchoolTeacher(models.Model):
    _name = "school.teacher"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "School Teacher"
    _rec_name = "teacher_name"

    
    teacher_name = fields.Char(string="Name", required=True)
    reference = fields.Char(string="Reference", required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    birth_date = fields.Date(string="Birth Date")
    age = fields.Integer(string="Age", compute="_compute_age", store=True)
    gender = fields.Selection([("male","Male"),("female","Female")], default="male", string="Gender", required=1)
    phone = fields.Char(string="Phone Number", required=True)
    mail = fields.Char(string="Email")
    delegation_date = fields.Date(string="Delegation Date")
    teaching_subjects = fields.Many2many("school.subject", string="Teaching Subjects")
    nationality_id = fields.Many2one("res.country", string="Nationality")
    note = fields.Text(string='Description')

    school_history_ids = fields.One2many('school.history', 'teacher_id', string="School History")


    #teacher_history_ids = fields.One2many('teacher.history', 'teacher_id', string="Teacher History")



    @api.depends('birth_date')
    def _compute_age(self):
        today = datetime.today()
        for rec in self:
            if rec.birth_date:
                delta = today.year - rec.birth_date.year - ((today.month, today.day) < (rec.birth_date.month, rec.birth_date.day))
                rec.age = delta
    


    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('school.teacher.sequence') or _('New')
        res = super(SchoolTeacher , self).create(vals)
        return res
    
###########################  CONSTRAINS ##############################################################

    #Check phone number format
    @api.constrains('phone')
    def _check_phone_format(self):
        for teacher in self:
            if teacher.phone:
                if not re.match(r'^[1-9]\d{7}$', teacher.phone):
                    raise ValidationError(_("Please check your phone number format !"))
    
    #Check mail format
    @api.constrains('mail')
    def _check_mail_format(self):
        for teacher in self:
            if teacher.mail:
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', teacher.mail):
                    raise ValidationError(_("Please check your Email format !"))
                
    #Check age not nagative or null
    @api.constrains('age')
    def _check_age_negative(self):
        for teacher in self:
            if teacher.age <= 0:
                raise ValidationError(_("Age cannot be negative or null !"))

########################################################################################################