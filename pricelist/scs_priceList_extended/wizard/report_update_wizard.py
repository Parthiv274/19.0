from odoo import fields,api,models
from datetime import date
import io
import xlsxwriter
import base64


class ReportUpdateWizard(models.TransientModel):
    _name = 'report.update.wizard'
    _description = 'Report Update Wizard'


    company_id = fields.Many2one('res.company', string="Company", required=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    pricelist_ids = fields.Many2many('product.pricelist', string="Pricelists")


    def action_generate_report(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Price List Update Report')

        bold = workbook.add_format({'align':'center','bold': True})
        center_format = workbook.add_format({'align': 'center'})
        

        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E',20)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 20)




        sheet.set_row(0, 20)
        sheet.set_row(1, 20)
        sheet.set_row(2, 20)
        sheet.set_row(3, 20)
        sheet.set_row(4, 20)
        sheet.set_row(5, 20)
        sheet.set_row(6, 20)
        sheet.set_row(7,20)

        sheet.write("A1", 'Product Name', bold)
        sheet.write("B1", 'Old Price', bold)
        sheet.write("C1", 'New Price', bold)
        sheet.write("D1", 'Old Min Qty', bold)
        sheet.write("E1", 'New Min Qty', bold)
        sheet.write("F1", 'Update Date', bold)
        sheet.write("G1", 'Pricelist', bold)
        sheet.write("H1", 'Company', bold)


        
        domain = [
            ('write_date', '>=', self.start_date),
            ('write_date', '<=', self.end_date),
            ('pricelist_id.company_id', '=', self.company_id.id),
        ]
        if self.pricelist_ids:
            domain.append(('pricelist_id', 'in', self.pricelist_ids.ids))

        items = self.env['pricelist.update.log'].search(domain)
        row = 1
        for item in items:
            sheet.write(row, 0, item.product_id.name or '', center_format)
            sheet.write(row, 1, item.old_price or 0.0, center_format)
            sheet.write(row, 2, item.new_price  or 0.0, center_format)
            sheet.write(row, 3, item.old_min_qty or 0.0, center_format)
            sheet.write(row, 4, item.new_min_qty or 0.0, center_format)
            sheet.write(row, 5, str(item.create_date))
            sheet.write(row, 6, item.pricelist_id.name or '', center_format)
            sheet.write(row, 7 , item.company_id.name or '', center_format)
            row += 1

        workbook.close()
        output.seek(0)

        file_data = base64.b64encode(output.read())
        attachment = self.env['ir.attachment'].create({
            'name': 'Update_report.xlsx',
            'type': 'binary',
            'datas': file_data,
            'res_model': 'report.update.wizard',
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }



