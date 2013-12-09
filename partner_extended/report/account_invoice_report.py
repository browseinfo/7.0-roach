from report import report_sxw
from datetime import datetime
import tools

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
		'display_address':self.display_address        
        })
	self.context = context
    def display_address(self, partner_id):
    	country = self.pool.get('res.country').read(self.cr, self.uid, partner_id.id, ['name'])['name']
    	address = (partner_id.name or "") + " " +(partner_id.street or "") + " " + (partner_id.street2 or "") + " " + (partner_id.city or "") + " " + (partner_id.state_id or "") + " " + (partner_id.zip or "") + country or ""
    	return address
