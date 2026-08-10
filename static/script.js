function openModal(id)  { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }

// ADD
async function addFaculty() {
  const body = {

    faculty_id:
        document.getElementById("add_faculty_id").value,

    username:
        document.getElementById("add_username").value,

    email:
        document.getElementById("add_email").value,

    contact:
        document.getElementById("add_contact").value,

    password:
        document.getElementById("add_password").value

}
  const res  = await fetch('/faculty/add', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  const data = await res.json();
  const msg  = document.getElementById('add_msg');
  msg.textContent = data.message || data.error;
  msg.className   = 'msg ' + (res.ok ? 'success' : 'error');
  }

// SEARCH for edit
async function searchFaculty() {
  const id  = document.getElementById('edit_search_id').value;
  const res = await fetch('/faculty/' + id);
  const data = await res.json();
  const msg  = document.getElementById('edit_msg');
  if (res.ok) {
    document.getElementById('edit_username').value = data.username;
    document.getElementById('edit_email').value    = data.email;
    document.getElementById('edit_contact').value  = data.contact;
    document.getElementById('edit_fields').style.display = 'block';
    msg.textContent = '';
  } else {
    msg.textContent = data.error;
    msg.className   = 'msg error';
  }
}

// EDIT
async function editFaculty() {
  const id   = document.getElementById('edit_search_id').value;
  const body = {
    username: document.getElementById('edit_username').value,
    email:    document.getElementById('edit_email').value,
    contact:  document.getElementById('edit_contact').value
  };
  const res  = await fetch('/faculty/edit/' + id, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  const data = await res.json();
  const msg  = document.getElementById('edit_msg');
  msg.textContent = data.message || data.error;
  msg.className   = 'msg ' + (res.ok ? 'success' : 'error');
}

// PREVIEW before remove
async function previewRemove() {
  const id  = document.getElementById('remove_id').value;
  const res = await fetch('/faculty/' + id);
  const data = await res.json();
  const msg  = document.getElementById('remove_msg');
  if (res.ok) {
    document.getElementById('remove_name').textContent  = '👤 ' + data.username;
    document.getElementById('remove_email').textContent = '✉️ ' + data.email;
    document.getElementById('remove_preview').style.display = 'block';
    document.getElementById('confirm_remove_btn').style.display = 'inline-block';
    msg.textContent = '';
  } else {
    msg.textContent = data.error;
    msg.className   = 'msg error';
  }
}

// REMOVE
async function removeFaculty() {
  const id  = document.getElementById('remove_id').value;
  const res = await fetch('/faculty/remove/' + id, { method: 'DELETE' });
  const data = await res.json();
  const msg  = document.getElementById('remove_msg');
  msg.textContent = data.message || data.error;
  msg.className   = 'msg ' + (res.ok ? 'success' : 'error');
  if (res.ok) {
    document.getElementById('remove_preview').style.display = 'none';
    document.getElementById('confirm_remove_btn').style.display = 'none';
  }
}