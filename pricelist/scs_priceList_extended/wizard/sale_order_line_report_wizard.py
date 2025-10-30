from odoo import fields, api, models, _
from datetime import date
import io
import xlsxwriter
import base64
from odoo.exceptions import ValidationError
import calendar


class SaleOrderLineReportWizard(models.TransientModel):
    _name = 'sale.order.line.report.wizard'
    _description = 'Sale Order Line Report Wizard'

    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)
    start_date = fields.Date(string="Start Date", required=True, default=lambda self: SaleOrderLineReportWizard._get_month_start())
    end_date = fields.Date(string="End Date", required=True, default=lambda self: SaleOrderLineReportWizard._get_month_end())
    sale_order_ids = fields.Many2many('sale.order', string="Sale Orders")

#for default moth start and end date and theie validation error
    def _get_month_start():
        today = date.today()
        return date(today.year, today.month, 1)

    def _get_month_end():
        today = date.today()
        last_day = calendar.monthrange(today.year, today.month)[1]
        return date(today.year, today.month, last_day)

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        today = date.today()
        for wizard in self:
            if wizard.start_date > today:
                raise ValidationError("Start date cannot be in the future.")
            if wizard.end_date < wizard.start_date:
                raise ValidationError("End Date cannot be earlier than Start Date")

#Generate the excel report
    def _generate_excel_attachment(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Sale Order Line Update Report')

        bold = workbook.add_format({'align': 'center', 'bold': True, 'border': 1})
        center_format = workbook.add_format({'align': 'center', 'border': 1})
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss', 'align': 'center', 'border': 1})

        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 25)
        sheet.set_column('C:C', 25)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:G', 25)
        sheet.set_column('H:H', 25)
        sheet.set_column('I:I', 25)

        sheet.write("A1", 'Sale Order', bold)
        sheet.write("B1", 'Order Line', bold)
        sheet.write("C1", 'Product', bold)
        sheet.write("D1", 'Field Changed', bold)
        sheet.write("E1", 'Old Value', bold)
        sheet.write("F1", 'New Value', bold)
        sheet.write("G1", 'Changed By', bold)
        sheet.write("H1", 'Change Date', bold)
        sheet.write("I1", 'Company', bold)

        headers = [
            'Sale Order', 'Order Line', 'Product', 'Field Changed',
            'Old Value', 'New Value', 'Changed By', 'Change Date', 'Company'
        ]
        for col, header in enumerate(headers):
            sheet.write(0, col, header, bold)

        domain = [
            ('change_date', '>=', self.start_date),
            ('change_date', '<=', self.end_date),
            ('sale_order_id.company_id', '=', self.company_id.id),
        ]
        if self.sale_order_ids:
            domain.append(('sale_order_id', 'in', self.sale_order_ids.ids))

        logs = self.env['sale.order.line.update.log'].search(domain)
        row = 1
        for log in logs:
            sheet.write(row, 0, log.sale_order_id.name or '', center_format)
            sheet.write(row, 1, log.sale_order_line_id.display_name or '', center_format)
            sheet.write(row, 2, log.product_id.display_name or '', center_format)
            sheet.write(row, 3, log.Value_changed or '', center_format)
            sheet.write(row, 4, log.old_value or '', center_format)
            sheet.write(row, 5, log.new_value or '', center_format)
            sheet.write(row, 6, log.changed_by.name or '', center_format)
            sheet.write(row, 7, str(log.change_date or ''), date_format)
            sheet.write(row, 8, log.sale_order_id.company_id.name or '', center_format)
            row += 1

        workbook.close()
        output.seek(0)
        file_data = base64.b64encode(output.read())

        attachment = self.env['ir.attachment'].create({
            'name': f'Sale_Order_Line_Update_Report_{self.start_date}_{self.end_date}.xlsx',
            'type': 'binary',
            'datas': file_data,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })
        return attachment

   #send the mail and print excel report in one button.
    def action_send_mail(self):
        self.ensure_one()

        attachment = self._generate_excel_attachment()
        data = base64.b64decode(attachment.datas)


        users = self.company_id.responsible_user_ids
        emails = [user.email for user in users if user.email]
        valid_emails = ",".join(emails)
        if not valid_emails:
            raise ValidationError("No valid email addresses found for responsible users!")
        
        template = self.env.ref('scs_priceList_extended.mail_template_sale_order_line_report_responsibles')
        template.sudo().write({'email_to': valid_emails})


        mail_id = template.sudo().send_mail(self.id, force_send=True, email_values={'email_to': valid_emails,
            'attachment_ids': [(6, 0, [attachment.id])]
        })

        template.sudo().write({'email_to': False})

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'self',
        }


#Added on button of print pdf report.
    def action_print_pdf_report(self):
        self.ensure_one()

        report = self.env.ref('scs_priceList_extended.action_sale_order_line_pdf_report')

        pdf_data, _ = report._render_qweb_pdf('scs_priceList_extended.action_sale_order_line_pdf_report', res_ids=self.ids)

        file_name = f"Sale_Order_Line_Report_{self.start_date}_{self.end_date}.pdf"
        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'type': 'binary',
            'datas': base64.b64encode(pdf_data),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })

        users = self.company_id.responsible_user_ids
        emails = [user.email for user in users if user.email]
        valid_emails = ",".join(emails)
        if not valid_emails:
            raise ValidationError("No valid email addresses found for responsible users!")

        template = self.env.ref('scs_priceList_extended.mail_template_sale_order_line_report_responsibles')
        template.sudo().write({'email_to': valid_emails})
        template.sudo().send_mail(self.id,force_send=True,email_values={'email_to': valid_emails,'attachment_ids': [(6, 0, [attachment.id])]})
        template.sudo().write({'email_to': False})

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }



        # return self.env.ref('scs_priceList_extended.action_sale_order_line_pdf_report').report_action(self)


