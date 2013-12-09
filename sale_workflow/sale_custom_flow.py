# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP

class sale_order(osv.osv):
    _inherit = 'sale.order'

    _columns = {
        
        'state': fields.selection([
            ('draft', 'Draft Quotation'),
            ('sent', 'Quotation Sent'),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('approved', 'Approved'),
            ('progress', 'Sales Order'),
            ('manual', 'Sale to Invoice'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ], 'Status', readonly=True),
        'send_order': fields.boolean('Send Order'),
        'order_priority': fields.selection([
            ('0', 'Not Urgent'),
            ('1', 'Very Low'),
            ('2', 'Low'),
            ('3', 'Normal'),
            ('4', 'Urgent'),
            ('5', 'Very Urgent'),
        ], 'Order Priority', required=True),
    }
    _defaults = {
        'send_order': False,
        'order_priority': '3'
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(sale_order, self).write(cr, uid, ids, vals, context=context)
        sale_browse = self.browse(cr, uid, ids, context=context)[0] #browse sale order
        manufac_obj = self.pool.get('mrp.production')
        manufac_search_id = manufac_obj.search(cr, uid, [('origin', '=', sale_browse.name)]) #search id of manufacture with related to SO
        manufac_obj.write(cr, uid, manufac_search_id, {'priority': sale_browse.order_priority}) #change priority 
        return res

    def sale_approved(self, cr, uid, ids, context=None):
         return self.write(cr, uid, ids, {'state' : 'approved'}, context=context)
         
    def action_send_to_order(self, cr, uid, ids, context=None):
        proc_obj = self.pool.get('procurement.order') 
        sale_browse = self.browse(cr, uid, ids, context=context) #browse sale order obj
        proc_ids = proc_obj.search(cr, uid, [('origin', '=', sale_browse[0].name)]) #search record on procurement order with saleorder name

        wf_service = netsvc.LocalService("workflow")
        self.write(cr, uid, ids, {'send_order': True}, context=context)

        for proc_id in proc_ids:
            wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_check', cr)
            return True


class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    def send_mail_to_member(self, cr, uid, ids):
            res = {}
            mail_mail = self.pool.get('mail.mail')
            mail_to = ""
            mail_ids = []

            admin_email = self.pool.get('res.users').browse(cr, uid, [1])[0].email
            manufacture = self.browse(cr, uid, ids)[0]
           
            team = manufacture.section_id.member_ids
            leader_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale_workflow', 'manufacture_team')[1]
            leader_email = self.pool.get('manufacture.team.section').browse(cr,uid,leader_id).user_id.email
            if manufacture.section_id == leader_id:
                mail_to = leader_email
            else:
                team_mail = ''
                for teamemail in team:
                    team_mail += teamemail.email
                if manufacture.section_id.user_id.email:
                    mail_to = manufacture.section_id.user_id.email + team_mail + ','
                sub = '[Production Need to be start]'

                body = """
                Hello , \n             
                We have got %s Manufacture Order, \n
                Product is %s and schedual date is %s, \n
                Bill of Material is %s, \n
                So we need to start production as much as eariler.
              
                """ % (manufacture.name, manufacture.product_id.name, manufacture.date_planned, manufacture.bom_id.name)                     
                if mail_to:
                    vals = {
                            'state': 'outgoing',
                            'subject': sub,
                            'body_html': body,
                            'email_to': mail_to,
                            'email_from': admin_email,
                        }
                  
                    mail_ids.append(mail_mail.create(cr, uid, vals))
                    mail_mail.send(cr, uid, mail_ids, auto_commit=True)
            return res


    
    def test_if_product(self, cr, uid, ids):
        res = super(mrp_production, self).test_if_product(cr, uid, ids)
        res =  self.send_mail_to_member(cr, uid, ids)
        return res

    _columns = {
        'priority': fields.selection([
            ('0', 'Not Urgent'),
            ('1', 'Very Low'),
            ('2', 'Low'),
            ('3', 'Normal'),
            ('4', 'Urgent'),
            ('5', 'Very Urgent'),
        ], 'Order Priority'),
        'section_id': fields.many2one('manufacture.team.section', 'Manufacture Team', select=True),
        'send_mail': fields.boolean(string="Send Mail"),
    }
    
    def default_get(self, cr, uid, fields, context=None):    
        vals = super(mrp_production, self).default_get(cr, uid, fields, context=context)
        vals.update({'section_id':1})
        return vals

    _order = 'priority desc'
    _defaults = {
        'priority': '3',
        'send_mail': False,
    }

class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'supplier_representative': fields.many2one('res.users', 'Supplier Representative'),
    }

class manufacture_team_section(osv.osv):
    """ Model for Manufacture teams. """
    _name = "manufacture.team.section"
    _inherits = {'mail.alias': 'alias_id'}
    _inherit = "mail.thread"
    _description = "Manufacture Teams"
    _order = "complete_name"

    def get_full_name(self, cr, uid, ids, field_name, arg, context=None):
        return  dict(self.name_get(cr, uid, ids, context=context))

    _columns = {
        'name': fields.char('Manufacture Team', size=64, required=True, translate=True),
        'complete_name': fields.function(get_full_name, type='char', size=256, readonly=True, store=True),
        'code': fields.char('Code', size=8),
        'active': fields.boolean('Active', help="If the active field is set to "\
                        "true, it will allow you to hide the Manufacture team without removing it."),
        'user_id': fields.many2one('res.users', 'Team Leader'),
        'member_ids':fields.many2many('res.users', 'manu_member_rel', 'section_id', 'member_id', 'Team Members'),
        'reply_to': fields.char('Reply-To', size=64, help="The email address put in the 'Reply-To' of all emails sent by OpenERP about cases in this sales team"),
        'parent_id': fields.many2one('manufacture.team.section', 'Parent Team'),
        'child_ids': fields.one2many('manufacture.team.section', 'parent_id', 'Child Teams'),
        'resource_calendar_id': fields.many2one('resource.calendar', "Working Time", help="Used to compute open days"),
        'note': fields.text('Description'),
        'alias_id': fields.many2one('mail.alias', 'Alias', ondelete="restrict", required=True,
                                    help="The email address associated with this team. New emails received will automatically "
                                         "create new leads assigned to the team."),
    }

    _defaults = {
        'active': 1,
        'alias_domain': False, # always hide alias during creation
        
    }

    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code of the manufacture team must be unique !')
    ]

    _constraints = [
        (osv.osv._check_recursion, 'Error ! You cannot create recursive Sales team.', ['parent_id'])
    ]

    def name_get(self, cr, uid, ids, context=None):
        """Overrides orm name_get method"""
        if not isinstance(ids, list) :
            ids = [ids]
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['name', 'parent_id'], context)

        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1] + ' / ' + name
            res.append((record['id'], name))
        return res

    def create(self, cr, uid, vals, context=None):
        mail_alias = self.pool.get('mail.alias')
        if not vals.get('alias_id'):
            vals.pop('alias_name', None) # prevent errors during copy()
            alias_id = mail_alias.create_unique_alias(cr, uid,
                    {'alias_name': vals['name']},
                    model_name="mrp.production",
                    context=context)
            vals['alias_id'] = alias_id
        res = super(manufacture_team_section, self).create(cr, uid, vals, context)
        mail_alias.write(cr, uid, [vals['alias_id']], {'alias_defaults': {'section_id': res, 'type':'lead'}}, context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        # Cascade-delete mail aliases as well, as they should not exist without the sales team.
        mail_alias = self.pool.get('mail.alias')
        alias_ids = [team.alias_id.id for team in self.browse(cr, uid, ids, context=context) if team.alias_id ]
        res = super(manufacture_team_section, self).unlink(cr, uid, ids, context=context)
        mail_alias.unlink(cr, uid, alias_ids, context=context)
        return res


class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    _columns = {
        'supplier_representative': fields.many2one('res.users', 'Supplier Representative'),
    }
    
    def onchange_partner_id(self, cr, uid, ids, partner_id): #onchange supplier representative get
        partner = self.pool.get('res.partner')
        if not partner_id:
            return {'value': {
                'fiscal_position': False,
                'payment_term_id': False,
                'supplier_representative': False,
                }}
        supplier_address = partner.address_get(cr, uid, [partner_id], ['default'])
        supplier = partner.browse(cr, uid, partner_id)
        return {'value': {
            'pricelist_id': supplier.property_product_pricelist_purchase.id,
            'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
            'payment_term_id': supplier.property_supplier_payment_term.id or False,
            'supplier_representative': supplier.supplier_representative.id or False,
            }}

    def create(self, cr, uid, vals, context=None): #use for the send mail when Purchase order create
        res = super(purchase_order, self).create(cr, uid, vals, context=context)
        mail_mail = self.pool.get('mail.mail')
        mail_to = ""
        mail_ids = []
        partner_id = vals.get('partner_id')
        represent_id = vals.get('supplier_representative')
        if not represent_id:
            return res
        partner = self.pool.get('res.users')
        admin_email = partner.browse(cr, uid, [1])[0].email
        saleperson = partner.browse(cr, uid, represent_id, context=context)
        if saleperson.email:
            mail_to = saleperson.email
            sub = '[Purchase Order Received]'

            body = """
            Hello , \n              
            We have got %s Purchase Order, \n 
            Order date is %s, \n
            So we need to work as much as eariler.
           
            """ % (vals['name'], vals['date_order'])                      
            if mail_to:
                vals = {
                        'state': 'outgoing',
                        'subject': sub,
                        'body_html': body,
                        'email_to': mail_to,
                        'email_from': admin_email,
                    }
               
                mail_ids.append(mail_mail.create(cr, uid, vals))
                mail_mail.send(cr, uid, mail_ids, auto_commit=True)
        return res

class procurement_order(osv.osv):
    _inherit = 'procurement.order'
    _columns = {
                
    }
    def make_po(self, cr, uid, ids, context=None):
        """ Make purchase order from procurement
        @return: New created Purchase Orders procurement wise
        """
        res = {}
        if context is None:
            context = {}
        company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        partner_obj = self.pool.get('res.partner')
        uom_obj = self.pool.get('product.uom')
        pricelist_obj = self.pool.get('product.pricelist')
        prod_obj = self.pool.get('product.product')
        acc_pos_obj = self.pool.get('account.fiscal.position')
        seq_obj = self.pool.get('ir.sequence')
        warehouse_obj = self.pool.get('stock.warehouse')

        for procurement in self.browse(cr, uid, ids, context=context):
            res_id = procurement.move_id.id
            partner = procurement.product_id.seller_id # Taken Main Supplier of Product of Procurement.
            seller_qty = procurement.product_id.seller_qty
            partner_id = partner.id
            address_id = partner_obj.address_get(cr, uid, [partner_id], ['delivery'])['delivery']
            pricelist_id = partner.property_product_pricelist_purchase.id
            warehouse_id = warehouse_obj.search(cr, uid, [('company_id', '=', procurement.company_id.id or company.id)], context=context)
            uom_id = procurement.product_id.uom_po_id.id
           

            qty = uom_obj._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, uom_id)
            if seller_qty:
                qty = max(qty,seller_qty)

            price = pricelist_obj.price_get(cr, uid, [pricelist_id], procurement.product_id.id, qty, partner_id, {'uom': uom_id})[pricelist_id]

            schedule_date = self._get_purchase_schedule_date(cr, uid, procurement, company, context=context)
            purchase_date = self._get_purchase_order_date(cr, uid, procurement, company, schedule_date, context=context)

            #Passing partner_id to context for purchase order line integrity of Line name
            new_context = context.copy()
            new_context.update({'lang': partner.lang, 'partner_id': partner_id})

            product = prod_obj.browse(cr, uid, procurement.product_id.id, context=new_context)
            taxes_ids = procurement.product_id.supplier_taxes_id
            taxes = acc_pos_obj.map_tax(cr, uid, partner.property_account_position, taxes_ids)

            name = product.partner_ref
            if product.description_purchase:
                name += '\n'+ product.description_purchase
            line_vals = {
                'name': name,
                'product_qty': qty,
                'product_id': procurement.product_id.id,
                'product_uom': uom_id,
                'price_unit': price or 0.0,
                'date_planned': schedule_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'move_dest_id': res_id,
                'taxes_id': [(6,0,taxes)],
            }
            name = seq_obj.get(cr, uid, 'purchase.order') or _('PO: %s') % procurement.name
            po_vals = {
                'name': name,
                'origin': procurement.origin,
                'partner_id': partner_id,
                'location_id': procurement.location_id.id,
                'warehouse_id': warehouse_id and warehouse_id[0] or False,
                'pricelist_id': pricelist_id,
                'date_order': purchase_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'company_id': procurement.company_id.id,
                'fiscal_position': partner.property_account_position and partner.property_account_position.id or False,
                'payment_term_id': partner.property_supplier_payment_term.id or False,
                'supplier_representative' : partner.supplier_representative.id or False,
            }
            res[procurement.id] = self.create_procurement_purchase_order(cr, uid, procurement, po_vals, line_vals, context=new_context)
            self.write(cr, uid, [procurement.id], {'state': 'running', 'purchase_id': res[procurement.id]})
            self.message_post(cr, uid, ids, body=_("Draft Purchase Order created"), context=context)
        return res
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
