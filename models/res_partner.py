# -*- coding: utf-8 -*-
from odoo import fields, api, models,_
from dateutil.relativedelta import relativedelta
import datetime
import re
from odoo.exceptions import ValidationError
from datetime import datetime


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_school_parent = fields.Boolean(string="Is School Parent")
    is_second_responsible = fields.Boolean(string="Is Second Responsible")

class SchoolResPartner(models.Model):
    _name = 'school.res.partner'



    partner_id = fields.Many2one('res.partner', delegate=1, required=True, ondelete='cascade')

    is_school_parent = fields.Boolean(string="Is School Parent")
    is_second_responsible = fields.Boolean(string="Is Second Responsible")

    establishment = fields.Char(string="Establishment")
    reference = fields.Char(string="Ref", required=True, copy=False, default=lambda self: _('New'))
    family_situation_id = fields.Many2one('school.familysituation')
    
    
    



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
        for rec in self:
            rec.main_children_ids = self.env['school.student'].search([('parent_id', '=', rec.id)])
            
    @api.depends('is_second_responsible')
    def _compute_second_children(self):
        for rec in self:
            rec.second_children_ids = self.env['school.student'].search([('sec_responsible_ids', 'in', [rec.id])])
    ########################################################################################


    # Initialisation of some fields depending on is_school_parent and is_second_responsible
    @api.model
    def create(self, vals):
        res = super(SchoolResPartner,self).create(vals)
        
        res.is_school_parent == True
        res.company_type == 'individual'
        res.is_second_responsible == True
        
        return res



    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if self.env.context.get('from_school_menu'):
            defaults['is_school_parent'] = True
            defaults['company_type'] = 'individual'
            if self.env.context.get('from_second_responsible'):
                defaults['is_second_responsible'] = True
        return defaults
    
    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('school.partner.sequence') or _('New')
        res = super(ResPartner , self).create(vals)
        return res









