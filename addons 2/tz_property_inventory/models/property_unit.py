from odoo import models, fields, api


class TzPropertyUnit(models.Model):
    _name = "tz.property.unit"
    _description = "Property Unit"
    _order = "name asc"

    name = fields.Char(string="Unit Name", required=True)

    unit_number = fields.Char(string="Unit Number")

    project_id = fields.Many2one(
        "tz.property.project",
        string="Project",
        required=True
    )

    building_id = fields.Many2one(
        "tz.property.building",
        string="Building"
    )

    developer_id = fields.Many2one(
        related="project_id.developer_id",
        string="Developer",
        store=True,
        readonly=True
    )

    city = fields.Char(
        related="project_id.city",
        string="City",
        store=True,
        readonly=True
    )

    area = fields.Char(string="Area")

    property_type = fields.Selection([
        ("apartment", "Apartment"),
        ("villa", "Villa"),
        ("townhouse", "Townhouse"),
        ("office", "Office"),
        ("retail", "Retail"),
        ("land", "Land"),
    ], string="Property Type", required=True)

    vat_treatment = fields.Selection([
        ("standard_5", "Standard Rated 5%"),
        ("zero_rated", "Zero Rated"),
        ("exempt", "Exempt"),
        ("out_of_scope", "Out of Scope"),
    ], string="VAT Treatment", default="standard_5", required=True)

    bedrooms = fields.Selection([
        ("studio", "Studio"),
        ("1", "1 Bedroom"),
        ("2", "2 Bedrooms"),
        ("3", "3 Bedrooms"),
        ("4", "4 Bedrooms"),
        ("5_plus", "5+ Bedrooms"),
    ], string="Bedrooms")

    bathrooms = fields.Integer(string="Bathrooms")
    size_sqft = fields.Float(string="Size Sqft")

    sale_price = fields.Float(string="Sale Price")
    rent_price = fields.Float(string="Rent Price")

    availability = fields.Selection([
        ("available", "Available"),
        ("reserved", "Reserved"),
        ("sold", "Sold"),
        ("rented", "Rented"),
        ("unavailable", "Unavailable"),
    ], string="Availability", default="available")

    owner_id = fields.Many2one(
        "res.partner",
        string="Owner"
    )

    assigned_agent_id = fields.Many2one(
        "res.users",
        string="Assigned Agent"
    )

    listing_ids = fields.One2many(
        "tz.property.listing",
        "unit_id",
        string="Listings"
    )

    active = fields.Boolean(default=True)

    display_price = fields.Float(
        string="Display Price",
        compute="_compute_display_price"
    )

    @api.depends("sale_price", "rent_price")
    def _compute_display_price(self):
        for unit in self:
            unit.display_price = unit.sale_price or unit.rent_price or 0.0

    @api.onchange("project_id")
    def _onchange_project_id(self):
        for unit in self:
            if unit.project_id:
                unit.area = unit.project_id.area

    @api.onchange("property_type")
    def _onchange_property_type_vat_treatment(self):
        for unit in self:
            if unit.property_type in ("office", "retail"):
                unit.vat_treatment = "standard_5"
            elif unit.property_type in ("apartment", "villa", "townhouse"):
                unit.vat_treatment = "exempt"
            elif unit.property_type == "land":
                unit.vat_treatment = "out_of_scope"