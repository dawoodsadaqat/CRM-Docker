from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    tz_sla_hours = fields.Float(
        string="Lead SLA Hours",
        config_parameter="tz_dashboard.sla_hours",
        default=2.0
    )
    tz_rescue_sla_hours = fields.Float(
    	string="Rescue SLA Hours",
    	config_parameter="tz_dashboard.rescue_sla_hours",
 	default=1.0
    )
    tz_sla_warning_hours = fields.Float(
    	string="SLA Warning Reminder Hours",
    	config_parameter="tz_dashboard.sla_warning_hours",
    	default=6.0
    )