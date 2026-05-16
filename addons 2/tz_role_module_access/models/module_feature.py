from odoo import fields, models


class TzModuleFeature(models.Model):
    _name = "tz.module.feature"
    _description = "Module / Submodule Feature"
    _order = "sequence, name"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    category = fields.Selection([
        ("crm", "CRM"),
        ("sales", "Sales"),
        ("property", "Property"),
        ("communication", "Communication"),
        ("finance", "Finance"),
        ("dashboard", "Dashboard"),
        ("hr", "HR"),
        ("tracking", "Tracking"),
        ("api", "API"),
        ("settings", "Settings"),
    ], string="Category", default="crm", required=True)

    technical_group_id = fields.Many2one(
        "res.groups",
        string="Technical Security Group",
        readonly=True,
        copy=False,
        help="Internal group used to control menus and access for this feature.",
    )

    menu_xml_ids = fields.Text(
        string="Menu XML IDs",
        help="One menu external XML ID per line. These menus will be restricted to this feature group.",
    )

    menu_name_keywords = fields.Text(
        string="Menu Name Keywords",
        help="Optional fallback menu names, one per line. Used only when a menu has no known XML ID.",
    )
