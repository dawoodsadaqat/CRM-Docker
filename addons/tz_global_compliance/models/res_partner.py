import re

from odoo import api, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.constrains("vat", "country_id")
    def _check_tz_uae_trn_format(self):
        for partner in self:
            if partner.vat and partner.country_id.code == "AE":
                if not re.fullmatch(r"\d{15}", partner.vat.strip()):
                    raise ValidationError("UAE TRN must be exactly 15 digits.")
