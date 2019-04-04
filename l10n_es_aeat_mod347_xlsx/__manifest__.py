# Copyright 2019 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'AEAT modelo 347 - Export Excel',
    'author': 'Acysos S.L.',
    'website': 'https://www.acysos.com',
    'category': 'Reporting',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
#         'l10n_es_aeat_mod347',
        'report_xlsx_helper'
    ],
    'data': [
        'views/mod347_view.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'installable': True,
}
