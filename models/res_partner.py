from odoo import models, fields, api, _




class ResPartner(models.Model):
    _inherit = "res.partner"




    is_school_parent = fields.Boolean(string="School Parent")
    is_second_responsible = fields.Boolean(string="Second Responsible")