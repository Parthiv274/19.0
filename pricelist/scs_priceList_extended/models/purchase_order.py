from odoo import fields,api,models
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

                
    # def button_confirm(self):
    #     for order in self:
    #         if not order.partner_id.allow_purchase:
    #             raise ValidationError(
    #                 f"Vendor '{order.partner_id.name}' is not allowed to confirm purchase orders."
    #             )
    #     return super(PurchaseOrder, self).button_confirm()


            


    @api.model_create_multi
    def create(self, vals):
        for value in vals:
            partner_id = value.get('partner_id')
            if partner_id:
                partner = self.env['res.partner'].browse(partner_id)
                if not partner.allow_purchase:
                    raise ValidationError(
                        f"You cannot create a Purchase Order for vendor '{partner.name}'"
                        f"because they are not allowed for purchases."
                    )
        return super(PurchaseOrder, self).create(vals)




