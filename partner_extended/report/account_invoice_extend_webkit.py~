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
            'amount2words': self.amount_to_words,
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

    def amount_to_words(self, amount, currency):
        amount_word = amount_to_text(amount)
        word = amount_word.upper()
        translation = Translator(to_lang="tr").translate(word)
        translation = translation.lower().replace('eighty','seksen').replace('ten','on').replace('sifir',ustr('sıfır‏')).replace(' ','').replace(',','').replace('ve','').replace('bir','')
        if currency:
            if currency.name == 'EUR':
                translation = translation.replace('euro','AVRO').replace('cents','SENTS').replace('cent','SENT')
            if currency.name == 'USD':
                translation = translation.replace('euro','DOLAR').replace('cents','SENTS').replace('cent','SENT')
            if currency.name == 'TRY':
                translation = translation.replace('euro','TL').replace('cents','KR').replace('cent','KR')
        return translation

report_sxw.report_sxw('report.account.invoice.webkit', 'account.invoice', '7.0-roach/partner_extended/report/account_invoice_extend_webkit_tmpl.mako', parser=account_webkit, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

