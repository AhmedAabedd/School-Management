# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from dateutil.relativedelta import relativedelta
import datetime
import re
from odoo.exceptions import ValidationError
from datetime import datetime

class SchoolSaleOrder(models.Model):
    _name = "school.sale.order"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Product Sale Order"


    name = fields.Char(string="Ref", required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    parent_id = fields.Many2one('school.parent', string='Parent name', required=True,
                                domain="[('is_second_responsible', '=', False)]")
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], default='draft', string="Status", tracking=True)

    untaxed_total = fields.Float(string="Untaxed Amount", compute="_compute_untaxed_total", store=True)
    taxes_total = fields.Float(string="Taxes", compute="_compute_taxes_total")
    amount_total = fields.Float(string="Total", compute="_compute_amount_total", store=1)

    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)

    order_line_ids = fields.One2many(
        'school.saleorderline',
        'sale_order_id'
    )

    invoice_count = fields.Integer(string="Invoices", compute="_compute_invoice_count")

    ################ TO CHECK SALE ORDER CREATION ORIGIN (from parent or sale order itself)  #########################################

    from_parent_form = fields.Boolean(string="From Parent Form", readonly=True)

    #def _compute_from_parent_form(self):
        #for rec in self:
            #rec.from_parent_form = bool(self.env.context.get('from_parent_form'))


    ####################### STATE ACTIONS ############################################

    def action_confirm(self):
        for rec in self:
            for line in rec.order_line_ids:
                if line.quantity > line.product_id.available_qty:
                    raise ValidationError(_(f"Not enough stock for ({line.product_id.name})!"))
                line.product_id.available_qty -= line.quantity
                line.aux = line.quantity
            rec.state = 'confirmed'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'
    
    def action_cancel(self):
        for rec in self:
            for line in self.order_line_ids:
                line.product_id.available_qty += line.aux
                line.aux = 0
            
            invoices = self.env['school.invoice'].search([('sale_order_id', '=', rec.id)])
            for invoice in invoices:
                invoice.state = 'cancelled'

            rec.state = 'cancelled'

    ##########################################################################################
    
    #Generate auto sequence(name)
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('school.sale.order.sequence') or _('New')
        res = super(SchoolSaleOrder , self).create(vals)
        return res
    
    @api.depends('order_line_ids.total')
    def _compute_untaxed_total(self):
        for rec in self:
            rec.untaxed_total = sum(line.total for line in rec.order_line_ids)
    
    def _compute_taxes_total(self):
        for rec in self:
            rec.taxes_total = 0.0
            for line in rec.order_line_ids:
                rec.taxes_total += line.taxes_amount
    
    @api.depends('untaxed_total', 'taxes_total')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = rec.untaxed_total + rec.taxes_total

    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = self.env['school.invoice'].search_count([('sale_order_id', '=', rec.id)])

    def action_view_invoice(self):
        self.ensure_one()
        if self.invoice_count == 0:
            raise ValidationError(_("No invoices created for this sale order !"))
        return{
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'school.invoice',
            'domain': [('sale_order_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target':'current',
            'context': {}
        }

    def action_create_invoice(self):
        invoice_lines = []
        for line in self.order_line_ids:
            invoice_lines.append((0, 0, {
                'product_type': line.product_type,
                'product_id': line.product_id.id,
                'unit_price': line.unit_price,
                'quantity': line.quantity,
                'total': line.total
            }))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Invoice',
            'res_model': 'school.invoice',
            'view_mode': 'form',
            'target': 'current',#to open in form
            'context': {
                'default_sale_order_id': self.id,
                'default_parent_id': self.parent_id.id,
                'default_currency_id': self.currency_id.id,
                'default_untaxed_amount': self.untaxed_total,
                'default_taxes_amount': self.taxes_total,
                'default_invoice_line_ids': invoice_lines,
            }
        }







class SaleOrderLine(models.Model):
    _name = "school.saleorderline"


    sale_order_id = fields.Many2one('school.sale.order', string='Sale Order', required=True)
    product_type = fields.Selection([
            ('kit', 'Robotics Kit'),
            ('book','Book')
        ], string='Product Type'
    )
    product_id = fields.Many2one('school.product', string='Product name', required=True,
                              domain="[('product_type', '=', product_type)]")
    
    unit_price = fields.Float(related='product_id.unit_price', store=True)
    taxes_id = fields.Many2many('account.tax', related="product_id.taxes_id")

    quantity = fields.Integer(string="Quantity", default=0)
    total = fields.Float(string="Subtotal", compute="_compute_line_total", store=True)

    taxes_amount = fields.Float(string="Taxes Amount", compute="_compute_taxes_amount", store=1)

    currency_id = fields.Many2one(related='sale_order_id.currency_id', string="Currency", store=True)

    aux = fields.Integer(string='Aux', default=0)




    @api.onchange('product_type')
    def _reset_product_name(self):
        for rec in self:
            rec.product_id = ''

    @api.depends('unit_price', 'quantity')
    def _compute_line_total(self):
        for rec in self:
            rec.total = rec.unit_price * rec.quantity
    
    @api.depends('total', 'taxes_id')
    def _compute_taxes_amount(self):
        for rec in self:
            rec.taxes_amount = 0.0
            for tax in rec.taxes_id:
                if tax.amount_type == 'fixed':
                    rec.taxes_amount += tax.amount
                elif tax.amount_type == 'percent':
                    rec.taxes_amount += (tax.amount * rec.total) / 100

    #Warning when selecting invalid quantity
    @api.onchange('quantity')
    def _check_selected_quantity(self):
        for rec in self:
            if rec.quantity > rec.product_id.available_qty and rec.sale_order_id.state == 'confirmed':
                raise ValidationError(_(f"Not enough stock for ({rec.product_id.name})"))
            if rec.quantity > rec.product_id.available_qty:
                return {
                    'warning': {
                        'title': "Stock Alert",
                        'message': f"The quantity selected ({rec.quantity}) exceeds available stock ({rec.product_id.available_qty})."
                    }
                }

    #disallowing deleting records when sale order is confirmed
    def unlink(self):
        for rec in self:
            if rec.sale_order_id.state == "confirmed":
                raise ValidationError(_("You cannot delete order line when sale order is confirmed!"))
            return super(SaleOrderLine, self).unlink()
    
