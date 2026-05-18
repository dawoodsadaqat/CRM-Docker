/** @odoo-module **/

function updateTitle() {
    if (document.title.includes("Odoo")) {
        document.title = document.title.replaceAll("Odoo", "DEVELVO");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    updateTitle();

    const observer = new MutationObserver(() => {
        updateTitle();
    });

    observer.observe(document.querySelector("title"), {
        childList: true,
    });
});