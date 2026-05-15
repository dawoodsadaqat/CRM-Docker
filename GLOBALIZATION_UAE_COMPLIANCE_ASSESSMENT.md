# GLOBALIZATION + UAE COMPLIANCE FOUNDATION Assessment

## Phase A: Custom module assessment

| Module | Models touched | UAE compliance impact | Globalization impact | Required change | Risk level |
|---|---|---|---|---|---|
| tz_accounting_extension | account.move, tz.commission | High | High | Centralized invoice posting validation from tz_global_compliance | High |
| tz_api_gateway | tz.api.log, tz.lead.config, tz.lead.integration, tz.lead.routing.rule | High | High | Use crm/account compliance constraints for API-created records; add compliance flag on api log | High |
| tz_attendance_geo | hr.attendance | Low | Medium | Compatibility only, no VAT logic | Low |
| tz_call_center | tz.call.log, crm.lead | Medium | Medium | Non-orphan integrity check for call context | Medium |
| tz_commission | tz.commission, milestones, clawbacks | High | High | VAT and company consistency constraints | High |
| tz_crm_base | crm.lead | Medium | High | Lead company/customer-company consistency constraints | Medium |
| tz_dashboard | dashboard models, res.users, crm.lead | Medium | High | No code change; requires metric validation under multi-company/multi-currency in UAT | Medium |
| tz_expense_extension | hr.expense | Medium | High | Lead-expense company consistency constraint | Medium |
| tz_hr_extension | hr.employee, res.users | Low | High | Compatibility only; retain existing role boundaries | Medium |
| tz_lead_assignment | crm.lead, routing rules | Low | High | Compatibility only through lead constraints | Low |
| tz_live_tracking | tz.user.location, history, config, res.users | Low | High | Compatibility only; existing rules should isolate data | Medium |
| tz_payroll | tz.payroll, tz.payroll.line | Medium | High | Payroll line employee-company consistency constraint | Medium |
| tz_property_inventory | property project/building/unit/listing, crm.lead | Medium | High | Project company/country support and listing currency propagation | High |
| tz_realestate_leads | crm.lead | Medium | High | Covered by central lead constraints | Low |
| tz_site_visit | tz.site.visit, crm.lead | Low | Medium | Keep lead/customer context checks | Low |
| tz_whatsapp | tz.whatsapp.message, crm.lead | Low | Medium | Keep lead/customer context checks | Low |

## Phase B: Odoo standard-first mapping
- Multi-language/translations: handled by standard Odoo language installation/translations.
- Multi-currency and rates: handled by core accounting currencies/rates.
- Multi-company access and allowed companies: handled by core users/company settings.
- Country-specific taxes and invoice tax lines: handled by core account and localization templates.
- Partner/company VAT fields: standard `vat` on `res.partner` and `res.company` reused as TRN.

## Phase C-F implementation summary
- Added `tz_global_compliance` module for centralized enforcement/checks.
- Added UAE invoice posting controls, TRN format validation, compliance mode (UAE/Saudi/International), ZATCA placeholder note, and cross-module consistency checks on CRM, property, commission, expense, payroll, and communication activity context.
