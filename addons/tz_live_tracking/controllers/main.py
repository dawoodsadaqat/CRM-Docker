import json

from odoo import http, fields
from odoo.http import request


class TzLiveTrackingController(http.Controller):

    def _json(self, data, status=200):
        return request.make_response(
            json.dumps(data),
            headers=[("Content-Type", "application/json")],
            status=status
        )

    def _get_config(self):
        config = request.env["tz.live.tracking.config"].sudo().search([], limit=1)

        if not config:
            config = request.env["tz.live.tracking.config"].sudo().create({
                "name": "Live Tracking Settings",
                "update_interval_seconds": 15,
                "online_threshold_seconds": 300,
                "tracking_enabled": True,
            })

        return config

    @http.route(
        "/api/tz/location/update",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False
    )
    def update_location(self, **kwargs):
        config = self._get_config()

        if not config.tracking_enabled:
            return self._json({
                "success": False,
                "error": "Live tracking is disabled by admin"
            }, 403)

        try:
            payload = json.loads(request.httprequest.data or b"{}")
        except Exception:
            return self._json({
                "success": False,
                "error": "Invalid JSON"
            }, 400)

        token = request.httprequest.headers.get("X-Location-Token")

        if not token:
            return self._json({
                "success": False,
                "error": "Missing location token"
            }, 401)

        user = request.env["res.users"].sudo().search([
            ("tz_location_token", "=", token),
            ("active", "=", True),
        ], limit=1)

        if not user:
            return self._json({
                "success": False,
                "error": "Invalid location token"
            }, 401)

        if not user.tz_location_tracking_enabled:
            return self._json({
                "success": False,
                "error": "Location tracking disabled for this user"
            }, 403)

        latitude = payload.get("latitude")
        longitude = payload.get("longitude")

        if latitude is None or longitude is None:
            return self._json({
                "success": False,
                "error": "Latitude and longitude are required"
            }, 400)

        Location = request.env["tz.user.location"].sudo()

        location = Location.search([
            ("user_id", "=", user.id)
        ], limit=1)

        vals = {
            "user_id": user.id,
            "latitude": float(latitude),
            "longitude": float(longitude),
            "accuracy": float(payload.get("accuracy") or 0),
            "battery_level": float(payload.get("battery_level") or 0),
            "last_seen": fields.Datetime.now(),
        }

        if location:
            location.write(vals)
        else:
            location = Location.create(vals)

        return self._json({
            "success": True,
            "user": user.name,
            "location_id": location.id,
            "interval_seconds": config.update_interval_seconds,
            "last_seen": str(location.last_seen),
        })

    @http.route(
        "/api/tz/location/config",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False
    )
    def location_config(self, **kwargs):
        config = self._get_config()

        return self._json({
            "success": True,
            "tracking_enabled": config.tracking_enabled,
            "update_interval_seconds": config.update_interval_seconds,
            "online_threshold_seconds": config.online_threshold_seconds,
        })

    @http.route(
        "/tz/location/share/<string:token>",
        type="http",
        auth="public",
        csrf=False
    )
    def location_share_page(self, token, **kwargs):
        config = self._get_config()

        user = request.env["res.users"].sudo().search([
            ("tz_location_token", "=", token),
            ("active", "=", True),
        ], limit=1)

        if not user:
            return request.make_response(
                "<h2>Invalid or expired tracking token.</h2>",
                headers=[("Content-Type", "text/html")]
            )

        interval = config.update_interval_seconds or 15

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Techzilla Live Tracking</title>
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f4f4f4;
            margin: 0;
            padding: 16px;
        }}
        .box {{
            max-width: 520px;
            margin: auto;
            background: white;
            padding: 22px;
            border-radius: 14px;
            box-shadow: 0 4px 18px rgba(0,0,0,0.08);
        }}
        h2 {{
            margin-top: 0;
        }}
        button {{
            width: 100%;
            padding: 14px;
            margin-top: 10px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
        }}
        .start {{
            background: #111827;
            color: white;
        }}
        .stop {{
            background: #dc2626;
            color: white;
        }}
        .status {{
            margin-top: 18px;
            padding: 12px;
            background: #f9fafb;
            border-radius: 8px;
            font-size: 14px;
            line-height: 1.6;
        }}
        .ok {{
            color: green;
            font-weight: bold;
        }}
        .err {{
            color: red;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="box">
        <h2>Techzilla Live Tracking</h2>
        <p>User: <strong>{user.name}</strong></p>
        <p>Keep this page open. Your GPS location will be updated every <strong>{interval}</strong> seconds.</p>

        <button class="start" onclick="startTracking()">Start Tracking</button>
        <button class="stop" onclick="stopTracking()">Stop Tracking</button>

        <div class="status" id="status">
            Waiting for permission...
        </div>
    </div>

    <script>
        const TOKEN = "{token}";
        let intervalSeconds = {interval};
        let timer = null;

        async function sendLocation() {{
            if (!navigator.geolocation) {{
                document.getElementById("status").innerHTML =
                    "<span class='err'>GPS is not supported on this device/browser.</span>";
                return;
            }}

            navigator.geolocation.getCurrentPosition(async function(pos) {{
                const payload = {{
                    latitude: pos.coords.latitude,
                    longitude: pos.coords.longitude,
                    accuracy: pos.coords.accuracy,
                    battery_level: 0
                }};

                try {{
                    const response = await fetch("/api/tz/location/update", {{
                        method: "POST",
                        headers: {{
                            "Content-Type": "application/json",
                            "X-Location-Token": TOKEN
                        }},
                        body: JSON.stringify(payload)
                    }});

                    const data = await response.json();

                    if (data.success) {{
                        if (data.interval_seconds) {{
                            intervalSeconds = data.interval_seconds;
                        }}

                        document.getElementById("status").innerHTML =
                            "<span class='ok'>Location updated successfully</span><br/>" +
                            "Latitude: " + payload.latitude + "<br/>" +
                            "Longitude: " + payload.longitude + "<br/>" +
                            "Accuracy: " + payload.accuracy + " meters<br/>" +
                            "Last Update: " + new Date().toLocaleTimeString();
                    }} else {{
                        document.getElementById("status").innerHTML =
                            "<span class='err'>Error: " + data.error + "</span>";
                    }}
                }} catch (error) {{
                    document.getElementById("status").innerHTML =
                        "<span class='err'>Failed to send location to server.</span>";
                }}
            }}, function(error) {{
                document.getElementById("status").innerHTML =
                    "<span class='err'>Location permission denied or GPS unavailable.</span>";
            }}, {{
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }});
        }}

        function startTracking() {{
            sendLocation();

            if (timer) {{
                clearInterval(timer);
            }}

            timer = setInterval(sendLocation, intervalSeconds * 1000);

            document.getElementById("status").innerHTML =
                "Tracking started. Waiting for GPS update...";
        }}

        function stopTracking() {{
            if (timer) {{
                clearInterval(timer);
                timer = null;
            }}

            document.getElementById("status").innerHTML =
                "Tracking stopped on this device.";
        }}
    </script>
</body>
</html>
        """

        return request.make_response(
            html,
            headers=[("Content-Type", "text/html")]
        )