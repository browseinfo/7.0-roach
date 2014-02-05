import time
from openerp.report import report_sxw
class account_webkit(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(account_webkit, self).__init__(cr, uid, name, context=context)
        self.page_total = 0.0
        self.record_len = 0.0
        self.localcontext.update({
            'time': time,
            'get_page_break' : self.get_page_break,
            'set_page_total' : self.set_page_total,
            'get_page_total' : self.get_page_total,
            'get_page_header' : self.get_page_header,
            'get_partner_name': self.get_partner_name,
            'get_vat': self.get_vat
        })
        
    def get_page_header(self):
        if self.record_len % 7.0 == 0.0:
            return True
        return False

    def get_page_break(self):
        if self.record_len == 0.0:
            return False
        elif self.record_len % 7.0 == 0.0:
            return True
        return False
    
    def set_page_total(self, subtotal):
        self.page_total += subtotal
        self.record_len += 1
    
    def get_page_total(self):
        return str(self.page_total)

    def get_partner_name(self, partner_id):
        if partner_id.is_company:
            return partner_id.name
        else:
            return partner_id.parent_id.name
    def get_vat(self, vat):
        if not vat:
            vat = ''
        else:
            length = len(vat)
            vat = vat[2:length]
        return vat
    
report_sxw.report_sxw('report.account.invoice.webkit', 'account.invoice', '7.0-roach/partner_extended/report/account_invoice_extend_webkit_tmpl.mako', parser=account_webkit, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

