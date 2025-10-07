from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()

        for order in self:
            partner = order.partner_id

            if partner.check_overdue and partner.overdue_days > 0 and not partner.over_credit:
                overdue_limit_date = date.today() - timedelta(days=partner.overdue_days)
                overdue_invoices = self.env['account.move'].search([
                    ('partner_id', '=', partner.id),
                    ('move_type', '=', 'out_invoice'),
                    ('payment_state', 'in', ['not_paid', 'partial']),
                    ('invoice_date_due', '!=', False),
                    ('invoice_date_due', '<', overdue_limit_date),
                ])
                if overdue_invoices:
                    msg = "You cannot confirm the Sale Order.\n\n"
                    for inv in overdue_invoices:
                        msg += "Customer '%s' has overdue invoice '%s'. Due date: %s.\n" % (
                            partner.name, inv.name, inv.invoice_date_due.strftime("%d-%b-%Y")
                        )
                    msg += "\nPlease clear old dues before confirming new orders."
                    raise ValidationError(msg)

            if partner.check_overdue and partner.overdue_percentage > 0 and not partner.over_credit:
                invoices = self.env['account.move'].search([
                    ('partner_id', '=', partner.id),
                    ('move_type', '=', 'out_invoice'),
                    ('invoice_date_due', '!=', False),
                    ('state', '=', 'posted'),
                    ('invoice_date', '<', fields.Date.today()),
                ])
                total_invoiced = sum(invoices.mapped('amount_total'))
                overdue_invoices = invoices.filtered(lambda inv: inv.payment_state in ['not_paid', 'partial'])
                total_overdue = sum(overdue_invoices.mapped('amount_residual'))

                if total_invoiced > 0:
                    overdue_percentage = (total_overdue / total_invoiced) * 100
                    if overdue_percentage > partner.overdue_percentage:
                        msg = _(
                            "You cannot confirm the Sale Order.\n\n"
                            "%s has overdue invoices.\n"
                            "Total Invoiced: %.2f\n"
                            "Total Overdue: %.2f\n"
                            "Overdue Percentage: %.2f%% (Allowed: %s%%)\n\n"
                            "Please pay the previous invoices before confirming new orders."
                        ) % (
                            partner.name,
                            total_invoiced,
                            total_overdue,
                            overdue_percentage,
                            partner.overdue_percentage
                        )
                        raise ValidationError(msg)

        return res
