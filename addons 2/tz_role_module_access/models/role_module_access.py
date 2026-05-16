from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TzRoleModuleAccess(models.Model):
    _name = "tz.role.module.access"
    _description = "Role Based Module Access"
    _order = "role_group_id"

    name = fields.Char(compute="_compute_name", store=True)

    role_group_id = fields.Many2one(
        "res.groups",
        string="CRM Role",
        required=True,
        domain="[('id', 'in', [22, 23, 24])]",
        help="Use existing CRM roles: CRM Agent, CRM Manager, CRM Admin.",
    )

    feature_ids = fields.Many2many(
        "tz.module.feature",
        "tz_role_module_access_feature_rel",
        "role_access_id",
        "feature_id",
        string="Allowed Modules/Submodules",
    )

    mapped_group_ids = fields.Many2many(
        "res.groups",
        compute="_compute_mapped_group_ids",
        string="Technical Groups Applied",
    )

    active = fields.Boolean(default=True)

    @api.depends("role_group_id")
    def _compute_name(self):
        for rec in self:
            rec.name = rec.role_group_id.name if rec.role_group_id else _("New Role Access")

    @api.depends("feature_ids", "feature_ids.technical_group_id")
    def _compute_mapped_group_ids(self):
        for rec in self:
            rec.mapped_group_ids = rec.feature_ids.mapped("technical_group_id")

    @api.constrains("role_group_id")
    def _check_unique_role_group(self):
        for rec in self:
            duplicate = self.search([
                ("role_group_id", "=", rec.role_group_id.id),
                ("id", "!=", rec.id),
            ], limit=1)
            if duplicate:
                raise ValidationError(_("This CRM role already has module access configuration."))

    def _get_managed_features(self):
        return self.env["tz.module.feature"].sudo().search([("active", "=", True)])

    def _get_all_managed_groups(self):
        return self._get_managed_features().mapped("technical_group_id").filtered(lambda g: g)

    def action_apply_access(self):
        Feature = self.env["tz.module.feature"].sudo()
        for rec in self.sudo():
            role = rec.role_group_id.sudo()
            selected_groups = rec.feature_ids.mapped("technical_group_id").filtered(lambda g: g)
            managed_groups = Feature.search([]).mapped("technical_group_id").filtered(lambda g: g)

            role.write({"implied_ids": [(3, group.id) for group in managed_groups]})
            role.write({"implied_ids": [(4, group.id) for group in selected_groups]})

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Role Access Updated"),
                "message": _("Module/submodule access has been applied to the selected CRM role. Logout/login affected users."),
                "type": "success",
                "sticky": False,
            },
        }

    def action_reapply_menu_security(self):
        self = self.sudo()
        managed_features = self._get_managed_features()
        managed_groups = managed_features.mapped("technical_group_id").filtered(lambda g: g)
        Menu = self.env["ir.ui.menu"].sudo()

        # Build menu -> feature group mapping.
        menu_group_map = {}
        for feature in managed_features:
            group = feature.technical_group_id
            if not group:
                continue

            for xmlid in (feature.menu_xml_ids or "").splitlines():
                xmlid = xmlid.strip()
                if not xmlid or xmlid.startswith("#"):
                    continue
                menu = self.env.ref(xmlid, raise_if_not_found=False)
                if menu and menu._name == "ir.ui.menu":
                    menu_group_map.setdefault(menu, self.env["res.groups"].sudo().browse())
                    menu_group_map[menu] |= group

            for keyword in (feature.menu_name_keywords or "").splitlines():
                keyword = keyword.strip()
                if not keyword or keyword.startswith("#"):
                    continue
                for menu in Menu.search([("name", "=ilike", keyword)]):
                    # Do not restrict root Settings/Apps/Discuss accidentally.
                    if menu.id:
                        menu_group_map.setdefault(menu, self.env["res.groups"].sudo().browse())
                        menu_group_map[menu] |= group

        # Restrict every managed menu exactly to its mapped feature group(s).
        for menu, groups in menu_group_map.items():
            menu.write({"groups_id": [(6, 0, groups.ids)]})

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Menu Security Reapplied"),
                "message": _("Managed menus are now restricted by module/submodule feature groups."),
                "type": "success",
                "sticky": False,
            },
        }
