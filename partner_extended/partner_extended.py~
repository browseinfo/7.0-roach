from datetime import datetime, timedelta
import time
import openerp.exceptions
from openerp import netsvc
from openerp import pooler
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare

class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'school': fields.boolean('School'),
        'university': fields.boolean('University'),
        'department_ids': fields.many2many('department.extended','name','description',string='Department'),
        'vat_area': fields.char('VAT Area'),
            }

class department_extended(osv.osv):
    _name = "department.extended"
    _columns = {
        'name': fields.char('Name'),
        'description': fields.char('Description'),
        'active': fields.boolean('Active'),
        'parent_id': fields.many2one('department.extended', 'Parent Department'),
        }

    _defaults = {
        'active': True,
        }

class res_users(osv.osv):
    _inherit = "res.users"
    _columns = {
        'last_name': fields.char('Last Name'),
        }

class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'privacy': fields.selection([('public', 'Public'),('private','Private')], 'Privacy / Visibility', required=True,),
        'shipping_date': fields.date('Shipping Date'),
        'catalog': fields.selection([('with', 'With Catalogue'),('without','Without Catalogue')], 'Catalogue Option', required=True,),
        }

    _defaults = {
        'privacy': 'public',
	'catalog': 'without',
    }

    def print_catalogue(self, cr, uid, ids, context=None):
        datas = {
                 'model': 'sale.order',
                 'ids': ids,
                 'form': self.read(cr, uid, ids[0], context=context),
        }
        return {'type': 'ir.actions.report.xml', 'report_name': 'sale.order.dipesh1', 'datas': datas, 'nodestroy': True}

#    def action_wait(self, cr, uid, ids, context=None):
#        context = context or {}
#        for o in self.browse(cr, uid, ids):
#            if not o.order_line:
#                raise osv.except_osv(_('Error!'),_('You cannot confirm a sales order which has no line.'))
#            noprod = self.test_no_product(cr, uid, o, context)
#            if (o.order_policy == 'manual') or noprod:
#                self.write(cr, uid, [o.id], {'state': 'manual', 'date_confirm': fields.date.context_today(self, cr, uid, context=context),'privacy':'public'})
#            else:
#                self.write(cr, uid, [o.id], {'state': 'progress', 'date_confirm': fields.date.context_today(self, cr, uid, context=context),'privacy':'public'})
 #           self.pool.get('sale.order.line').button_confirm(cr, uid, [x.id for x in o.order_line])
 #       return True
       
    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        inv_vals = super(sale_order, self)._prepare_invoice(cr, uid, order, lines, context=context)
        inv_vals.update({'shipping_date' : order.shipping_date})
        return inv_vals
    
    def create(self, cr, uid, vals, context=None):
         if vals.get('name','/')=='/':
            name = self.pool.get('res.users').browse(cr, uid, [vals['user_id']], context)[0].name
            last_name = self.pool.get('res.users').browse(cr, uid, [vals['user_id']], context)[0].last_name or ""
            dummy, sequence_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'seq_sale_order')
            name = datetime.now().strftime('%Y')+name+last_name
            self.pool.get('ir.sequence').write(cr, uid, [sequence_id], {'prefix': name}, context)
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.order') or '/'
         return super(sale_order, self).create(cr, uid, vals, context=context)
     
class account_invoice(osv.osv):
    _inherit = "account.invoice"
    _columns = {
        'shipping_date': fields.date('Shipping Date'),
        'account_invoice_create': fields.date('Invoice Creation Date'),
        }

    _defaults = {
        'account_invoice_create': lambda *a: time.strftime('%Y-%m-%d')
    }

class mail_compose_message(osv.TransientModel):
    _inherit = "mail.compose.message"
    
    def default_get(self, cr, uid, fields, context=None):
         res = super(mail_compose_message, self).default_get(cr, uid, fields, context=context)
         res.update({'template_id': 7})
         return res
    
