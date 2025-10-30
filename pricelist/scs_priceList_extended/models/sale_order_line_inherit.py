from odoo import fields,api,models

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"


    def write(self,vals):
        for record in self:
            old_qty = record.product_uom_qty
            old_price = record.price_unit

        res = super(SaleOrderLine,self).write(vals)

        for record in self:
            new_qty = record.product_uom_qty
            new_price = record.price_unit

            if old_qty != new_qty:
                self.env['sale.order.line.update.log'].create({          
                    'sale_order_id': record.order_id.id,
                    'sale_order_line_id': record.id,
                    'product_id': record.product_id.id,
                    'Value_changed': 'Quantity',
                    'old_value': old_qty,
                    'new_value': new_qty,
                })

            if old_price != new_price:
                self.env['sale.order.line.update.log'].create({
                    'sale_order_id': record.order_id.id,
                    'sale_order_line_id': record.id,
                    'product_id': record.product_id.id,
                    'Value_changed': 'Unit_price',
                    'old_value': old_price,
                    'new_value': new_price,
                })                         
            


    def action_view_update_logs(self):
        self.ensure_one()
        return{
            'type': 'ir.actions.act_window',
            'name': 'Sale Order Line Updates',
            'view_mode': 'list',
            'res_model': 'sale.order.line.update.log',
            'domain': [('sale_order_line_id', '=', self.id)],
            'target': 'current',
        }
    