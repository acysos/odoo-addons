# -*- coding: utf-8 -*-
{
    'name': 'Attendance Portal Check In/Out',

    'summary': """ Attendance Portal Check In/Out """,

    'description': """
        Attendance Portal Check In/Out
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Human Resources',
    'version': '14.0',

    'depends': [
        'web',
        'portal',
        'hr_attendance',
        'hr_attendance_portal',
    ],

    'data': [
        'views/hr_attendance_portal_templates.xml',
        'views/hr_attendance_views.xml',
    ],
}