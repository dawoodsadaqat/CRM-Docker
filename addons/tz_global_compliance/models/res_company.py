from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    tz_enable_uae_compliance = fields.Boolean(
        string="Enable UAE Compliance",
        default=False,
        help="Enforce UAE VAT/TRN checks during operational and accounting flows.",
    )

    tz_compliance_country_mode = fields.Selection(
        selection=[
            ("uae", "UAE"),
            ("saudi", "Saudi"),
            ("international", "International"),
        ],
        string="Compliance Country Mode",
        default="uae",
        required=True,
    )

    tz_zatca_readiness_note = fields.Text(
        string="Saudi ZATCA Readiness Checklist",
        default=(
            "Placeholder only: configure Saudi localization, e-invoicing, QR and reporting "
            "per ZATCA regulations before production rollout."
        ),
    )
