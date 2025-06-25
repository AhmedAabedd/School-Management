# -*- coding: utf-8 -*-
from odoo import fields, api, models,_
from dateutil.relativedelta import relativedelta
import datetime
import re
from odoo.exceptions import ValidationError
from datetime import datetime


class SchoolParent(models.Model):
    _name = "school.parent"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "School Parent"
    _rec_name = "parent_name"

    
    is_second_responsible = fields.Boolean(string="Is second responsible", default=False)
    parent_name = fields.Char(string="Name", required=0)
    reference = fields.Char(string="Reference", required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    civility_id = fields.Many2one('responsible.civility', string="Civility")
    phone = fields.Char(string="Phone Number", required=0)
    mail = fields.Char(string="Email")
    job_id = fields.Many2one('responsible.job', string="Job")
    establishment = fields.Char(string="Establishment")
    personnal_adress = fields.Char(string="Personnal Adress")
    nationality_id = fields.Many2one("res.country", string="Nationality")
    city_id = fields.Many2one("res.country.state", string="City")
    zip = fields.Char(string="Zip")
    street = fields.Char(string="Street")
    work_adress = fields.Char(string="Work Adress")
    family_situation_id = fields.Many2one('school.familysituation', string="Family Situation")
    note = fields.Text(string='Description')
    #children_ids = fields.One2many('school.student', 'responsible_id', string="Childrens Lines")

    #second_responsible_ids = fields.One2many('school.secondresponsible', 'main_responsible_id', string="Second Responsible")

    sale_order_ids = fields.One2many(
        'school.sale.order',
        'parent_id',
        domain="[('parent_id', '=', id)]"
    )
    sale_order_count = fields.Integer(string="Sale Order", compute="_compute_sale_order_count")
    



    ########################################################################################
    #Computed One2many field for main Children (li teba3 lparent)
    main_children_ids = fields.One2many(
        'school.student',
        compute='_compute_main_children',
        string="All Children"
    )
    #Computed One2many field for secondry Children (li teba3 lsecond responsible)
    second_children_ids = fields.One2many(
        'school.student',
        compute='_compute_second_children',
        string="All Children"
    )
    
    @api.depends('is_second_responsible')
    def _compute_main_children(self):
        for parent in self:
            parent.main_children_ids = self.env['school.student'].search([('responsible_id', '=', parent.id)])
            
    
    @api.depends('is_second_responsible')
    def _compute_second_children(self):
        for parent in self:
            parent.second_children_ids = self.env['school.student'].search([('second_responsible_ids', 'in', [parent.id])])
    ########################################################################################



    
    #Sequence auto generate
    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('school.parent.sequence') or _('New')
        res = super(SchoolParent , self).create(vals)
        return res
    
    #def create_other_responsibles(self):
    #    print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")


    #Affect True to is_second_responsible when record added from second responsible action
    @api.model
    def default_get(self, fields_list):
        defaults = super(SchoolParent, self).default_get(fields_list)
        if self.env.context.get('from_second_responsible'):
            defaults['is_second_responsible'] = True
        return defaults
    
    def _compute_sale_order_count(self):
        for rec in self:
            rec.sale_order_count = self.env['school.sale.order'].search_count([('parent_id', '=', rec.id)])


###########################  CONSTRAINS ##############################################################

    #Check phone number format
    @api.constrains('phone')
    def _check_mail_format(self):
        for parent in self:
            if parent.phone:
                if not re.match(r'^[1-9]\d{7}$', parent.phone):
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

    #calling default "create" action of school sale order model
    def action_create_sale_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Sale Order',
            'res_model': 'school.sale.order',
            'view_mode': 'form',
            'target': 'new', #to open in wizard
            'context': {
                'default_parent_id': self.id,
                'default_from_parent_form': True,
            }
        }
    
    def action_view_sale_order(self):
       return {
            'type': 'ir.actions.act_window',
            'name': 'View Sale Order',
            'res_model': 'school.sale.order',
            'view_mode': 'tree,form',
            'target': 'current', #to open in new view
            'domain': [('parent_id', '=', self.id)],
            'context': {
                'default_parent_id': self.id,
                'default_from_parent_form': True
            }
        }
