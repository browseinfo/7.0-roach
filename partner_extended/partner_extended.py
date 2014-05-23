from datetime import datetime, timedelta
import time
import base64
from xml.etree import ElementTree
import openerp.exceptions
from openerp import netsvc
from openerp import pooler
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from dateutil.relativedelta import relativedelta
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

    def do_run_scheduler_stock(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
        """Scheduler for Task reminder
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user's ID for security checks,
        @param ids: List of calendar alarm's IDs.
        @param use_new_cursor: False or the dbname
        @param context: A standard dictionary for contextual values
        """
        if context is None:
            context = {}
        mail_mail = self.pool.get('mail.mail')
        attach_obj = self.pool.get('ir.attachment')
        product_obj = self.pool.get('product.product')
        move_obj = self.pool.get('stock.move')
        warehouse_obj = self.pool.get('stock.warehouse')
        product_uom_obj = self.pool.get('product.uom')
        line_ids = []
        mail_to = ""
        mail_ids = []  
        date = ""
        admin_email = self.pool.get('res.users').browse(cr, uid, [1])[0].email
        today = time.strftime('%Y-%m-%d')

        
        last_5th_date = datetime.strptime(today, '%Y-%m-%d') - relativedelta(days=5)
        last_date =  last_5th_date.strftime('%Y-%m-%d')

        incoming_qty = 0.0
        warehouse_ids = warehouse_obj.search(cr, uid, [], context=context)        
        for loc in warehouse_obj.browse(cr, uid, warehouse_ids, context=context):
            stock_location = loc.lot_stock_id.id   
            incoming_ids = move_obj.search(cr, uid, [('location_id','in', [stock_location]),('state', '=', 'done')])
            print "incoming ids",incoming_ids
            if incoming_ids:
                real = 0.0
                incoming_qty = ''
                for move in move_obj.browse(cr, uid, incoming_ids):
                    real += move.product_id.qty_available
                    incoming_qty += move.product_id.name + ',' + str(move.product_qty) + '\n'
                    date = move.date
        print "las_date=",last_date,"date=",date
        if last_date < date:
            

            product_ids = product_obj.search(cr, uid, [], context=context)
            if product_ids:
                display = ''
                for product in product_obj.browse(cr, uid, product_ids, context=context):
                    display += product.name + ',' + str(product.qty_available) + '\n'
                    mail_to = admin_email
            if admin_email:
                sub = '[Stock Of the Product]'
            
                body = """
                Hello ,
                
                Please see the current stock of today which is as follow,  
                \n %s'
                
                
                And we have delivered the following product on last 5 days
                
                
                \n %s""" % (display,incoming_qty)
				# following code is for creating xls file for the prodct name and stock
				#@@@@@@@@@@@@@@@@@
                import xlwt

                wb = xlwt.Workbook()
                ws = wb.add_sheet('Prodct Qty Info')

                ws.write(0, 0, 'Product')
                ws.write(0, 1, 'Qty')
                ws.write(1, 0, display)
                ws.write(1, 1, incoming_qty)
                wb.save('/home/aanad/workspace/7.0-roach/partner_extended/Product_stock_info.xls')
                attach_id = attach_obj.create(cr, uid, {'name':'Incoming stock Details','datas_fname':'Product_stock_info.xls','datas':('Product_stock_info.xls').encode('base64')})
                print "attch id",attach_id
    			#@@@@@@@@@@@@@@@@@
                if mail_to:
                    vals = {
                            'state': 'outgoing',
                            'subject': sub,
                            'body_html': body,
                            'email_to': mail_to,
                            'email_from': admin_email,
                        }
                    
                    mail_ids.append(mail_mail.create(cr, uid, vals, context=context))
                    print "\n\n***",mail_ids
                    mail_mail.write(cr, uid, mail_ids, {'attachment_ids': [(6,0,[attach_id])]}, context=context)
                    mail_mail.send(cr, uid, mail_ids, auto_commit=True, context=context)
        return True

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
            name = self.pool.get('res.users').browse(cr, uid, [vals['user_id']], context)[0].name[:1]
	 if vals.get('last_name','/')=='/':
	    last_name = self.pool.get('res.users').browse(cr, uid, [vals['user_id']], context)[0].last_name and self.pool.get('res.users').browse(cr, uid, [vals['user_id']], context)[0].last_name[:2] or ""
            dummy, sequence_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'seq_sale_order')
            name = datetime.now().strftime('%Y')+name+last_name
            self.pool.get('ir.sequence').write(cr, uid, [sequence_id], {'prefix': name}, context)
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.order') or '/'
         return super(sale_order, self).create(cr, uid, vals, context=context)

    def action_quotation_send(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'sale', 'email_template_edi_sale')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        ctx.update({
            'default_model': 'sale.order',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
    def print_quotation_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': ids,
             'model': 'sale.order',
             'form': data
                 }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'sale.order.partner',
            'datas': datas,
            }
class account_invoice(osv.osv):
    _inherit = "account.invoice"
    _columns = {
        'shipping_date': fields.date('Shipping Date'),
        'account_invoice_create': fields.date('Invoice Creation Date'),
		'create_time': fields.char('Invoice Creation Time'),
        }

    _defaults = {
        'account_invoice_create': lambda *a: time.strftime('%Y-%m-%d'),
		'create_time': str(datetime.now().time())[0:5],
    }

    def account_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': ids,
             'model': 'account.invoice',
             'form': data
                 }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.invoice.webkit',
            'datas': datas,
            }
class mail_compose_message(osv.TransientModel):
    _inherit = "mail.compose.message"
    
    def default_get(self, cr, uid, fields, context=None):
         res = super(mail_compose_message, self).default_get(cr, uid, fields, context=context)
         template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'partner_extended', 'email_template_partner_extended')[1]
         res.update({'template_id': template_id})
         return res

class procurement_order(osv.osv):
    _inherit = "procurement.order"
    _columns = {
		'shipping_date': fields.date('Shipping Date'),
		'sale_order_id': fields.many2one('sale.order','Sale Order'),
        }

class mrp_production(osv.osv):
    _inherit = "mrp.production"
    _columns = {
		'shipping_date': fields.date('Shipping Date'),
		'sale_order_id': fields.many2one('sale.order','Sale Order'),
        }
