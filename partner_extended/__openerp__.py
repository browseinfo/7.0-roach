{
    'name': 'Partner and sales Extension',
    'version': '1.0',
    'category': 'sales',
    'author': 'BrowseInfo',
    'website': 'http://www.browseinfo.in',
    'images': [],
    'depends': ['report_aeroo',
                'report_aeroo_ooo',
                 'sale_stock', 
                 'base_vat',
                 'mrp',],
    'data': [
        'security/partner_extended_security.xml',
        'security/ir.model.access.csv',
        'partner_extended_view.xml',
        'partner_extended_cron.xml',
        'report/account_invoice_extend.xml',
        'report/aeroo_report.xml',
        'report/aeroo_report_invoice.xml',
        'partner_extended_report.xml',
        'report/report_aeroo.xml',
        'report/report.xml',
        'partner_extended_data.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

