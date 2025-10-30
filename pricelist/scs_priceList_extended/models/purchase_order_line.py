from odoo import fields,api,models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    hsn_code = fields.Char(string="HSN Code")
    