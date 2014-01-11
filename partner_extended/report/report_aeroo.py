from report import report_sxw
from datetime import datetime
import tools

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
		'date':self.formatDate,
        })
	self.context = context
    def formatDate(self, date):
		lst = str(date).split('-')
		return lst[2]+'/'+lst[1]+'/'+lst[0]
