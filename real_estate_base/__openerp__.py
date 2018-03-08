# -*- coding: utf-8 -*-
# Copyright (c) 2013 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                    Ignacio Ibeas <ignacio@acysos.com>
#                    Daniel Pascal <daniel@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name" : "Real Estate Base",
    "version" : "1.0",
    "author" : "Acysos S.L.",
    "website" : "www.acysos.com",
    "description": """Add real estate management""",
    "license" : "AGPL-3",
    "category" : "Specific Industry Applications",
    "depends" : [
         'base',
         'calendar',
         'base_location',
         'crm',
         'document',
         'account'
#        "document_ftp",
        ],
    "init_xml" : [],
    "demo_xml" : [],
    "data" :[
        'security/real_estate_security.xml',
        'security/ir.model.access.csv',
#        'report/generic_list.xml',
        'views/top_view.xml',
        'views/partner_view.xml',
        'data/top_sequence.xml',
#        'data/document_data.xml',
        'views/company_view.xml',
        'views/res_user.xml',
        'data/rental_agreement_sequence.xml',
        'views/rental_agreement_view.xml',
        'views/calendar_view.xml',
        'views/top_meetings_view.xml',
        ],
    "active": False,
    "installable": True
}