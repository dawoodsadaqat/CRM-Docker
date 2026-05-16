import json

from odoo import http
from odoo.http import request


class TzPwaController(http.Controller):

    @http.route("/manifest.webmanifest", type="http", auth="public", csrf=False)
    def manifest(self):
        manifest_data = {
            "name": "Techzilla CRM",
            "short_name": "TZ CRM",
            "description": "Techzilla CRM Mobile App",
            "start_url": "/web",
            "scope": "/",
            "display": "standalone",
            "orientation": "portrait",
            "background_color": "#ffffff",
            "theme_color": "#111111",
            "icons": [
                {
                    "src": "/tz_pwa/static/src/img/icon-192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                },
                {
                    "src": "/tz_pwa/static/src/img/icon-512.png",
                    "sizes": "512x512",
                    "type": "image/png"
                }
            ]
        }

        return request.make_response(
            json.dumps(manifest_data),
            headers=[
                ("Content-Type", "application/manifest+json"),
                ("Cache-Control", "no-cache"),
            ],
        )

    @http.route("/service-worker.js", type="http", auth="public", csrf=False)
    def service_worker(self):
        js = """
self.addEventListener("install", function(event) {
    self.skipWaiting();
});

self.addEventListener("activate", function(event) {
    event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", function(event) {
    return;
});
"""
        return request.make_response(
            js,
            headers=[
                ("Content-Type", "application/javascript"),
                ("Service-Worker-Allowed", "/"),
                ("Cache-Control", "no-cache"),
            ],
        )
