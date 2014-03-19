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
        self.ucluler=["","bin","milyon","milyar","trilyon","katrilyon","kentilyon",
             "sekstilyon","oktilyon","nonilyon","desilyon"]

        self.localcontext.update({
            'time': time,
            'get_page_break' : self.get_page_break,
            'set_page_total' : self.set_page_total,
            'get_page_total' : self.get_page_total,
            'get_page_header' : self.get_page_header,
            'get_partner_name': self.get_partner_name,
            'get_vat': self.get_vat,
            'amount2words': self.nu2word,
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

    def nu2word(self,sayi, currency):
        sayi =  str(sayi).split('.')
        translation1 = self.return_number(float(sayi[0]))
        if sayi[1] == '00':
            translation2 = ustr('sıfır‏')
        else:
            translation2 = self.return_number(float(sayi[1]))
        translation = translation1 + translation2
        if currency.name == 'EUR':
            translation = translation1 + 'AVRO' + translation2 + 'SENT'
        if currency.name == 'USD':
            translation = translation1 + 'DOLAR' + translation2 + 'SENT'
        if currency.name == 'TRY':
            translation = translation1 + 'TL' + translation2 + 'KR'
        return translation
    def ucluyuVer(self,sayi):
        birler = ["","bir","iki",ustr("üç"),ustr("dört"),"bes","alti","yedi","sekiz","dokuz"]
        onlar = ["","on","yirmi","otuz","kirk","elli","altmis","yetmis","seksen","doksan"]
        yuzler = [i+ustr("yüz") for i in birler]
        yuzler[1] = ustr("yüz")

        basamaklar = [birler,onlar,yuzler]

        sayi = sayi[::-1]
        yazi,bs = [],0
        for i in sayi:
            rakam = sayi[bs]
            bs += 1
            if rakam != "0":
                yazi.append(basamaklar[bs-1][int(rakam)])
        return "".join(reversed(yazi))

    def return_number(self,sayi):
	    sayi = '{:,}'.format(int(sayi))
	    haneler = reversed(sayi.split(","))
	    uclus,sonuc = 0,[]
	    for hane in haneler:
		    uclu = self.ucluyuVer(hane)
		    if uclu != "":
			    sonuc.append(uclu+""+ self.ucluler[uclus])
		    uclus+=1
	    son = "".join(reversed(sonuc))
	    if son.startswith('birbin'):
		    son = son[3:]
	    return(son.strip())
report_sxw.report_sxw('report.account.invoice.webkit', 'account.invoice', '7.0-roach/partner_extended/report/account_invoice_extend_webkit_tmpl.mako', parser=account_webkit, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

