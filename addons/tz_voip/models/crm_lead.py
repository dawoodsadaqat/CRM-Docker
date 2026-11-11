import socket

from odoo import _, fields, models
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    call_log_ids = fields.One2many(
        "tz.call.log",
        "lead_id",
        string="Call Logs",
    )

    call_log_count = fields.Integer(
        string="Call Logs",
        compute="_compute_call_log_count",
    )

    def _compute_call_log_count(self):
        for lead in self:
            lead.call_log_count = len(lead.call_log_ids)

    def _get_clean_phone_number(self):
        self.ensure_one()
        phone = self.mobile or self.phone
        if not phone:
            raise UserError(_("No phone/mobile number found on this lead."))

        return phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

    def _get_active_voip_provider(self):
        provider = self.env["tz.voip.provider"].search([
            ("active", "=", True),
            ("company_id", "=", self.env.company.id),
        ], limit=1)

        if not provider:
            raise UserError(_("No active VOIP provider configured."))

        return provider

    def action_voip_call_customer(self):
        self.ensure_one()

        provider = self._get_active_voip_provider()
        phone = self._get_clean_phone_number()
        extension = self.env.user.tz_voip_extension

        if provider.call_mode in ("manual_softphone", "ami_originate") and not extension:
            raise UserError(_("Your user does not have a VOIP extension configured."))

        call_log = self.env["tz.call.log"].sudo().create({
            "name": _("Call to %s") % (self.name or phone),
            "provider_id": provider.id,
            "lead_id": self.id,
            "customer_id": self.partner_id.id if self.partner_id else False,
            "agent_id": self.env.user.id,
            "phone_number": phone,
            "destination_number": phone,
            "source_extension": extension,
            "call_direction": "outgoing",
            "call_status": "not_called",
            "call_datetime": fields.Datetime.now(),
            "started_at": fields.Datetime.now(),
        })

        if provider.call_mode == "tel_link":
            return {
                "type": "ir.actions.act_url",
                "url": "tel:%s" % phone,
                "target": "new",
            }

        if provider.call_mode == "manual_softphone":
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Call Log Created"),
                    "message": _("Now call %s from your softphone extension %s.") % (phone, extension),
                    "type": "success",
                    "sticky": False,
                },
            }

        if provider.call_mode == "ami_originate":
            self._asterisk_ami_originate(provider, extension, phone, call_log)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Call Started"),
                    "message": _("Calling %s using %s.") % (phone, provider.name),
                    "type": "success",
                    "sticky": False,
                },
            }

        raise UserError(_("Unsupported VOIP call mode."))

    def _asterisk_ami_originate(self, provider, extension, phone, call_log):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((provider.host, provider.port))

            login = (
                "Action: Login\r\n"
                "Username: %s\r\n"
                "Secret: %s\r\n\r\n"
            ) % (provider.username, provider.password)

            originate = (
                "Action: Originate\r\n"
                "Channel: PJSIP/%s\r\n"
                "Context: %s\r\n"
                "Exten: %s\r\n"
                "Priority: 1\r\n"
                "CallerID: %s\r\n"
                "Variable: ODOO_CALL_LOG_ID=%s\r\n"
                "Async: true\r\n\r\n"
            ) % (
                extension,
                provider.default_context or "from-internal",
                phone,
                extension,
                call_log.id,
            )

            logout = "Action: Logoff\r\n\r\n"

            sock.sendall(login.encode())
            sock.recv(4096)
            sock.sendall(originate.encode())
            sock.recv(4096)
            sock.sendall(logout.encode())
            sock.close()

        except Exception as exc:
            call_log.write({
                "call_status": "failed",
                "notes": str(exc),
                "ended_at": fields.Datetime.now(),
            })
            raise UserError(_("Asterisk call failed: %s") % str(exc))
    def action_view_call_logs(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Call Logs"),
            "res_model": "tz.call.log",
            "view_mode": "tree,form",
            "domain": [("lead_id", "=", self.id)],
            "context": {
                "default_lead_id": self.id,
                "default_customer_id": self.partner_id.id if self.partner_id else False,
                "default_agent_id": self.env.user.id,
                "default_phone_number": self.mobile or self.phone,
            },
        }    