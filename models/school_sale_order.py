# -*- coding: utf-8 -*-
from odoo import fields, api, models,_
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

    amount_total = fields.Float(string="Total", compute="_compute_amount_total", store=True)

    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)

    order_line_ids = fields.One2many(
        'school.saleorderline',
        'sale_order_id'
    )

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
    def _compute_amount_total(self):
        for rec in self:
            total = sum(line.total for line in rec.order_line_ids)
            rec.amount_total = total
    
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
                'default_parent_id': self.parent_id.id,
                'default_currency_id': self.currency_id.id,
                'default_untaxed_amount': self.amount_total,
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

    quantity = fields.Integer(string="Quantity", default=0)
    total = fields.Float(string="Subtotal", compute="_compute_line_total", store=True)
    currency_id = fields.Many2one(related='sale_order_id.currency_id', string="Currency", store=True)
    invoice_id = fields.Many2one('school.invoice', readonly=1)

    aux = fields.Integer(string='Aux', default=0)




    @api.onchange('product_type')
    def _reset_product_name(self):
        for rec in self:
            rec.product_id = ''

    @api.depends('unit_price', 'quantity')
    def _compute_line_total(self):
        for rec in self:
            rec.total = rec.unit_price * rec.quantity

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
    
