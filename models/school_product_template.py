# -*- coding: utf-8 -*-
from odoo import fields, api, models,_
from dateutil.relativedelta import relativedelta
import datetime
import re
from odoo.exceptions import ValidationError
from datetime import datetime

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    

    #name
    #reference ---> default_code
    #image ---> image_1920
    is_school_product  = fields.Boolean(string="Is school product")
    school_product_type = fields.Selection([
            ('kit', 'Robotics Kit'),
            ('book','Book')
        ], string='Product Type'
    )
    #unit_price ---> list_price
    #description ---> description_sale
    #active
    
    #available_qty ---> qty_available
    state = fields.Selection([
            ('available', 'Available'),
            ('out_of_stock', 'Out of stock')
        ], string="status",
           compute="",
           default='available',
           store=True
    )


    ##################################################################

    stock_warning = fields.Boolean(string="warning", compute="_compute_stock_warning", store=True)

    #Change state depending on available quantity
    @api.depends('qty_available')
    def _compute_stock_warning(self):
        for rec in self:
            if rec.qty_available > 0 and rec.qty_available <= 10:
                rec.stock_warning = True
            else :
                rec.stock_warning = False

    ##################################################################


    #Affect True to is_school_product when opened from school menu
    @api.model
    def default_get(self, fields_list):
        defaults = super(ProductTemplate, self).default_get(fields_list)
        if self.env.context.get('from_school_menu'):
            defaults['is_school_product'] = True
            defaults['detailed_type'] = 'product'
        return defaults

    #Change state depending on available quantity
    @api.depends('qty_available')
    def _compute_state(self):
        for rec in self:
            if rec.qty_available > 0:
                rec.state = 'available'
            else :
                rec.state = 'out_of_stock'
    
    #Raise Error when available quantity < 0
    @api.constrains('qty_available','list_price')
    def _check_negative_quantity(self):
        for rec in self:
            if rec.qty_available < 0:
                raise ValidationError(_("Available quantity cannot be negative !"))
    
    #Raise Error when price is < 0
    @api.constrains('list_price')
    def _check_negative_price(self):
        for rec in self:
            if rec.list_price < 0:
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