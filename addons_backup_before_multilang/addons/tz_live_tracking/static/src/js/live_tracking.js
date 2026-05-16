/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class TzLiveTrackingPanel extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");

        this.watchId = null;

        this.state = useState({
            status: "Stopped",
            latitude: "-",
            longitude: "-",
            accuracy: "-",
            lastSent: "-",
        });

        onWillUnmount(() => {
            this.stopTracking();
        });
    }

    startTracking() {
        if (!navigator.geolocation) {
            this.state.status = "GPS not supported";
            this.notification.add("GPS is not supported in this browser.", {
                type: "danger",
            });
            return;
        }

        if (this.watchId !== null) {
            this.notification.add("Tracking is already running.", {
                type: "warning",
            });
            return;
        }

        this.state.status = "Starting...";

        this.watchId = navigator.geolocation.watchPosition(
            async (position) => {
                const payload = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                    battery_level: 100,
                };

                this.state.latitude = payload.latitude;
                this.state.longitude = payload.longitude;
                this.state.accuracy = payload.accuracy;
                this.state.status = "Tracking Active";
                this.state.lastSent = new Date().toLocaleString();

                try {
                    const result = await this.rpc("/api/tz/location/update", payload);

                    if (!result.success) {
                        this.state.status = result.error || "Backend rejected request";
                        this.notification.add(this.state.status, {
                            type: "danger",
                        });
                    } else {
                        console.log("Location sent:", payload);
                    }

                } catch (error) {
                    console.error("Location update failed:", error);
                    this.state.status = "Backend Error";
                    this.notification.add("Location could not be saved.", {
                        type: "danger",
                    });
                }
            },
            (error) => {
                console.error("GPS error:", error);
                this.state.status = "GPS Error: " + error.message;
                this.notification.add(error.message, {
                    type: "danger",
                });
            },
            {
                enableHighAccuracy: true,
                maximumAge: 5000,
                timeout: 10000,
            }
        );

        this.notification.add("Live tracking started.", {
            type: "success",
        });
    }

    async stopTracking() {
        if (this.watchId !== null) {
            navigator.geolocation.clearWatch(this.watchId);
            this.watchId = null;
        }

        this.state.status = "Stopped";

        try {
            await this.rpc("/api/tz/location/stop", {});
        } catch (error) {
            console.error("Stop tracking failed:", error);
        }

        this.notification.add("Live tracking stopped.", {
            type: "info",
        });
    }
}

TzLiveTrackingPanel.template = "tz_live_tracking.LiveTrackingPanel";

registry.category("actions").add("tz_live_tracking_panel", TzLiveTrackingPanel);