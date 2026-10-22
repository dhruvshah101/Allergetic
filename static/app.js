const form = document.querySelector('#record-form');
if (form) {
  const section = document.querySelector('#allergies-section');
  const entries = document.querySelector('#allergy-entries');
  const addButton = document.querySelector('#add-allergy');
  const announcement = document.querySelector('#entry-announcement');
  function updateEntries() {
    const active = form.querySelector('[name="status"]:checked')?.value === 'yes';
    section.hidden = !active;
    const rows = [...entries.querySelectorAll('.allergy-entry')];
    rows.forEach((row, index) => {
      row.querySelector('.entry-number').textContent = `ALLERGY ${index + 1}`;
      const remove = row.querySelector('.remove-entry');
      remove.disabled = rows.length === 1;
      remove.setAttribute('aria-label', `Remove allergy ${index + 1}`);
      row.querySelectorAll('input').forEach(input => {
        input.disabled = !active;
        input.required = active && input.name === 'allergen';
        input.id = `${input.name}-${index + 1}`;
        row.querySelector(`label[for^="${input.name}-"]`).htmlFor = input.id;
      });
    });
    addButton.disabled = rows.length >= 30;
  }
  form.querySelectorAll('[name="status"]').forEach(input => input.addEventListener('change', updateEntries));
  addButton.addEventListener('click', () => {
    if (entries.children.length >= 30) return;
    const row = entries.firstElementChild.cloneNode(true);
    row.querySelectorAll('input').forEach(input => { input.value = ''; });
    entries.append(row);
    updateEntries();
    row.querySelector('input').focus();
    announcement.textContent = `${entries.children.length} allergy entries.`;
  });
  entries.addEventListener('click', event => {
    const button = event.target.closest('.remove-entry');
    if (!button || entries.children.length <= 1) return;
    button.closest('.allergy-entry').remove();
    updateEntries();
    addButton.focus();
    announcement.textContent = `Entry removed. ${entries.children.length} allergy entries.`;
  });
  updateEntries();
  document.querySelector('#form-errors')?.focus();
}
document.querySelector('#print-button')?.addEventListener('click', () => window.print());
document.querySelector('#reset-form')?.addEventListener('submit', event => {
  if (!window.confirm('Delete the saved record from this app? This cannot be undone.')) event.preventDefault();
});
