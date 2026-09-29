(() => {
    const themeToggle = document.querySelector("[data-theme-toggle]");
    const themeIcon = document.querySelector("[data-theme-icon]");
    const themeLabel = document.querySelector("[data-theme-label]");
    const themeMeta = document.querySelector('meta[name="theme-color"]');

    const applyTheme = (theme, persist = false) => {
        const isDark = theme === "dark";
        document.documentElement.dataset.theme = theme;

        if (themeToggle) {
            themeToggle.setAttribute("aria-pressed", String(isDark));
            themeToggle.setAttribute(`aria-label`, `Switch to ${isDark ? "light" : "dark"} theme`);
        }

        if (themeIcon) themeIcon.textContent = isDark ? "☼" : "☾";
        if (themeLabel) themeLabel.textContent = isDark ? "Light mode" : "Dark mode";
        if (themeMeta) themeMeta.content = isDark ? "#111a29" : "#f3f6fa";

        if (persist) {
            try {
                localStorage.setItem("annotation-ops-theme", theme);
            } catch {
                return;
            }
        }
    };

    applyTheme(document.documentElement.dataset.theme === "dark" ? "dark" : "light");
    themeToggle?.addEventListener("click", () => {
        const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
        applyTheme(nextTheme, true);
    });

    const fileInput = document.querySelector("[data-file-input]");
    const dropZone = document.querySelector("[data-drop-zone]");
    const fileStatus = document.querySelector("[data-file-status]");

    if (!fileInput || !dropZone || !fileStatus) return;

    const showSelection = () => {
        const file = fileInput.files && fileInput.files[0];
        fileStatus.textContent = file ? `${file.name} selected` : "No file selected";
    };

    fileInput.addEventListener("change", showSelection);

    ["dragenter", "dragover"].forEach((eventName) => {
        dropZone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropZone.classList.add("is-dragover");
        });
    });

    ["dragleave", "drop"].forEach((eventName) => {
        dropZone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropZone.classList.remove("is-dragover");
        });
    });

    dropZone.addEventListener("drop", (event) => {
        const files = event.dataTransfer && event.dataTransfer.files;
        if (!files || !files.length) return;

        const transfer = new DataTransfer();
        Array.from(files).forEach((file) => transfer.items.add(file));
        fileInput.files = transfer.files;
        showSelection();
    });
})();