/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

function getCurrentPosition() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error("Geolocation is not supported by this browser."));
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => resolve(position),
            (error) => reject(error),
            {
                enableHighAccuracy: true,
                timeout: 15000,
                maximumAge: 0,
            }
        );
    });
}

registry.category("actions").add("tz_site_visit.capture_meeting_location", async (env, action) => {
    const notification = env.services.notification;
    const orm = env.services.orm;

    const eventId = action.params.event_id;

    if (!eventId) {
        notification.add(_t("Meeting must be saved before capturing location."), {
            type: "danger",
        });
        return;
    }

    try {
        const position = await getCurrentPosition();

        const latitude = position.coords.latitude;
        const longitude = position.coords.longitude;

        const mapUrl = `https://www.google.com/maps?q=${latitude},${longitude}`;

        await orm.write("calendar.event", [eventId], {
            meeting_latitude: latitude,
            meeting_longitude: longitude,
            in_person_location: mapUrl,
            meeting_location_captured_at: new Date().toISOString().slice(0, 19).replace("T", " "),
        });

        notification.add(_t("Latest current location captured successfully."), {
            type: "success",
        });

        window.location.reload();

    } catch (error) {
        notification.add(_t("Could not capture location. Allow browser location permission and try again."), {
            type: "danger",
        });
    }
});