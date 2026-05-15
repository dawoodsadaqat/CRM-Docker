def post_init_hook(env):
    duplicate_xmlids = [
        "tz_menu_structure.menu_tz_main_crm",
        "tz_menu_structure.menu_tz_main_employees",
        "tz_payroll.menu_tz_payroll_root",
    ]

    for xmlid in duplicate_xmlids:
        menu = env.ref(xmlid, raise_if_not_found=False)
        if menu:
            menu.sudo().write({"active": False})

    crm_root = env.ref("crm.crm_menu_root", raise_if_not_found=False)
    if crm_root:
        crm_root.sudo().write({
            "active": True,
            "sequence": 10,
            "name": "CRM",
        })

    hr_root = env.ref("hr.menu_hr_root", raise_if_not_found=False)
    if hr_root:
        hr_root.sudo().write({
            "active": True,
            "sequence": 20,
            "name": "Employees",
        })

    accounting_root = env.ref("tz_menu_structure.menu_tz_main_accounting", raise_if_not_found=False)

    possible_invoicing_xmlids = [
        "account.menu_invoicing",
        "account.menu_finance",
        "account_accountant.menu_accounting",
    ]

    if accounting_root:
        for xmlid in possible_invoicing_xmlids:
            menu = env.ref(xmlid, raise_if_not_found=False)
            if menu:
                menu.sudo().write({
                    "active": True,
                    "parent_id": accounting_root.id,
                    "sequence": 40,
                })