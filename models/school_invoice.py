# -*- coding: utf-8 -*-
from odoo import fields, api, models,_
from dateutil.relativedelta import relativedelta
import datetime
import re
from odoo.exceptions import ValidationError
from datetime import datetime

class SchoolInvoice(models.Model):
    _name = "school.invoice"



    name = fields.Char(string="Reference", required=1, default=lambda self: _('New'))
    parent_id = fields.Many2one('school.parent', string="Customer", required=1, domain="[('is_second_responsible', '=', False)]")
    payment_date = fields.Date()
    due_date = fields.Date()
    currency_id = fields.Many2one('res.currency', string="Currency")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('notpaid', 'Not Paid'),
    ], default='draft')

    tax_id = fields.Many2one('account.tax', string="Taxes", required=1)
    tax_amount = fields.Float(related="tax_id.amount", string="Taxes")

    untaxed_amount = fields.Float(string="Untaxed Amount")
    amount_total = fields.Float(string="Total", compute="_compute_amount_total", store=1)

    invoice_line_ids = fields.One2many('school.invoice.line', 'invoice_id', string="Order Lines")




    #Generate auto sequence(name)
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('school.invoice.sequence') or _('New')
        res = super(SchoolInvoice,self).create(vals)
        return res

    @api.depends('tax_id', 'untaxed_amount')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = rec.untaxed_amount + rec.tax_id.amount
    







class InvoiceLine(models.Model):
    _name = "school.invoice.line"


    #sale_order_id = fields.Many2one('school.sale.order', string='Sale Order', required=True)
    invoice_id = fields.Many2one('school.invoice')
    product_type = fields.Selection([
            ('kit', 'Robotics Kit'),
            ('book','Book')
        ], string='Product Type'
    )
    product_id = fields.Many2one('school.product', string='Product name', required=True,
                              domain="[('product_type', '=', product_type)]")
    
    unit_price = fields.Float(related='product_id.unit_price', store=True)

    quantity = fields.Integer(string="Quantity", default=0)
    total = fields.Float(string="Subtotal")
    currency_id = fields.Many2one(related='invoice_id.currency_id', string="Currency", store=True)