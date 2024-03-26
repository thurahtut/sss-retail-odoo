from odoo import api, fields, models, _

from . import sale_margin_report

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def _run_wkhtmltopdf(
            self,
            bodies,
            report_ref=False,
            header=None,
            footer=None,
            landscape=False,
            specific_paperformat_args=None,
            set_viewport_size=False):
        if sale_margin_report.CONTEXT and sale_margin_report.CONTEXT.get('sale_margin_report', False):
            res = super()._run_wkhtmltopdf(bodies,report_ref,header,footer,sale_margin_report.CONTEXT.get('landscape'),specific_paperformat_args,set_viewport_size)
        else:
            res = super()._run_wkhtmltopdf(bodies,report_ref,header,footer,landscape,specific_paperformat_args,set_viewport_size)

        return res