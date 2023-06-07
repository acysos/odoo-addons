# -*- coding: utf-8 -*-
{
    'name': 'Attendance Portal',

    'summary': """ Attendance Portal """,

    'description': """
        Attendance Portal
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Human Resources',
    'version': '14.0',

    'depends': [
        'web',
        'portal',
        'hr_attendance',
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/hr_attendance_security.xml',
        'views/hr_attendance_portal_templates.xml',
    ],
}