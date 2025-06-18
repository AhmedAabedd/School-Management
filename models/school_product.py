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
            ('kit', 'Robotics Kit'),
            ('book','Book')
        ], string='Product Type'
    )
    unit_price = fields.Float(string="Unit Price")
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)
    
    available_qty = fields.Integer(string="Available Quantity")
    state = fields.Selection([
            ('available', 'Available'),
            ('out_of_stock', 'Out of stock')
        ], string="status",
           compute="_compute_state",
           default='available',
           store=True
    )


    ##################################################################

    stock_warning = fields.Boolean(string="warning", compute="_compute_stock_warning", store=True)

    #Change state depending on available quantity
    @api.depends('available_qty')
    def _compute_stock_warning(self):
        for rec in self:
            if rec.available_qty > 0 and rec.available_qty <= 10:
                rec.stock_warning = True
            else :
                rec.stock_warning = False

    ##################################################################

    

    #Change state depending on available quantity
    @api.depends('available_qty')
    def _compute_state(self):
        for product in self:
            #print("///////////////////////") if state attr store=true , this function get triggered only using depends
            if product.available_qty > 0:
                product.state = 'available'
            else :
                product.state = 'out_of_stock'
    
    #Raise Error when available quantity < 0
    @api.constrains('available_qty','unit_price')
    def _check_negative_quantity(self):
        for rec in self:
            if rec.available_qty < 0:
                raise ValidationError(_("Available quantity cannot be negative !"))
    
    #Raise Error when price is < 0
    @api.constrains('unit_price')
    def _check_negative_price(self):
        for rec in self:
            if rec.unit_price < 0:
                raise ValidationError(_("Price cannot be negative !"))
            
    #Warning when changing state to Out of Stock
    @api.onchange('state')
    def _check_state_outOfStock(self):
        if self.state == 'out_of_stock' and self.name:
            msg = "This product (" + self.name + ") is now out of stock !"
            return {
                'warning': {
                    'title': "Stock Alert",
                    'message': msg
                }
            }
    

    ################## TRASH ############################################

    #inserting product_type when creaing new product
    #@api.model
    #def default_get(self, fields_list):
        #defaults = super(SchoolProduct, self).default_get(fields_list)
        #if self.env.context.get('from_product_product'):
            #defaults['product_type'] = 'product'
        #elif self.env.context.get('from_product_program'):
            #defaults['product_type'] = 'program'
        #return defaults
    #note : api.model tekhdem ki tenzel aala create

    #show_quantity_state_fields = fields.Boolean(
    #    compute='_compute_show_quantity_state_fields',
    #    string="Show Quantity Fields"
    #)
    #@api.depends('product_type')
    #def _compute_show_quantity_state_fields(self):
    #    for product in self:
    #        product.show_quantity_state_fields = product.product_type == 'product'
