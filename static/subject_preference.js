document.addEventListener("DOMContentLoaded", () => {
    const regulation = document.getElementById("regulation");
    const program = document.getElementById("program");
    const department = document.getElementById("department");
    const programStep = document.getElementById("programStep");
    const curriculumStep = document.getElementById("curriculumStep");
    const preferenceForm = document.getElementById("subjectPreferenceForm");
    const validationError = document.getElementById("preferenceValidationError");
    const faSemester = document.getElementById("fa_semester");
    const faCorePreference = document.getElementById("core_preference_1");

    function activateTab(panelId) {
        document.querySelectorAll(".preference-tab").forEach(tab => {
            const isActive = tab.dataset.tab === panelId;
            tab.classList.toggle("is-active", isActive);
            tab.setAttribute("aria-selected", isActive ? "true" : "false");
        });
        document.querySelectorAll(".preference-panel").forEach(panel => {
            const isActive = panel.id === panelId;
            panel.hidden = !isActive;
            panel.classList.toggle("is-visible", isActive);
        });
    }

    function updateSteps() {
        const hasRegulation = regulation.value === "2021";
        const hasProgram = program.value === "UG" || program.value === "PG";
        programStep.hidden = !hasRegulation;
        curriculumStep.hidden = !hasProgram;
        document.querySelectorAll(".curriculum-group").forEach(group => {
            group.hidden = group.dataset.program !== program.value;
        });
    }

    document.querySelectorAll('[data-selector="regulation"] .selector-button[data-value], [data-selector="program"] .selector-button[data-value]').forEach(button => {
        button.addEventListener("click", () => {
            const target = button.closest("[data-selector]").dataset.selector;
            document.getElementById(target).value = button.dataset.value;
            button.closest("[data-selector]").querySelectorAll(".selector-button").forEach(item => item.classList.remove("is-selected"));
            button.classList.add("is-selected");
            if (target === "program") {
                department.value = "";
                document.querySelectorAll(".curriculum-card").forEach(card => card.classList.remove("is-selected"));
            }
            updateSteps();
        });
    });

    document.querySelectorAll(".preference-tab").forEach(tab => {
        tab.addEventListener("click", () => activateTab(tab.dataset.tab));
    });

    document.querySelectorAll(".curriculum-card").forEach(card => {
        card.addEventListener("click", () => {
            department.value = card.dataset.department;
            document.querySelectorAll(".curriculum-card").forEach(item => item.classList.remove("is-selected"));
            card.classList.add("is-selected");
        });
    });

    function updateFaCorePreference() {
        if (!faSemester || !faCorePreference) return;
        const semester = faSemester.value;
        faCorePreference.disabled = !semester;
        if (!semester) faCorePreference.value = "";
        faCorePreference.querySelectorAll("option[data-fa-semesters]").forEach(option => {
            option.hidden = option.dataset.faSemesters !== semester;
        });
        const selectedOption = faCorePreference.selectedOptions[0];
        if (selectedOption && selectedOption.hidden) {
            faCorePreference.value = "";
        }
    }

    if (faSemester) {
        faSemester.addEventListener("change", updateFaCorePreference);
        updateFaCorePreference();
    }

    preferenceForm.addEventListener("submit", event => {
        const groups = ["core", "elective"];
        const hasDuplicate = groups.some(group => {
            const values = Array.from(document.querySelectorAll(`[data-preference-group="${group}"] select`))
                .map(select => select.value)
                .filter(Boolean);
            return new Set(values).size !== values.length;
        });

        const hasFaError = faSemester && !faSemester.value;
        if (hasFaError) {
            event.preventDefault();
            validationError.textContent = "Select the semester for which you are FA.";
            validationError.hidden = false;
        }

        if (hasDuplicate) {
            event.preventDefault();
            validationError.textContent = "Choose different subjects for each preference.";
            validationError.hidden = false;
        } else if (!hasFaError) {
            validationError.hidden = true;
        }
    });

    updateSteps();
});