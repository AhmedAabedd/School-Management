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
    sale_order_id = fields.Many2one('school.sale.order', string="Sale Order")
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

    amount_total = fields.Float(string="Total")

    order_line_ids = fields.One2many('school.saleorderline', 'invoice_id', string="Order Lines")




    #Generate auto sequence(name)
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('school.invoice.sequence') or _('New')
        res = super(SchoolInvoice,self).create(vals)
        return res


