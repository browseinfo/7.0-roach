import time
from openerp.report import report_sxw
class sale_dipesh(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(sale_dipesh, self).__init__(cr, uid, name, context=context)
        self.line_no = 1
        self.index = 0
        self.localcontext.update({
            'time': time,
            'cur_page': self.cur_page,
            'total_page': self.total_page,
            'set_index':self.set_index,
        })
    def cur_page(self):
        self.line_no += 1
        return self.line_no
    def set_index(self):
        self.index +=1
        return self.index
    def total_page(self, order):
        self.total = 1
        for no in order.order_line:
            self.total += 1
        return self.total
report_sxw.report_sxw('report.sale.order.dipesh1', 'sale.order', '7.0-dipesh/partner_extended/report/report_rml.rml', parser=sale_dipesh, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
