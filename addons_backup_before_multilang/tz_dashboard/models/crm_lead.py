from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta


class ResUsers(models.Model):
    _inherit = "res.users"

    supervisor_id = fields.Many2one(
        "res.users",
        string="Supervisor / Manager"
    )


class CrmLead(models.Model):
    _inherit = "crm.lead"

    TRACKED_FIELDS = {
        "name": ("lead_updated", "Lead Title"),
        "phone": ("lead_updated", "Phone"),
        "email_from": ("lead_updated", "Email"),
        "user_id": ("agent_assigned", "Salesperson / Supervisor"),
        "agent_owner_id": ("agent_assigned", "Assigned Agent"),
        "team_id": ("team_changed", "Sales Team"),
        "stage_id": ("stage_changed", "Pipeline Stage"),
        "conversion_stage": ("stage_changed", "Conversion Stage"),
        "probability": ("probability_changed", "Probability"),
        "expected_revenue": ("expected_revenue_changed", "Expected Revenue"),
        "deal_value": ("expected_revenue_changed", "Deal Value"),
        "type": ("lead_updated", "Lead Type"),
        "lead_category_id": ("lead_updated", "Lead Category"),
        "next_followup_date": ("followup_created", "Next Follow-up Date"),
        "first_response_date": ("first_response", "First Response Date"),
        "sla_rescue_status": ("rescue_started", "Rescue SLA Status"),
    }

    lead_category_id = fields.Many2one(
        "tz.lead.category",
        string="Lead Category",
        tracking=True
    )

    conversion_stage = fields.Selection([
        ("new", "New"),
        ("contacted", "Contacted"),
        ("site_visit", "Site Visit"),
        ("negotiation", "Negotiation"),
        ("won", "Won"),
        ("lost", "Lost"),
    ], string="Conversion Stage", default="new", tracking=True)

    conversion_stage_date = fields.Datetime(
        string="Last Conversion Update",
        default=fields.Datetime.now
    )

    deal_value = fields.Float(string="Deal Value")
    first_response_date = fields.Datetime(string="First Response Date")

    response_time_hours = fields.Float(
        string="Response Time Hours",
        compute="_compute_response_time_hours",
        store=True
    )

    sla_deadline = fields.Datetime(
        string="SLA Deadline",
        compute="_compute_sla_deadline",
        store=True
    )

    sla_status = fields.Selection([
        ("pending", "Pending"),
        ("met", "Met"),
        ("breached", "Breached"),
    ], string="SLA Status", compute="_compute_sla_status", store=True)

    sla_rescue_user_id = fields.Many2one("res.users", string="Rescue Agent")
    sla_rescue_assigned_date = fields.Datetime(string="Rescue Assigned Date")
    sla_rescue_deadline = fields.Datetime(string="Rescue SLA Deadline")

    sla_rescue_status = fields.Selection([
        ("none", "None"),
        ("in_progress", "In Progress"),
        ("rescued", "Rescued"),
        ("breached", "Breached Again"),
    ], string="Rescue SLA Status", default="none")

    next_followup_date = fields.Datetime(string="Next Follow-up Date")

    followup_status = fields.Selection([
        ("no_followup", "No Follow-up"),
        ("planned", "Planned"),
        ("overdue", "Overdue"),
        ("done", "Done"),
    ], string="Follow-up Status", compute="_compute_followup_status", store=True)

    lead_age_days = fields.Integer(
        string="Lead Age Days",
        compute="_compute_lead_age_days",
        store=True
    )

    stage_age_days = fields.Integer(
        string="Stage Age Days",
        compute="_compute_stage_age_days",
        store=True
    )

    is_stuck = fields.Boolean(
        string="Stuck Lead",
        compute="_compute_is_stuck",
        store=True
    )

    def _get_display_value(self, value):
        if not value:
            return False

        if hasattr(value, "display_name"):
            return value.display_name

        return value

    def _get_rescue_sla_hours(self):
        return float(
            self.env["ir.config_parameter"].sudo().get_param(
                "tz_dashboard.rescue_sla_hours",
                default="1"
            )
        )

    def _get_sla_warning_hours(self):
        return float(
            self.env["ir.config_parameter"].sudo().get_param(
                "tz_dashboard.sla_warning_hours",
                default="6"
            )
        )

    def _log_lead_history(
        self,
        event_type,
        old_agent=False,
        new_agent=False,
        note=False,
        field_name=False,
        old_value=False,
        new_value=False,
    ):
        for lead in self:
            visible_agents = self.env["res.users"]

            if lead.agent_owner_id:
                visible_agents |= lead.agent_owner_id

            if new_agent:
                visible_agents |= new_agent

            # Old agent should see only the actual reassignment/removal row.
            # Do NOT add old_agent for rescue_started / assigned_from_queue / later events.
            if old_agent and event_type == "agent_assigned":
                visible_agents |= old_agent

            if self.env.user.has_group("tz_crm_base.group_tz_crm_agent"):
                visible_agents |= self.env.user

            self.env["tz.lead.history"].sudo().create({
                "lead_id": lead.id,
                "event_type": event_type,
                "old_agent_id": old_agent.id if old_agent else False,
                "new_agent_id": new_agent.id if new_agent else False,
                "performed_by_id": self.env.user.id,
                "field_name": field_name or False,
                "old_value": str(self._get_display_value(old_value)) if old_value else False,
                "new_value": str(self._get_display_value(new_value)) if new_value else False,
                "sla_deadline": lead.sla_deadline,
                "rescue_deadline": lead.sla_rescue_deadline,
                "note": note or False,
                "visible_agent_ids": [(6, 0, visible_agents.ids)],
            })

    @api.onchange("conversion_stage")
    def _onchange_conversion_stage(self):
        for lead in self:
            lead.conversion_stage_date = fields.Datetime.now()

    @api.depends("create_date", "first_response_date")
    def _compute_response_time_hours(self):
        for lead in self:
            if lead.create_date and lead.first_response_date:
                delta = lead.first_response_date - lead.create_date
                lead.response_time_hours = delta.total_seconds() / 3600
            else:
                lead.response_time_hours = 0

    @api.depends("create_date")
    def _compute_sla_deadline(self):
        sla_hours = float(
            self.env["ir.config_parameter"].sudo().get_param(
                "tz_dashboard.sla_hours",
                default="2"
            )
        )

        for lead in self:
            lead.sla_deadline = (
                lead.create_date + timedelta(hours=sla_hours)
                if lead.create_date
                else False
            )

    @api.depends("first_response_date", "sla_deadline")
    def _compute_sla_status(self):
        now = fields.Datetime.now()

        for lead in self:
            if lead.first_response_date and lead.sla_deadline:
                lead.sla_status = "met" if lead.first_response_date <= lead.sla_deadline else "breached"
            elif lead.sla_deadline and now > lead.sla_deadline:
                lead.sla_status = "breached"
            else:
                lead.sla_status = "pending"

    @api.depends("next_followup_date")
    def _compute_followup_status(self):
        now = fields.Datetime.now()

        for lead in self:
            if not lead.next_followup_date:
                lead.followup_status = "no_followup"
            elif lead.next_followup_date < now:
                lead.followup_status = "overdue"
            else:
                lead.followup_status = "planned"

    @api.depends("create_date")
    def _compute_lead_age_days(self):
        now = fields.Datetime.now()

        for lead in self:
            lead.lead_age_days = (now - lead.create_date).days if lead.create_date else 0

    @api.depends("conversion_stage_date")
    def _compute_stage_age_days(self):
        now = fields.Datetime.now()

        for lead in self:
            lead.stage_age_days = (now - lead.conversion_stage_date).days if lead.conversion_stage_date else 0

    @api.depends("conversion_stage", "stage_age_days")
    def _compute_is_stuck(self):
        for lead in self:
            lead.is_stuck = (
                lead.conversion_stage not in ["won", "lost"]
                and lead.stage_age_days >= 3
            )

    def action_mark_first_response(self):
        for lead in self:
            if not lead.first_response_date:
                lead.first_response_date = fields.Datetime.now()

            lead.conversion_stage = "contacted"
            lead.conversion_stage_date = fields.Datetime.now()

            self.env["mail.activity"].search([
                ("res_model", "=", "crm.lead"),
                ("res_id", "=", lead.id),
                ("summary", "=", "SLA Warning Reminder"),
            ]).unlink()

            lead._log_lead_history(
                "first_response",
                new_agent=lead.user_id,
                note="First response marked"
            )

            if lead.sla_rescue_status == "in_progress":
                lead.sla_rescue_status = "rescued"

                lead._log_lead_history(
                    "rescued",
                    new_agent=lead.user_id,
                    note="Lead rescued within rescue SLA"
                )

        return True

    def action_mark_followup_done(self):
        for lead in self:
            lead.next_followup_date = False

            self.env["mail.activity"].search([
                ("res_model", "=", "crm.lead"),
                ("res_id", "=", lead.id),
                ("summary", "in", ["Follow-up Reminder", "Escalation Required"]),
            ]).unlink()

            lead._log_lead_history(
                "followup_done",
                new_agent=lead.user_id,
                note="Follow-up marked done"
            )

        return True

    def action_assign_to_me(self):
        rescue_hours = self._get_rescue_sla_hours()
        now = fields.Datetime.now()

        for lead in self:
            old_agent = lead.user_id

            if old_agent and old_agent.id == self.env.user.id:
                raise UserError(
                    "You cannot assign this breached SLA lead to yourself because you are already the current agent. "
                    "Another agent or supervisor must take ownership."
                )

            lead.write({
                "user_id": self.env.user.id,
                "sla_rescue_user_id": self.env.user.id,
                "sla_rescue_assigned_date": now,
                "sla_rescue_deadline": now + timedelta(hours=rescue_hours),
                "sla_rescue_status": "in_progress",
            })

            if old_agent != self.env.user:
                lead._log_lead_history(
                    "assigned_from_queue",
                    old_agent=old_agent,
                    new_agent=self.env.user,
                    note="Lead picked from SLA Breach Queue"
                )

            lead._log_lead_history(
                "rescue_started",
                new_agent=self.env.user,
                note="Rescue SLA started"
            )

            lead.message_post(
                body=f"Lead assigned to {self.env.user.name}. Rescue SLA started."
            )

        return True

    def action_assign_to_user(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Assign Lead",
            "res_model": "crm.lead",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
            "context": {
                "default_user_id": self.user_id.id,
            },
        }

    def action_set_won(self):
        result = super().action_set_won()

        for lead in self:
            lead.conversion_stage = "won"
            lead.conversion_stage_date = fields.Datetime.now()

            lead._log_lead_history(
                "won",
                new_agent=lead.user_id,
                note="Opportunity marked as won"
            )

        return result

    def action_set_lost(self, **additional_values):
        result = super().action_set_lost(**additional_values)

        for lead in self:
            lead.conversion_stage = "lost"
            lead.conversion_stage_date = fields.Datetime.now()

            lead._log_lead_history(
                "lost",
                new_agent=lead.user_id,
                note="Opportunity marked as lost"
            )

        return result

    def _get_followup_users(self):
        self.ensure_one()
        return [self.user_id] if self.user_id else []

    def _create_followup_activities_for_lead(self):
        activity_type = self.env.ref(
            "mail.mail_activity_data_call",
            raise_if_not_found=False
        )

        for lead in self:
            if not lead.user_id or not lead.next_followup_date:
                continue

            if lead.conversion_stage in ["won", "lost"]:
                continue

            for user in lead._get_followup_users():
                existing_activity = self.env["mail.activity"].search([
                    ("res_model", "=", "crm.lead"),
                    ("res_id", "=", lead.id),
                    ("user_id", "=", user.id),
                    ("summary", "=", "Follow-up Reminder"),
                ], limit=1)

                if existing_activity:
                    continue

                lead.activity_schedule(
                    activity_type_id=activity_type.id if activity_type else False,
                    summary="Follow-up Reminder",
                    note=f"Follow-up reminder for lead: {lead.name}",
                    user_id=user.id,
                    date_deadline=lead.next_followup_date.date(),
                )

                lead._log_lead_history(
                    "followup_created",
                    new_agent=user,
                    note="Follow-up reminder created"
                )

    def _create_escalation_activity(self):
        activity_type = self.env.ref(
            "mail.mail_activity_data_todo",
            raise_if_not_found=False
        )

        for lead in self:
            if not lead.user_id or not lead.user_id.supervisor_id:
                continue

            if lead.conversion_stage in ["won", "lost"]:
                continue

            if lead.sla_rescue_status == "in_progress":
                continue

            if lead.sla_status != "breached" and lead.followup_status != "overdue":
                continue

            supervisor = lead.user_id.supervisor_id

            existing_activity = self.env["mail.activity"].search([
                ("res_model", "=", "crm.lead"),
                ("res_id", "=", lead.id),
                ("user_id", "=", supervisor.id),
                ("summary", "=", "Escalation Required"),
            ], limit=1)

            if existing_activity:
                continue

            lead.activity_schedule(
                activity_type_id=activity_type.id if activity_type else False,
                summary="Escalation Required",
                note=f"Lead requires manager attention: {lead.name}",
                user_id=supervisor.id,
                date_deadline=fields.Date.today(),
            )

            lead._log_lead_history(
                "escalation_created",
                new_agent=supervisor,
                note="Escalation activity created for supervisor"
            )

    def _create_sla_warning_reminder(self):
        activity_type = self.env.ref(
            "mail.mail_activity_data_todo",
            raise_if_not_found=False
        )

        for lead in self:
            if not lead.user_id:
                continue

            existing = self.env["mail.activity"].search([
                ("res_model", "=", "crm.lead"),
                ("res_id", "=", lead.id),
                ("user_id", "=", lead.user_id.id),
                ("summary", "=", "SLA Warning Reminder"),
            ], limit=1)

            if existing:
                continue

            lead.activity_schedule(
                activity_type_id=activity_type.id if activity_type else False,
                summary="SLA Warning Reminder",
                note=f"SLA will breach soon for lead: {lead.name}",
                user_id=lead.user_id.id,
                date_deadline=fields.Date.today(),
            )

            lead._log_lead_history(
                "sla_warning_created",
                new_agent=lead.user_id,
                note="SLA warning reminder created"
            )

    @api.model_create_multi
    def create(self, vals_list):
        leads = super().create(vals_list)

        for lead in leads:
            lead._log_lead_history(
                "lead_created",
                new_agent=lead.user_id,
                note="Lead created"
            )

        leads._create_followup_activities_for_lead()
        leads._create_escalation_activity()

        return leads

    def write(self, vals):
        tracking_data = {}

        for lead in self:
            tracking_data[lead.id] = {}

            for field_name, tracking_config in self.TRACKED_FIELDS.items():
                if field_name in vals and field_name in lead._fields:
                    tracking_data[lead.id][field_name] = {
                        "old": lead[field_name],
                        "event_type": tracking_config[0],
                        "label": tracking_config[1],
                    }

        if "conversion_stage" in vals:
            vals["conversion_stage_date"] = fields.Datetime.now()

        result = super().write(vals)

        for lead in self:
            for field_name, data in tracking_data.get(lead.id, {}).items():
                old_value = data["old"]
                new_value = lead[field_name]

                if str(lead._get_display_value(old_value)) != str(lead._get_display_value(new_value)):
                    lead._log_lead_history(
                        data["event_type"],
                        old_agent=old_value if field_name in ["user_id", "agent_owner_id"] else False,
                        new_agent=new_value if field_name in ["user_id", "agent_owner_id"] else False,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        note=f"{data['label']} changed"
                    )

        trigger_fields = [
            "next_followup_date",
            "user_id",
            "conversion_stage",
            "first_response_date",
            "sla_rescue_status",
        ]

        if any(field in vals for field in trigger_fields):
            self._create_followup_activities_for_lead()
            self._create_escalation_activity()

        return result

    def _cron_create_followup_activities(self):
        now = fields.Datetime.now()

        leads = self.search([
            ("next_followup_date", "!=", False),
            ("next_followup_date", "<=", now),
            ("conversion_stage", "not in", ["won", "lost"]),
        ])

        leads._create_followup_activities_for_lead()
        leads._create_escalation_activity()

    def _cron_check_rescue_sla(self):
        now = fields.Datetime.now()

        leads = self.search([
            ("sla_rescue_status", "=", "in_progress"),
            ("sla_rescue_deadline", "!=", False),
            ("sla_rescue_deadline", "<", now),
            ("conversion_stage", "not in", ["won", "lost"]),
        ])

        for lead in leads:
            lead.sla_rescue_status = "breached"

            lead._log_lead_history(
                "rescue_breached",
                new_agent=lead.sla_rescue_user_id,
                note="Rescue SLA breached"
            )

            lead.message_post(
                body="Rescue SLA breached. Lead returned to SLA Breach Queue."
            )

        leads._create_escalation_activity()

    def _cron_create_sla_warning_reminders(self):
        now = fields.Datetime.now()
        warning_hours = self._get_sla_warning_hours()

        leads = self.search([
            ("user_id", "!=", False),
            ("first_response_date", "=", False),
            ("sla_deadline", "!=", False),
            ("sla_status", "=", "pending"),
            ("conversion_stage", "not in", ["won", "lost"]),
        ])

        for lead in leads:
            warning_time = lead.sla_deadline - timedelta(hours=warning_hours)

            if not (warning_time <= now < lead.sla_deadline):
                continue

            lead._create_sla_warning_reminder()