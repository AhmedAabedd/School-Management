# -*- coding: utf-8 -*-
from odoo import fields, api, models,_
from dateutil.relativedelta import relativedelta
import datetime
import re
from odoo.exceptions import ValidationError
from datetime import datetime

class SchoolProduct(models.Model):
    _name = "school.product"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "School Product"
    

    #Basic Infos
    name = fields.Char(string="Name", required=True)
    reference = fields.Char(string="Reference", required=True)
    image = fields.Binary(string="Product Photo")
    product_type = fields.Selection([
            ('program', 'Program'),
            ('item', 'Item'),
        ], string='Type', required=True
    )
    unit_price = fields.Float(string="Price (DT)")
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)
    
    #For Program
    program_category_id = fields.Many2one('school.subject', string="Category")
    #program_categorys = fields.Selection([('robotic', 'Robotics'),('python', 'Python'),('scratch', 'Scratch')], string='Category')
    duration_hours = fields.Float(string="Total hours")
    duration_weeks = fields.Integer(string="Total weeks")
    total_sessions = fields.Integer(string="Number of sessions")

    #For Items
    item_type = fields.Selection([
            ('kit', 'Robotics Kit'),
            ('book','Book')
        ], string='Item Type'
    )
    quantity = fields.Integer(string="Available Quantity")
    state = fields.Selection([
            ('available', 'Available'),
            ('out_of_stock', 'Out of stock')
        ], string="status",
           compute="_compute_state",
           default='available',
           store=True
    )




    #selecting automatically product_type when creaing new product
    @api.model
    def default_get(self, fields_list):
        defaults = super(SchoolProduct, self).default_get(fields_list)
        if self.env.context.get('from_product_item'):
            defaults['product_type'] = 'item'
        elif self.env.context.get('from_product_program'):
            defaults['product_type'] = 'program'
        return defaults
    
    #Change state depending on quantity
    @api.depends('quantity')
    def _compute_state(self):
        for product in self:
            if product.quantity > 0:
                product.state = 'available'
            else :
                product.state = 'out_of_stock'
    
    #Raise Error when quantity < 0
    @api.constrains('quantity','unit_price')
    def _check_quantity(self):
        for product in self:
            if product.quantity < 0:
                raise ValidationError("Available quantity cannot be negative !")
    
    #Raise Error when price is < 0
    @api.constrains('unit_price')
    def _check_price(self):
        for product in self:
            if product.unit_price < 0:
                raise ValidationError(_("Price cannot be negative !"))
            
    #Warning when changing state to Out of Stock
    @api.onchange('quantity')
    def _onchange_quantity(self):
        if self.quantity == 0 and self.name:
            msg = "This product (" + self.name + ") is now out of stock !"
            return {
                'warning': {
                    'title': "Stock Alert",
                    'message': msg
                }
            }
    

    #show_quantity_state_fields = fields.Boolean(
    #    compute='_compute_show_quantity_state_fields',
    #    string="Show Quantity Fields"
    #)
    #@api.depends('product_type')
    #def _compute_show_quantity_state_fields(self):
    #    for product in self:
    #        product.show_quantity_state_fields = product.product_type == 'item'
