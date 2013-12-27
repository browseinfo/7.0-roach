import time
from openerp.report import report_sxw
class account(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(account, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })
report_sxw.report_sxw('report.sale.order.dipesh', 'account.invoice', '7.0-roach/partner_extended/report/account_invoice_extend.rml', parser=account, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

