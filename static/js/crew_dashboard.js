const drafts = [];

function addToTable() {
  const judul = document.getElementById('judul').value.trim();
  const pasal = document.getElementById('pasal').value.trim();
  const isi = document.getElementById('isi').value.trim();
  const penjelasan = document.getElementById('penjelasan').value.trim();

  if (!judul || !pasal || !isi || !penjelasan) {
    alert("Please complete all fields.");
    return;
  }

  drafts.push({ judul, pasal, isi, penjelasan });
  updateTable();
  document.getElementById('draftForm').reset();
}

function updateTable() {
  const tableBody = document.querySelector("#previewTable tbody");
  tableBody.innerHTML = "";

  drafts.forEach((draft, index) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${draft.judul}</td>
      <td>${draft.pasal}</td>
      <td>${draft.isi}</td>
      <td>${draft.penjelasan}</td>
      <td>
        <button onclick="editDraft(${index})">✏️ Edit</button>
        <button onclick="deleteDraft(${index})">❌ Delete</button>
      </td>
    `;
    tableBody.appendChild(row);
  });
}

function editDraft(index) {
  const draft = drafts[index];
  document.getElementById('judul').value = draft.judul;
  document.getElementById('pasal').value = draft.pasal;
  document.getElementById('isi').value = draft.isi;
  document.getElementById('penjelasan').value = draft.penjelasan;
  drafts.splice(index, 1);
  updateTable();
}

function deleteDraft(index) {
  drafts.splice(index, 1);
  updateTable();
}

function prepareFinalSubmit() {
  if (drafts.length === 0) {
    alert("Please add at least one draft.");
    return false;
  }
  document.getElementById('all_drafts').value = JSON.stringify(drafts);
  return true;
}
