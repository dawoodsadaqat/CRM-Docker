from odoo import fields, models


class TzCallLog(models.Model):
    _inherit = "tz.call.log"

    provider_id = fields.Many2one(
        "tz.voip.provider",
        string="VOIP Provider",
    )

    external_call_id = fields.Char(
        string="External Call ID",
        index=True,
        copy=False,
    )

    linked_call_id = fields.Char(
        string="Linked Call ID",
        index=True,
        copy=False,
    )

    source_extension = fields.Char(
        string="Agent Extension",
    )

    destination_number = fields.Char(
        string="Destination Number",
    )

    started_at = fields.Datetime(
        string="Started At",
    )

    answered_at = fields.Datetime(
        string="Answered At",
    )

    ended_at = fields.Datetime(
        string="Ended At",
    )