# -*- coding: utf-8 -*-
from odoo import fields, api, models,_
from dateutil.relativedelta import relativedelta
import datetime
import re
from odoo.exceptions import ValidationError
from datetime import datetime


class SchoolAttendance(models.Model):
    _name = "school.attendance"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "School Attendance"


    #refers_to = fields.Selection([('student', 'Student'),('teacher', 'Teacher')], string="Refers to", required=True, default='student')
    display_name = fields.Char(string="Attendance Reference", compute="_compute_attendance_name", store=True)
    date = fields.Date(String="Date", default=fields.Date.today, required=True)
    subject_id = fields.Many2one(
        'school.subject',
        string="Subject"
    )
    group_id = fields.Many2one(
        'school.group',
        string="Group",
        domain="[('subject_id', '=', subject_id)]"
    )
    attendance_line_ids = fields.One2many(
        'school.attendance.line',
        'attendance_id',
        string="Student Records",
        store=True
    )


    #Auto display name generate
    @api.depends('date', 'subject_id', 'group_id')
    def _compute_attendance_name(self):
        for attendance in self:
            attendance.display_name = f"{attendance.date} | {attendance.subject_id.name}-{attendance.group_id.name}"

    #Clear the field group when subject changes
    @api.onchange('subject_id')
    def _onchange_subject_id(self):
        self.group_id = False

    @api.onchange('group_id')
    def _onchange_group_id(self):
        # Clear existing lines
        self.attendance_line_ids = [(5, 0, 0)]

        if self.group_id:
            #Auto sign subject when selecting group
            #self.subject_id = self.group_id.subject_id.id
            
            # Get all students in this group
            students = self.env['school.student'].search([
                ('group_id', '=', self.group_id.id)
            ])
            
            # Create attendance lines
            for student in students:
                self.attendance_line_ids = [(0, 0, {
                    'student_id': student.id
                })]





class AttendanceLine(models.Model):
    _name = 'school.attendance.line'
    

    attendance_id = fields.Many2one(
        'school.attendance',
        string="Attendance",
        readonly=True,
        ondelete='cascade'
    )
    student_id = fields.Many2one(
        'school.student',
        string="Name",
    )
    is_present = fields.Boolean(string="Present", default=True)



    #@api.model
    #def default_get(self, fields_list):
        #defaults = super(AttendanceLine, self).default_get(fields_list)
        
        #if self.attendance_id:
            #defaults['attendance_id'] = self.env.context.get("AAAAAAAa")
        #return defaults

    
    