# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from dateutil.relativedelta import relativedelta
import datetime
import re
from odoo.exceptions import ValidationError
from datetime import datetime


class SchoolStudent(models.Model):
    _name = "school.student"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "School Student"
    #_order = 'id desc'
    _rec_name = "student_name"


    
    student_name = fields.Char(string="Name", required=True)
    #display_name = fields.Char(string="full name", compute="_compute_display_name", store=True)
    reference = fields.Char(string="Reference", required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    
    #Status bar
    student_state = fields.Selection([
        ('actif', 'ACTIF'),
        ('out_unpaid', 'OUT/UNPAID'),
        ('out', 'OUT')
        ], default="actif", string="Student state")


    #General information
    gender = fields.Selection([("male","Male"),("female","Female")], default="male", string="Gender", required=True)
    birth_date = fields.Date(string="Birth Date")
    age = fields.Integer(string="Age", compute="compute_age", store=True)
    phone = fields.Char(string="Phone")
    mail = fields.Char(string="Email")
    image = fields.Binary(string="Student Photo")

    responsible_id = fields.Many2one(
        "school.parent",
        string="Responsibe Name",
        domain="[('is_second_responsible', '=', False)]",
        required=True
    )
    #parent_id = fields.Many2one(
        #'res.partner',
        #string="Parent Name",
        #domain="[('is_school_parent', '=', True), ('is_second_responsible', '=', False)]"
    #)

    relation_id = fields.Many2one('responsible.relation', string="Relation")
    
    birth_country_id = fields.Many2one("res.country",string="Birth Country")
    birth_state_id = fields.Many2one("res.country.state",string="Birth State")


    use_responsible_address = fields.Boolean(string="Use Responsible Address", default=False)


    nationality_id = fields.Many2one("res.country", string="Nationality")
    city_id = fields.Many2one("res.country.state", string="City")
    zip = fields.Char(string="Zip")
    street = fields.Char(string="Street")


    #Academic Information
    academic_year_id = fields.Many2one('school.year', string="School Year")
    level_id = fields.Many2one('school.level', string="Level")
    class_id = fields.Many2one('school.classe', string="Class")
    group_id = fields.Many2one('school.group', string="Group")
    admission_date = fields.Date(string="Admission Date")
    maternal_language = fields.Char(string="Maternal Language")
    previous_school = fields.Char(string="Previous School")
    release_date = fields.Date(string="Release Date")


    #Academic career
    school_history_ids = fields.One2many('school.history', 'student_id', string="School History")


    #Skills
    skill = fields.Text(string='Skill (s)', default="Enter student's skills...")


    #Second Responsibles
    second_responsible_ids = fields.Many2many(
        "school.parent",
        string="Second Responsibles",
        domain="[('is_second_responsible','=',True),('id', '!=', responsible_id)]"
    )

    #sec_responsible_ids = fields.Many2many(
        #'res.partner',
        #string="Seconds Responsible",
        #domain="[('is_school_parent', '=', True), ('is_second_responsible','=',True),('id', '!=', responsible_id)]"
    #)

    #second_responsible_ids = fields.Many2many(
    #    "school.parent",                  # Related model (Parent)
    #    "student_parent_rel",            # Relationship table name
    #    "student_id",                    # Field in rel table pointing to student
    #    "parent_id",                     # Field in rel table pointing to parent
    #    string="Second Responsibles",     # UI label
    #    domain="[('is_second_responsible','=',True),('id', '!=', responsible_id)]"
    #)




    #second responsible
    #second_responsible_id = fields.Many2one(
    #    'school.parent',
    #    string='second responsible',
    #    domain="[('is_second_responsible','=',True),('id', '!=', responsible_id)]"
    #)



    #Assinging responsible Address to student Address infos
    @api.onchange('responsible_id','use_responsible_address')
    def onchange_use_responsible_address(self):
        if self.responsible_id and self.use_responsible_address:
            self.nationality_id = self.responsible_id.country_id.id
            self.city_id = self.responsible_id.state_id.id
            self.zip = self.responsible_id.zip
            self.street = self.responsible_id.street
        else:
            self.nationality_id = ''
            self.city_id = ''
            self.zip = ''
            self.street = ''
    
    #Age auto calculating
    @api.onchange('birth_date')
    def compute_age(self):
        today = datetime.today()
        for rec in self:
            if rec.birth_date:
                delta = today.year - rec.birth_date.year - ((today.month, today.day) < (rec.birth_date.month, rec.birth_date.day))
                rec.age = delta

    @api.model
    def create(self, vals):
        #assign default note if it's empty
        if not vals.get('skill') or vals.get('skill') == "Enter student's skills...":
            vals['skill'] = 'Have no skills  :('
        #create reference
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('school.student.sequence') or _('New')
        res = super(SchoolStudent , self).create(vals)
        return res
    

################################ Constrains ############################################

    #Check phone format
    @api.constrains('phone')
    def _check_phone_format(self):
        for rec in self:
            if rec.phone:
                if not re.match(r'^[1-9]\d{7}$', rec.phone):
                    raise ValidationError(_("Please check your phone number format !"))

    #Check mail format
    @api.constrains('mail')
    def _check_mail_format(self):
        for rec in self:
            if rec.mail:
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', rec.mail):
                    raise ValidationError(_("Please check your Email format !"))

    #Check age not negative or null
    @api.constrains('age')
    def _check_age_negative(self):
        for rec in self:
            if rec.age <= 0:
                raise ValidationError(_("Age cannot be negative or null !"))
            
##########################################################################################