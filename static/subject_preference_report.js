document.addEventListener("DOMContentLoaded", () => {
    const search = document.getElementById("preferenceReportSearch");
    const filters = document.querySelectorAll(".preference-report-filter");
    const rows = document.querySelectorAll(".preference-report-row");
    const noResults = document.getElementById("preferenceReportNoResults");

    const normalize = value => value.trim().toLowerCase();

    function applyFilters() {
        const criteria = {
            faculty: normalize(search.value),
        };

        filters.forEach(filter => {
            criteria[filter.dataset.filter] = normalize(filter.value);
        });

        let visibleCount = 0;

        rows.forEach(row => {
            const matches = Object.entries(criteria).every(([key, value]) => {
                if (!value) {
                    return true;
                }

                return (row.dataset[key] || "").toLowerCase().includes(value);
            });

            row.hidden = !matches;
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