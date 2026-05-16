/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("actions").add("tz_call_center.dial_tel", async (env, action) => {
    const phone = action.params.phone;

    if (!phone) {
        env.services.notification.add("No phone number found.", {
            type: "danger",
        });
        return;
    }

    window.location.href = `tel:${phone}`;

    env.services.notification.add(`Calling ${phone}`, {
        type: "info",
    });
});