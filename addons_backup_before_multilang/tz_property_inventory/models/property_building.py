from odoo import models, fields


class TzPropertyBuilding(models.Model):
    _name = "tz.property.building"
    _description = "Property Building"
    _order = "name asc"

    name = fields.Char(string="Building Name", required=True)

    project_id = fields.Many2one(
        "tz.property.project",
        string="Project",
        required=True,
        ondelete="cascade"
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

    area = fields.Char(
        related="project_id.area",
        string="Area",
        store=True,
        readonly=True
    )

    address = fields.Char(string="Address")
    floors = fields.Integer(string="Number of Floors")
    amenities = fields.Text(string="Amenities")

    unit_ids = fields.One2many(
        "tz.property.unit",
        "building_id",
        string="Units"
    )

    unit_count = fields.Integer(
        string="Units",
        compute="_compute_unit_count"
    )

    def _compute_unit_count(self):
        for building in self:
            building.unit_count = len(building.unit_ids)