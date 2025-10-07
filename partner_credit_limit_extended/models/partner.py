from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    overdue_days = fields.Integer(string="Block Overdue Days>")
    overdue_percentage = fields.Float(string="Block Overdue invoice %>")
    check_overdue = fields.Boolean(default=True)    