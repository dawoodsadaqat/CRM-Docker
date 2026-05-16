from odoo import models, fields, api


class TzPropertyListing(models.Model):
    _name = "tz.property.listing"
    _description = "Property Listing"
    _order = "published_date desc, id desc"

    name = fields.Char(string="Listing Title", required=True)

    unit_id = fields.Many2one(
        "tz.property.unit",
        string="Unit",
        required=True
    )

    project_id = fields.Many2one(
        related="unit_id.project_id",
        string="Project",
        store=True,
        readonly=True
    )

    building_id = fields.Many2one(
        related="unit_id.building_id",
        string="Building",
        store=True,
        readonly=True
    )

    area = fields.Char(
        related="unit_id.area",
        string="Area",
        store=True,
        readonly=True
    )

    property_type = fields.Selection(
        related="unit_id.property_type",
        string="Property Type",
        store=True,
        readonly=True
    )

    listing_type = fields.Selection([
        ("sale", "Sale"),
        ("rent", "Rent"),
    ], string="Listing Type", required=True)

    listing_price = fields.Float(string="Listing Price")

    portal_reference = fields.Char(string="Portal Reference")

    status = fields.Selection([
        ("draft", "Draft"),
        ("published", "Published"),
        ("unpublished", "Unpublished"),
        ("closed", "Closed"),
    ], string="Status", default="draft")

    published_date = fields.Date(string="Published Date")

    description = fields.Text(string="Description")

    @api.onchange("unit_id", "listing_type")
    def _onchange_unit_or_listing_type(self):
        for listing in self:
            if listing.unit_id and listing.listing_type == "sale":
                listing.listing_price = listing.unit_id.sale_price

            if listing.unit_id and listing.listing_type == "rent":
                listing.listing_price = listing.unit_id.rent_price