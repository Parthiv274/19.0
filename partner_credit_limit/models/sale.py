
from odoo import _, api, models,fields
from odoo.exceptions import UserError, ValidationError
import logging
from datetime import date,timedelta 


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def check_limit(self): 
        self.ensure_one() 
        moveline_obj = self.env['account.move.line'] 
        partner = self.partner_id 
        user_id = self.env['res.users'].search([ \
            ('partner_id', '=', partner.id)], limit=1)
        if user_id and not user_id.has_group('base.group_portal') or not user_id:
            movelines = moveline_obj.search([
                ('partner_id', '=', partner.id),
                ('account_id.account_type', 'in', ['asset_receivable', 'liability_payable']),
                ('move_id.state', '!=', 'cancel')
            ])
            confirm_sale_order = self.search(
                [('partner_id', '=', partner.id),
                 ('state', '=', 'sale'),
                 ('invoice_status', '!=', 'invoiced')])



            amount_total = sum(confirm_sale_order.mapped('amount_total'))
            credit = sum(movelines.mapped('credit'))
            debit = sum(movelines.mapped('debit'))

            
            partner_credit_limit = (debit + amount_total) - credit
            remaining_credit_limit = max(0, round(partner.credit_limit - partner_credit_limit, 2))

            if partner_credit_limit > partner.credit_limit and partner.credit_limit > 0.0:
                over_limit = max(0, round(partner_credit_limit - partner.credit_limit, 2))
                msg = _(
                    "You cannot confirm the Sale Order.\n"
                    "Your total credit limit is: {cust_credit_limit}\n"
                    "Your total overdue or due amount including this order is: {due_amt}\n"
                    "Your Remaining Credit Limit including this order is: {remaining_credit_limit}\n"
                    "Customer Name: {customer}\n\n"
                    "Please check your credit limits and complete the payment of your due invoices before confirming new orders.\n\n"
                ).format(
                    over=over_limit,
                    cust_credit_limit=partner.credit_limit,
                    due_amt=partner_credit_limit,
                    remaining_credit_limit=remaining_credit_limit,
                    customer=self.partner_id.name
                )
                raise ValidationError(msg)
            
                
        # return True
        
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.partner_id.credit_limit > 0.0 and not order.partner_id.over_credit:
                order.check_limit()
        return res

    @api.constrains('amount_total')
    def check_amount(self):
        for order in self:
            if order.partner_id.credit_limit > 0.0 and not order.partner_id.over_credit:
                order.check_limit()


    @api.model_create_multi
    def create(self, vals_list):
        res = super(SaleOrder, self).create(vals_list)
        if res.partner_id.credit_limit > 0.0 and not res.partner_id.over_credit:
            res.check_limit()
        return res
    

           
                
                
                
                
                
                




            
        





