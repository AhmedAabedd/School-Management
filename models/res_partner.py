from odoo import models, fields, api, _




class ResPartner(models.Model):
    _inherit = "res.partner"




    is_school_parent = fields.Boolean(string="School Parent")
    is_second_responsible = fields.Boolean(string="Second Responsible")

    reference = fields.Char(string="Ref", required=True, copy=False, default=lambda self: _('New'))
    
    job_id = fields.Many2one('responsible.job', string="Job")
    establishment = fields.Char(string="Establishment")
    personnal_adress = fields.Char(string="Personnal Adress")

    work_adress = fields.Char(string="Work Adress")
    family_situation_id = fields.Many2one('school.familysituation', string="Family Situation")

    children_count = fields.Integer(compute="_compute_children_count")
    invoices_count = fields.Integer(compute="_compute_invoices_count")

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
            rec.main_children_ids = self.env['school.student'].search([('parent_id', '=', rec.id)])
            
    
    @api.depends('is_second_responsible')
    def _compute_second_children(self):
        for rec in self:
            rec.second_children_ids = self.env['school.student'].search([('second_responsible_ids', 'in', [rec.id])])



    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('school.partner.sequence') or _('New')
        res = super().create(vals)
        return res

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if self.env.context.get('from_parent_menu'):
            defaults["is_school_parent"] = True
        return defaults
    
    def _compute_children_count(self):
        for rec in self:
            rec.children_count = self.env['school.student'].search_count([('parent_id', '=', self.id)])

    def _compute_invoices_count(self):
        for rec in self:
            rec.invoices_count = self.env['account.move'].search_count([('partner_id', '=', rec.id)])

    def action_view_children(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'View Children',
            'res_model': 'school.student',
            'view_mode': 'tree,form',
            'target': 'current', #to open in new view
            'domain': [('parent_id', '=', self.id)],
            'context': {
                'default_parent_id': self.id,
            }
        }

    def action_view_parent_invoices(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'View Invoices',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'target': 'current', #to open in new view
            'domain': [('partner_id', '=', self.id), ('move_type', '=', 'out_invoice')],
            'context': {
                'default_partner_id': self.id,
                'default_move_type': 'out_invoice',  # <-- This is critical
            }
        }