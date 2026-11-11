from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    tz_voip_extension = fields.Char(
        string="VOIP Extension",
        help="Agent SIP extension, for example 1001."
    )