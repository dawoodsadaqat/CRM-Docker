{
    "name": "TZ HR Extension",
    "version": "17.0.1.0.0",
    "summary": "Create CRM users from Employee screen and restrict manual user creation",
    "category": "Human Resources",
    "author": "Techzilla",
    "license": "LGPL-3",
    "depends": [
        "base",
        "hr",
        "crm",
        "sales_team",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_employee_views.xml",
    ],
    "installable": True,
    "application": False,
}