# -*- coding: utf-8 -*-
import time
from openerp.report import report_sxw
from tools import ustr
from translate import Translator
from openerp.tools.amount_to_text_en import amount_to_text
import util
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
            'get_vat': self.get_vat,
            'fill_star': self.fill_star,
            'fill_stars': self.fill_stars,
        })
        self.context = context.copy()       
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
            return ustr(partner_id.name)
        else:
            return ustr(partner_id.parent_id.name)
    def get_vat(self, vat):
        if not vat:
            vat = ''
        else:
            length = len(vat)
            vat = vat[2:length]
        return vat

    def fill_stars(self, amount):
        if self.context['lang'] != "es_GT":
            amount_word = amount_to_text(amount)
            amount_word = amount_word.replace('Dollars','')
            word = amount_word.upper()
            translation = Translator(to_lang="tr").translate(word)
            translation = translation.lower().replace('euro','TL').replace('cents','KR').replace(' ','')
            return translation
        else:
            return ''

    def fill_star(self, amount):
        if self.context['lang'] == "es_GT":
            word = util.num_a_letras(amount).upper()
            translation = Translator(to_lang="tr").translate(word)
            translation = translation.lower().replace('euro','TL').replace('cents','KR').replace(' ','')
            return translation
        else:
            return ''
report_sxw.report_sxw('report.account.invoice.webkit', 'account.invoice', '7.0-roach/partner_extended/report/account_invoice_extend_webkit_tmpl.mako', parser=account_webkit, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

