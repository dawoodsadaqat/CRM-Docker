{
    "name": "TZ Attendance Geo",
    "version": "17.0.1.0.1",
    "summary": "Extend standard Odoo Attendances with GPS, maps and fraud warnings",
    "category": "Human Resources",
    "author": "Techzilla",
    "license": "LGPL-3",
    "depends": [
        "hr",
        "hr_attendance",
        "tz_live_tracking",
        "tz_hr_extension",
    ],
    "data": [
        "views/hr_attendance_views.xml",
    ],
    "installable": True,
    "application": False,
}