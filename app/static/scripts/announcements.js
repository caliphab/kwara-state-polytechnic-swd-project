document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.getElementById("toggle-post-form");
    const postCard = document.getElementById("post-form-card");

    toggleBtn?.addEventListener("click", () => {
        postCard?.classList.toggle("hidden");
    });
});