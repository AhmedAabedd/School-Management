# -*- coding: utf-8 -*-
from odoo import fields, api, models,_
from dateutil.relativedelta import relativedelta
import datetime
import re
from odoo.exceptions import ValidationError
from datetime import datetime

class SchoolSaleOrder(models.Model):
    _name = "school.saleorder"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Item Sale Order"


    name = fields.Char(string="Reference", required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    parent_id = fields.Many2one('school.parent', string='Parent name', required=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
    ], default='draft', string="Status", tracking=True)

    amount_total = fields.Float(
        string="Total",
        compute="_compute_amount_total",
        store=True
    )

    order_lines_ids = fields.One2many(
        'school.saleorderline',
        'sale_order_id'
    )




    #Generate auto sequence(name)
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('school.saleorder.sequence') or _('New')
        res = super(SchoolSaleOrder , self).create(vals)
        return res

    def action_confirm(self):
        for rec in self:
            #if rec.item_id.quantity < rec.quantity:
                #raise ValidationError("Not enough stock!")
            #rec.item_id.quantity -= rec.quantity
            #rec.state = 'confirmed'
            for line in rec.order_lines_ids:
                if line.quantity > line.item_id.quantity:
                    raise ValidationError(_("Not enough stock!"))
                line.item_id.quantity -= line.quantity
            rec.state = 'confirmed'

    def action_paid(self):
        for rec in self:
            rec.state = 'paid'
    
    @api.depends('order_lines_ids.total')
    def _compute_amount_total(self):
        for rec in self:
            total = sum(line.total for line in rec.order_lines_ids)
            rec.amount_total = total








class SaleOrderLine(models.Model):
    _name = "school.saleorderline"


    sale_order_id = fields.Many2one('school.saleorder', string='Sale Order', required=True)
    item_type = fields.Selection([
            ('kit', 'Robotics Kit'),
            ('book','Book')
        ], string='Item Type'
    )
    item_id = fields.Many2one('school.product', string='Item', required=True,
                              domain="[('product_type', '=', 'item'), ('item_type', '=', item_type)]")
    
    unit_price = fields.Float(related='item_id.unit_price', store=True)
    #available_quantity = fields.Integer(related='item_id.quantity', store=True)

    quantity = fields.Integer(string="Quantity", default=1)
    total = fields.Float(string="Total (DT)", compute="_compute_line_total", store=True)


    @api.onchange('item_type')
    def _reset_item_name(self):
        for rec in self:
            rec.item_id = ''

    @api.depends('unit_price', 'quantity')
    def _compute_line_total(self):
        for rec in self:
            rec.total = rec.unit_price * rec.quantity

    #Warning when selecting invalid quantity
    @api.onchange('quantity')
    def _check_available_quantity(self):
        for rec in self:
            if rec.quantity > rec.item_id.quantity:
                return {
                    'warning': {
                        'title': "Stock Alert",
                        'message': f"The quantity selected ({rec.quantity}) exceeds available stock ({rec.item_id.quantity})."
                    }
                }

    
