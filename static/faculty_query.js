document.addEventListener("DOMContentLoaded", () => {
    const rows = JSON.parse(document.getElementById("queryData").textContent);
    const forms = document.querySelectorAll(".query-form");
    const labels = {
        availability: ["faculty_name", "subject_code", "subject_name", "venue", "time"],
        faculty: ["faculty_name", "professor_post", "cabin_no", "day", "time", "subject_code", "subject_name", "venue"],
        venue: ["time", "faculty_name", "subject_code", "subject_name"],
    };

    const normalize = value => String(value || "").trim().toLowerCase();

    function matchingRows(form, queryType) {
        const criteria = {};
        form.querySelectorAll("[data-field]").forEach(field => {
            criteria[field.dataset.field] = normalize(field.value);
        });

        return rows.filter(row => Object.entries(criteria).every(([key, value]) => {
            if (!value) return true;
            if (key === "faculty") {
                return normalize(`${row.faculty_name} ${row.faculty_id}`).includes(value);
            }
            return normalize(row[key]).includes(value);
        }));
    }

    function render(queryType, matches) {
        const tbody = document.querySelector(`[data-results="${queryType}"]`);
        const empty = document.querySelector(`[data-empty="${queryType}"]`);
        const count = document.querySelector(`[data-count="${queryType}"]`);
        tbody.innerHTML = matches.map(row => `<tr>${labels[queryType].map(field => `<td>${row[field] || "Venue not assigned"}</td>`).join("")}</tr>`).join("");
        empty.hidden = matches.length !== 0;
        count.textContent = `${matches.length} result${matches.length === 1 ? "" : "s"}`;
    }

    forms.forEach(form => {
        const queryType = form.dataset.query;
        render(queryType, []);
        form.addEventListener("submit", event => {
            event.preventDefault();
            render(queryType, matchingRows(form, queryType));
        });
    });
});