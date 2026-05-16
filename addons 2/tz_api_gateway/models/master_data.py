from odoo import fields, models


class TzPropertyType(models.Model):
    _name = "tz.property.type"
    _description = "Property Type"
    _rec_name = "name"

    name = fields.Char(required=True)
    code = fields.Char(required=True)


class TzLeadTemperature(models.Model):
    _name = "tz.lead.temperature"
    _description = "Lead Temperature"
    _rec_name = "name"

    name = fields.Char(required=True)
    code = fields.Char(required=True)