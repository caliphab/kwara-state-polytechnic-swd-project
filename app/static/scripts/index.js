document.addEventListener("DOMContentLoaded", () => {
    const authSection = document.querySelector(".auth-section");
    const signupCard = document.querySelector(".auth-signup");
    const signinCard = document.querySelector(".auth-signin");
    const showSigninLink = document.getElementById("show-signin");
    const showSignupLink = document.getElementById("show-signup");
    const headerLoginBtn = document.getElementById("nav-login-btn");
    const heroRegisterBtn = document.getElementById("hero-register-btn");
    const heroLoginBtn = document.getElementById("hero-login-btn");
    const closeAuthBtns = document.querySelectorAll(".close-auth");

    const openModal = () => {
        if (headerLoginBtn?.textContent.trim().toLowerCase() === "logout") {
            return;
        }

        authSection?.classList.add("active");
        document.body.style.overflow = "hidden";
    };

    const closeModal = () => {
        authSection?.classList.remove("active");
        document.body.style.overflow = "";
    };

    const switchToSignin = (e) => {
        if (e) e.preventDefault();
        signupCard?.classList.add("hidden");
        signinCard?.classList.remove("hidden");
        openModal();
    };

    const switchToSignup = (e) => {
        if (e) e.preventDefault();
        signinCard?.classList.add("hidden");
        signupCard?.classList.remove("hidden");
        openModal();
    };

    // Open & switch triggers
    heroRegisterBtn?.addEventListener("click", switchToSignup);
    heroLoginBtn?.addEventListener("click", switchToSignin);
    headerLoginBtn?.addEventListener("click", switchToSignin);
    showSigninLink?.addEventListener("click", switchToSignin);
    showSignupLink?.addEventListener("click", switchToSignup);

    // Close triggers (close button, clicking outside card, or Escape key)
    closeAuthBtns.forEach((btn) => btn.addEventListener("click", closeModal));

    authSection?.addEventListener("click", (e) => {
        if (e.target === authSection) {
            closeModal();
        }
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && authSection?.classList.contains("active")) {
            closeModal();
        }
    });

    // Password visibility toggle
    document.querySelectorAll(".toggle-password").forEach((btn) => {
        btn.addEventListener("click", () => {
            const input = btn.previousElementSibling;
            const icon = btn.querySelector("i");
            const isHidden = input.type === "password";

            input.type = isHidden ? "text" : "password";
            icon.classList.toggle("fa-eye");
            icon.classList.toggle("fa-eye-slash");
        });
    });
});
