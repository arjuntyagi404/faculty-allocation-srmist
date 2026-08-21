document.addEventListener("DOMContentLoaded", () => {
    const search = document.getElementById("facultyReportSearch");
    const filters = document.querySelectorAll(".report-filter");
    const cards = document.querySelectorAll(".faculty-report-card");
    const noResults = document.getElementById("facultyReportNoResults");
    const dataKeys = {
        subject: "subjects",
        day: "days",
        time: "times",
        building: "buildings",
        room: "rooms",
        batch: "batches",
        post: "post",
        special_role: "specialRoles",
    };

    const normalize = value => value.trim().toLowerCase();

    function applyFilters() {
        const criteria = {
            faculty: normalize(search.value),
        };

        filters.forEach(filter => {
            criteria[filter.dataset.filter] = normalize(filter.value);
        });

        let visibleCount = 0;

        cards.forEach(card => {
            const matches = Object.entries(criteria).every(([key, value]) => {
                if (!value) {
                    return true;
                }

                const dataValue = card.dataset[dataKeys[key] || key] || "";
                return dataValue.includes(value);
            });

            card.hidden = !matches;
            if (matches) {
                visibleCount += 1;
            }
        });

        noResults.hidden = visibleCount !== 0;
    }

    search.addEventListener("input", applyFilters);
    filters.forEach(filter => {
        filter.addEventListener("change", applyFilters);
    });
});
