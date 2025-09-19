# Copyright 2025 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hacienda Foral de Navarra',
    'version': '16.0.0.1.4',
    'author': 'Acysos S.L.',
    'website': 'https://www.navarradoo.com',
    'category': 'Accounting',
    'license': 'AGPL-3',
    'summary': 'Sistema IAP para la presentación de impuestos en Navarra',
    'depends': [
        'base',
        'account',
        'l10n_es',
        'l10n_es_aeat',
        'l10n_es_aeat_sii_oca',
        'l10n_es_aeat_mod347',
        'l10n_es_aeat_mod349',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/l10n_es_navarra_f69_security.xml',
        'data/f69/2024-10/l10n.es.aeat.map.tax.csv',
        'data/f69/2024-10/l10n.es.aeat.map.tax.line.csv',
        'wizard/export_to_hn_wizard.xml',
        'views/navarra_menu_views.xml',
        'views/modf69_views.xml',
        'views/res_company_views.xml',
        'views/aeat_report_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
}
