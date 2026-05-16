from odoo import models, fields


class TzPropertyProject(models.Model):
    _name = "tz.property.project"
    _description = "Property Project"
    _order = "name asc"

    name = fields.Char(string="Project Name", required=True)

    developer_id = fields.Many2one(
        "res.partner",
        string="Developer"
    )

    city = fields.Char(string="City", default="Dubai")
    area = fields.Char(string="Area")

    project_type = fields.Selection([
        ("residential", "Residential"),
        ("commercial", "Commercial"),
        ("mixed_use", "Mixed Use"),
    ], string="Project Type", default="residential")

    completion_status = fields.Selection([
        ("off_plan", "Off Plan"),
        ("under_construction", "Under Construction"),
        ("ready", "Ready"),
    ], string="Completion Status", default="ready")

    handover_date = fields.Date(string="Handover Date")
    description = fields.Text(string="Description")

    building_ids = fields.One2many(
        "tz.property.building",
        "project_id",
        string="Buildings"
    )

    unit_ids = fields.One2many(
        "tz.property.unit",
        "project_id",
        string="Units"
    )

    building_count = fields.Integer(
        string="Buildings",
        compute="_compute_counts"
    )

    unit_count = fields.Integer(
        string="Units",
        compute="_compute_counts"
    )

    def _compute_counts(self):
        for project in self:
            project.building_count = len(project.building_ids)
            project.unit_count = len(project.unit_ids)