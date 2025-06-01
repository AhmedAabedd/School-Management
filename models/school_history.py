# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SchoolHistory(models.Model):
    _name = "school.history"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "School History"


    #name = fields.Char(string="Name", required=True)
    
    #General Fields
    refers_to = fields.Selection([
            ('student', 'Student'),
            ('teacher', 'Teacher')
        ], string="Refers to", readonly=True
    )
    school_year_id = fields.Many2one('school.year', string="School Year")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], required=False, default='draft')
    notes = fields.Text(string="Notes")

    #Student Fields
    student_id = fields.Many2one('school.student', string="Student Name", readonly=True)
    level_id = fields.Many2one('school.level', string="Level")
    class_id = fields.Many2one('school.classe', string="Class")
    annual_average = fields.Float(string="Annual Average")
    rank = fields.Integer(string="Rank")
    certificate_id = fields.Char(string="Certificate")

    #teacher Fields
    teacher_id = fields.Many2one('school.teacher', string="Teacher Name", readonly=True)
    #subject_ids = fields.Many2many(
    #    'school.subject', 
    #    'history_subject_rel',  # relation table name
    #    'history_id',           # field referring to this model
    #    'subject_id',           # field referring to related model
    #    string="Subjects Taught"
    #)
    subject_ids = fields.Many2many('school.subject', string="Subjects")
    teaching_hours = fields.Float(string="Instructional Hours")


    @api.model
    def default_get(self, fields_list):
        defaults = super(SchoolHistory, self).default_get(fields_list)
        
        # Auto-detect if created from teacher or student
        if self.env.context.get('is_student_action'):
            defaults['refers_to'] = 'student'
            defaults['teacher_id'] = self.env.context.get('active_id')
        elif self.env.context.get('is_teacher_action'):
            defaults['refers_to'] = 'teacher'
            defaults['student_id'] = self.env.context.get('active_id')
        return defaults
    