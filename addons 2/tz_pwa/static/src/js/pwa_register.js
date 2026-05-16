/** @odoo-module **/

if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
        navigator.serviceWorker
            .register("/service-worker.js", { scope: "/" })
            .then(function () {
                console.log("TZ PWA service worker registered");
            })
            .catch(function (error) {
                console.warn("TZ PWA service worker failed", error);
            });
    });
}
