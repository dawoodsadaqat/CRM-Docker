{
    "name": "TZ Payroll",
    "version": "17.0.1.0.0",
    "summary": "Lightweight payroll integrated with CRM commissions",
    "category": "Human Resources",
    "author": "Techzilla",
    "license": "LGPL-3",
    "depends": [
        "hr",
        "hr_attendance",
        "hr_expense",
        "account",
        "tz_hr_extension",
        "tz_commission",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/tz_payroll_security.xml",
        "views/tz_payroll_views.xml",
    ],
    "installable": True,
    "application": True,
}