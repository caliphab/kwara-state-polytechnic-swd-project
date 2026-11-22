document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.getElementById("toggle-course-form");
    const formCard = document.getElementById("course-form-card");
    toggleBtn?.addEventListener("click", () => formCard?.classList.toggle("hidden"));
});