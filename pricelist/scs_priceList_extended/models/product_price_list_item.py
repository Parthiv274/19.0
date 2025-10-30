from odoo import models, api,fields

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'
    # _inherit = 'product.pricelist'



    def write(self, vals):
        for record in self:
            old_price = record.fixed_price
            old_qty = record.min_quantity

        res = super(ProductPricelistItem, self).write(vals)

        for record in self:
            new_price = record.fixed_price
            new_qty = record.min_quantity

            if old_price != new_price or old_qty != new_qty:
                self.env['pricelist.update.log'].create({
                    'pricelist_id': record.pricelist_id.id,
                    'product_id': record.product_id.id if record.product_id else record.product_tmpl_id.product_variant_id.id,
                    'old_price': old_price,
                    'new_price': new_price,
                    'old_min_qty': old_qty,
                    'new_min_qty': new_qty,
                    'company_id': record.company_id.id,
                })
        return res


    def action_view_update_logs(self):
        self.ensure_one()
        product_id = self.product_id.id or self.product_tmpl_id.product_variant_id.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Price List Updates',
            'view_mode': 'list',
            # 'res_model': 'pricelist.update.log',
            'res_model': 'pricelist.update.log',
            'domain': [('product_id', '=', product_id)],
            'context': {'default_product_id': product_id},
            'target': 'current',  
        }
