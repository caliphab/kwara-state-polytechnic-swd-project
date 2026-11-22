document.addEventListener("DOMContentLoaded", () => {
    const photoInput = document.getElementById("photo-input");
    const photoPreview = document.getElementById("photo-preview");
    const fileNameDisplay = document.getElementById("file-name-display");

    photoInput?.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (file) {
            fileNameDisplay.textContent = `Selected: ${file.name}`;
            const reader = new FileReader();
            reader.onload = (event) => {
                photoPreview.src = event.target.result;
            };
            reader.readAsDataURL(file);
        }
    });
});