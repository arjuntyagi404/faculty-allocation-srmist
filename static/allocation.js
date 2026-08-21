let subjectsData = [];
async function loadFaculty() {

    const res = await fetch("/faculty/list");

    const faculty = await res.json();

    const select = document.getElementById("faculty");

    select.innerHTML = "";

    faculty.forEach(f => {

        select.innerHTML += `
            <option value="${f.faculty_id}">
                ${f.username}
            </option>
        `;

    });

}


async function loadSubjects() {

    const res = await fetch("/subjects");

    subjectsData = await res.json();

    const select = document.getElementById("subject");

    select.innerHTML = "";

    subjectsData.forEach(s => {

        select.innerHTML += `
            <option value="${s.subject_code}">
                ${s.subject_name}
            </option>
        `;

    });

    updateClassType();
}
function updateClassType() {

    const subjectCode =
        document.getElementById("subject").value;

    const subject =
        subjectsData.find(
            s => s.subject_code === subjectCode
        );

    const field =
        document.getElementById("classTypeField");

    if (!subject) {
        field.style.display = "none";
        return;
    }

    const courseType =
        subject.course_type;

    if (courseType === "J") {

        field.style.display = "block";

    } else {

        field.style.display = "none";

    }
}

document
    .getElementById("subject")
    .addEventListener(
        "change",
        updateClassType
    );

async function loadAllocations() {

    const res = await fetch("/allocation/list");

    const allocations = await res.json();

    const table = document.getElementById("allocationTable");

    table.innerHTML = "";

    allocations.forEach(a => {

        table.innerHTML += `

        <tr>

            <td>${a.faculty_name}</td>

            <td>${a.subject_name}</td>

            <td>${a.batch}</td>

            <td>${a.section || ""}</td>
                <td>${a.room_number || ""}</td>
                <td>${a.building_name || ""}</td>

            <td>

                <button onclick="editAllocation(${a.id})">

                    Edit

                </button>

                <button onclick="deleteAllocation(${a.id})">

                    Delete

                </button>

            </td>

        </tr>

        `;

    });

}


document
    .getElementById("allocationForm")
    .addEventListener("submit", addAllocation);


async function addAllocation(event) {

    event.preventDefault();

    const body = {

    faculty_id:
        document.getElementById("faculty").value,

    subject_code:
        document.getElementById("subject").value,

    batch:
        Number(document.getElementById("batch").value),

    section:
        document.getElementById("section").value,

    room_number:
        document.getElementById("room_number").value,

    building_name:
        document.getElementById("building_name").value,

    class_type:
        document.getElementById("classType").value

};

    let url = "/allocation/add";
    let method = "POST";

    if (window.editingAllocation) {

        url = "/allocation/edit/" + window.editingAllocation;

        method = "PUT";

    }

    const res = await fetch(url, {

        method,

        headers: {

            "Content-Type": "application/json"

        },

        body: JSON.stringify(body)

    });

    const data = await res.json();

    alert(
        [data.message, data.warning || data.error]
            .filter(Boolean)
            .join("\n")
    );

    if (res.ok) {

        window.editingAllocation = null;

        document.getElementById("allocationForm").reset();

        loadAllocations();

    }

}


async function editAllocation(id) {

    const res = await fetch("/allocation/" + id);

    const allocation = await res.json();

    document.getElementById("faculty").value =
        allocation.faculty_id;

    document.getElementById("subject").value =
        allocation.subject_code;

    document.getElementById("batch").value =
        allocation.batch;

    document.getElementById("section").value =
        allocation.section || "";
    document.getElementById("room_number").value = allocation.room_number || "";
    document.getElementById("building_name").value = allocation.building_name || "";

    window.editingAllocation = id;

}


async function deleteAllocation(id) {

    const confirmed = confirm(
        "Delete this allocation?"
    );

    if (!confirmed)
        return;

    await fetch(
        "/allocation/delete/" + id,
        {
            method: "DELETE"
        }
    );

    loadAllocations();

}


loadFaculty();

loadSubjects();

loadAllocations();