# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    # App information
    'name': 'Sale Margin Report',
    'version': '12.0',
    'summary': 'With the Sale Margin Report, use can see the profit they are getting against each sales order.',
    'category': 'sale',
    'license': 'OPL-1',
    
    # Dependencies
    'depends': ['sale_margin','stock', 'sale'],
    
    # Views
    'data': [
        'security/ir.model.access.csv',
        'view/sale_margin_report_view.xml',
        'report/sale_margin_qweb_report.xml',
        'report/layouts.xml',
        'report/sale_margin_report_template.xml',
    ],
    
    # Odoo Store Specific
    'images': ['static/description/Sale-Margin-Report-Store-Cover.jpg'],
    
    # Author
    
    "author": "Emipro Technologies Pvt. Ltd.",
    'website': 'http://www.emiprotechnologies.com/',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
    
    # Technical
    'installable': True,
    'application': True,
    'auto_install': False,
    'live_test_url':'https://www.emiprotechnologies.com/free-trial?app=sale-margin-report-ept&version=12&edition=enterprise',
    'price': '199',
    'currency': 'EUR',
}
