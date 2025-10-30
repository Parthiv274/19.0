from odoo import fields,api,models
from datetime import date
import base64


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    responsible_user_ids = fields.Many2many('res.users', string="Responsible Users")
    
    @api.model
    def cron_send_daily_sale_line_update_report(self):
        today = date.today()
        SaleOrderLineUpdateLog = self.env['sale.order.line.update.log']
        Wizard = self.env['sale.order.line.report.wizard']

        logs = SaleOrderLineUpdateLog.search([('change_date', '>=', today)])
        if not logs:
            return

        companies = logs.mapped('sale_order_id.company_id')


        for company in companies:
            wizard = Wizard.create({
                'company_id': company.id,
                'start_date': today,
                'end_date': today,
            })

            # attachment = wizard._generate_pdf_attachment()
            attachment = wizard.action_print_pdf_report()
            

            users = company.responsible_user_ids
            emails = [user.email for user in users if user.email]

            if not emails:
                continue

            valid_emails = ",".join(emails)

            template = self.env.ref('scs_priceList_extended.mail_template_sale_order_line_report_responsibles')

            # template.sudo().send_mail(wizard.id,force_send=True,email_values={'email_to': valid_emails,'attachment_ids': [(6, 0, [attachment.id])],})

            # template.sudo().send_mail(
            #     wizard.id,
            #     force_send=True,
            #     email_values={
            #         'email_to': valid_emails,
            #         'attachment_ids': [(6, 0, [attachment.id])]
            #     }
            # )
            # template.sudo().send_mail(self.id,force_send=True,email_values={'email_to': valid_emails,'attachment_ids': [(6, 0, [attachment.id])]})
            template.sudo().send_mail(wizard.id,force_send=True,email_values={'email_to': valid_emails, 'attachment_ids':[(6,0,[attachment.id])]})


        return True
