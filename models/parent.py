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

    
    partner_id = fields.Many2one('res.partner', delegate=1, required=True, ondelete='cascade')
    is_second_responsible = fields.Boolean(string="Is second responsible", default=False)
    #parent_name -> name
    reference = fields.Char(string="Ref", required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    #civility_id -> title
    #phone
    #mail -> email
    job_id = fields.Many2one('responsible.job', string="Job")
    establishment = fields.Char(string="Establishment")
    personnal_adress = fields.Char(string="Personnal Adress")
    #nationality_id -> country_id
    #city_id -> state_id
    #zip
    #street
    work_adress = fields.Char(string="Work Adress")
    family_situation_id = fields.Many2one('school.familysituation', string="Family Situation")
    #note -> comment


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
        string="All Children",
        compute='_compute_main_children',
    )
    #Computed One2many field for secondry Children (li teba3 lsecond responsible)
    second_children_ids = fields.One2many(
        'school.student',
        compute='_compute_second_children',
        string="All Children"
    )
    
    @api.depends('is_second_responsible')
    def _compute_main_children(self):
        for rec in self:
            rec.main_children_ids = self.env['school.student'].search([('responsible_id', '=', rec.id)])
            
    
    @api.depends('is_second_responsible')
    def _compute_second_children(self):
        for rec in self:
            rec.second_children_ids = self.env['school.student'].search([('second_responsible_ids', 'in', [rec.id])])
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
    def _check_phone_format(self):
        for rec in self:
            if rec.phone:
                if not re.match(r'^[1-9]\d{7}$', rec.phone):
                    raise ValidationError(_("Please check your phone number format !"))
    
    #Check email format
    @api.constrains('email')
    def _check_email_format(self):
        for rec in self:
            if rec.email:
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', rec.email):
                    raise ValidationError(_("Please check your Email format !"))
                
    #Check age not nagative or null
    @api.constrains('age')
    def _check_age_negative(self):
        for rec in self:
            if rec.age <= 0:
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
    
    ################ INHERITED METHODS ####################################################

    def action_view_partner_invoices(self):
        if self.partner_id:
            action = self.partner_id.action_view_partner_invoices()
            if action and isinstance(action, dict):
                context = dict(action.get('context') or {})
                context.update({'default_partner_id': self.partner_id.id})
                action['context'] = context
            return action

    def action_view_sale_order(self):
        if self.partner_id:
            action = self.partner_id.action_view_sale_order()
            if action and isinstance(action, dict):
                context = dict(action.get('context') or {})
                context.update({'default_partner_id': self.partner_id.id})
                action['context'] = context
            return action
