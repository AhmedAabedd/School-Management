# -*- coding: utf-8 -*-
from odoo import fields, api, models,_
from dateutil.relativedelta import relativedelta
import datetime
import re
from odoo.exceptions import ValidationError
from datetime import datetime


class SchoolTest(models.Model):
    _name = "school.test"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "School Test"


    formation_id = fields.Many2one('school.subject', string="Subject")
    group_id = fields.Many2one(
        'school.group',
        string="Group",
        domain="[('subject_id', '=', formation_id)]"
    )
    date = fields.Date(string="Date")
    max_score = fields.Float(string="Max Score")

    total_students = fields.Integer(string="Total Students", compute="_compute_total_students", store=True)
    total_passed = fields.Integer(string="Total Passed", compute="_compute_total_passed", store=True)
    total_failed = fields.Integer(string="Total Failed", compute="_compute_total_failed", store=True)

    high_score = fields.Float(string="Highest", compute="_compute_score_stats", store=True)
    low_score = fields.Float(string="Lowest", compute="_compute_score_stats", store=True)
    avg_score = fields.Float(string="Average", compute="_compute_score_stats", store=True)

    result_ids = fields.One2many(
        'test.result',
        'test_id'
    )
    



    #Clear the field group when formation changes
    @api.onchange('formation_id')
    def _onchange_formation_id(self):
        self.group_id = False
    
    #Calculating student stats
    @api.depends('result_ids')
    def _compute_total_students(self):
        for test in self:
            test.total_students = len(test.result_ids)

    @api.depends('result_ids.score')
    def _compute_total_passed(self):
        for test in self:
            count = 0
            for result in test.result_ids:
                if result.score >= test.max_score / 2:
                    count += 1
            test.total_passed = count

    @api.depends('result_ids.score')
    def _compute_total_failed(self):
        for test in self:
            count = 0
            for result in test.result_ids:
                if result.score < test.max_score / 2:
                    count += 1
            test.total_failed = count

    #Calculating score stats
    @api.depends('result_ids.score')
    def _compute_score_stats(self):
        for test in self:
            scores = test.result_ids.mapped('score')
            if scores:
                test.high_score = max(scores)
                test.low_score = min(scores)
                test.avg_score = sum(scores) / len(scores)
            else:
                test.high_score = 0.0
                test.low_score = 0.0
                test.avg_score = 0.0


    @api.onchange('group_id')
    def _onchange_group_id(self):
        if not self.group_id:
            # Clear existing lines
            self.result_ids = [(5, 0, 0)]

        elif self.group_id:
            # Clear existing lines
            self.result_ids = [(5, 0, 0)]
            
            # Get all students in this group
            students = self.env['school.student'].search([('group_id', '=', self.group_id.id)])#students contain Students IDs
            
            # Create result lines instances
            for student in students:
                self.result_ids = [(0, 0, {'student_id': student.id})]







class TestResult(models.Model):
    _name = "test.result"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Test Result"

    test_id = fields.Many2one('school.test', string="Test name")
    student_id = fields.Many2one('school.student', string="Student name")
    score = fields.Float(string="Score")
    rank = fields.Integer(string="Rank")


################# Constrains ############################
    @api.onchange('score')
    def _check_score(self):
        for result in self:
            if result.score < 0 or result.score > result.test_id.max_score:
                raise ValidationError(
                    _("Score must be between 0 and %(max)s for %(student)s !") % {
                        'max': result.test_id.max_score,
                        'student': result.student_id.student_name
                    }
                )
    
    @api.constrains('rank')
    def _check_rank(self):
        for result in self:
            if result.rank < 0:
                raise ValidationError(
                    _("Rank must be positive for %(student)s !") % {
                        'student': result.student_id
                    }
                )