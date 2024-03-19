# Copyright 2015-2020 Acysos S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    'name': 'Account Invoice Retention',
    'version': '13.0.0.1.0',
    'author': 'Acysos S.L.',
    'category': 'Account',
    'license': 'AGPL-3',
    'description': """
    """,
    'website': 'http://www.acysos.com',
    'images': [],
    'depends': ['base',
                'account'
                ],
    'data': ['views/res_company_view.xml',
             'views/account_move_view.xml',
             'views/res_partner_view.xml',
             'views/report_invoice.xml'
             ],
    'installable': True,
    'auto_install': False,
}
