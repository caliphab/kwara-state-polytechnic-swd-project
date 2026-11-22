document.addEventListener("DOMContentLoaded", () => {
    const flashAlerts = document.querySelectorAll(".flash-alert");

    const dismissAlert = (alert) => {
        alert.classList.add("fade-out");
        setTimeout(() => alert.remove(), 300);
    };

    flashAlerts.forEach((alert) => {
        const closeBtn = alert.querySelector(".flash-close");
        closeBtn?.addEventListener("click", () => dismissAlert(alert));

        setTimeout(() => {
            if (document.body.contains(alert)) {
                dismissAlert(alert);
            }
        }, 5000);
    });


    const headerLoginBtn = document.getElementById("nav-login-btn");

    headerLoginBtn?.addEventListener("click", (e) => {
        const logoutUrl = headerLoginBtn.dataset.logoutUrl;
        if (logoutUrl) {
            window.location.href = logoutUrl;
            return;
        }
        switchToSignin(e);
    });
});