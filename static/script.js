function openModal(id)  { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }

function selectedSpecialRoles(prefix) {
  return Array.from(document.querySelectorAll(`#${prefix}Modal [data-special-role]:checked`))
    .map(input => input.value);
}

function setSpecialRoles(prefix, roles) {
  const selected = new Set(roles.map(role => role.trim()).filter(Boolean));
  const inputs = document.querySelectorAll(`#${prefix}Modal [data-special-role]`);
  inputs.forEach(input => {
    input.checked = selected.has(input.value);
  });
  const group = document.querySelector(`#${prefix}Modal [data-special-role-group]`);
  if (group) updateSpecialRoleState(group);
}

function updateSpecialRoleState(group) {
  group.querySelectorAll('[data-special-role]').forEach(input => {
    input.closest('.special-role-option').classList.toggle('is-selected', input.checked);
  });
}

document.addEventListener('change', event => {
  const input = event.target.closest('[data-special-role]');
  if (!input) return;
  const group = input.closest('[data-special-role-group]');
  const none = group.querySelector('[data-special-role][value="None"]');
  const otherInputs = group.querySelectorAll('[data-special-role]:not([value="None"])');
  if (input.value === 'None' && input.checked) {
    otherInputs.forEach(other => { other.checked = false; });
  } else if (input.value !== 'None' && input.checked) {
    none.checked = false;
  }
  updateSpecialRoleState(group);
});

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

    ,
    professor_post:
      document.getElementById("add_professor_post") ? document.getElementById("add_professor_post").value : undefined,

    special_role: selectedSpecialRoles('add')

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
    if (document.getElementById('edit_professor_post')) {
      document.getElementById('edit_professor_post').value = data.professor_post || 'Assistant Professor';
    }
    setSpecialRoles('edit', (data.special_role || 'None').split(','));
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
  const newPassword = document.getElementById('edit_new_password').value;
  const confirmPassword = document.getElementById('edit_confirm_password').value;
  const msg  = document.getElementById('edit_msg');

  if ((newPassword || confirmPassword) && newPassword !== confirmPassword) {
    msg.textContent = 'New password and confirmation do not match.';
    msg.className   = 'msg error';
    return;
  }

  const body = {
    username: document.getElementById('edit_username').value,
    email:    document.getElementById('edit_email').value,
    contact:  document.getElementById('edit_contact').value
    ,
    professor_post: document.getElementById('edit_professor_post') ? document.getElementById('edit_professor_post').value : undefined,
    special_role: selectedSpecialRoles('edit')
  };
  const res  = await fetch('/faculty/edit/' + id, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  const data = await res.json();
  if (!res.ok) {
    msg.textContent = data.message || data.error;
    msg.className   = 'msg error';
    return;
  }

  if (!newPassword) {
    msg.textContent = data.message;
    msg.className   = 'msg success';
    return;
  }

  const resetRes = await fetch('/faculty/reset-password/' + id, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password: newPassword })
  });
  const resetData = await resetRes.json();
  msg.textContent = resetData.message || resetData.error;
  msg.className   = 'msg ' + (resetRes.ok ? 'success' : 'error');
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
    if (data.professor_post) {
      document.getElementById('remove_professor_post').textContent = '📚 ' + data.professor_post;
    } else {
      document.getElementById('remove_professor_post').textContent = '';
    }
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