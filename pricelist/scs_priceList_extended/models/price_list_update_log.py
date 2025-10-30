from odoo import fields,api,models
from datetime import datetime

class PriceListUpdateLog(models.Model):

    _name = "pricelist.update.log"
    _description = "Price List Update Log"
    _order = 'update_date desc'
    _rec_name = 'product_id'



    company_id = fields.Many2one('res.company',string='Company',required=True,default=lambda self: self.env.company)
    pricelist_id = fields.Many2one('product.pricelist', string="Price List")
    product_id = fields.Many2one('product.product', string="Product")
    old_price = fields.Float(string="Old Price")
    new_price = fields.Float(string="New Price")
    old_min_qty = fields.Float(string="Old Min Qty")
    new_min_qty = fields.Float(string="New MIn Qty")
    update_date = fields.Datetime(string='Update Date', default=lambda self: fields.Datetime.now())
    updated_by = fields.Many2one('res.users', string='Updated By', default=lambda self: self.env.user)


