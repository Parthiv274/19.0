from odoo import fields,api,models
from datetime import datetime

class SaleOrderLineUpdateLog(models.Model):

    _name = "sale.order.line.update.log"
    _description = "Sale Order Line Update Log"
    _order = "change_date desc"
    _rec_name = 'sale_order_line_id'
    


    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    sale_order_line_id = fields.Many2one('sale.order.line', string = "Sale Order Line")
    product_id = fields.Many2one('product.product', string="Product")
    Value_changed = fields.Char(string="Value Changed")
    old_value = fields.Char(string="Old Value")
    new_value = fields.Char(string="New Value")
    changed_by = fields.Many2one('res.users', string="Changed By", default=lambda self:self.env.user)
    change_date = fields.Datetime(string="Change Date", default=lambda self: fields.Datetime.now())
    company_id = fields.Many2one('res.company',string='Company',required=True,default=lambda self: self.env.company)