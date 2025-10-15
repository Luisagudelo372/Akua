// Akua Bootstrap behaviors
document.addEventListener('DOMContentLoaded', () => {
  // Chips "active"
  document.querySelectorAll('[data-chip]').forEach(chip => {
    chip.addEventListener('click', () => chip.classList.toggle('active'));
  });

  // Travelers counter
  const dec = document.querySelector('[data-dec]');
  const inc = document.querySelector('[data-inc]');
  const out = document.querySelector('[data-out]');
  if (dec && inc && out){
    let val = parseInt(out.textContent.trim()||'1',10);
    const render = ()=> out.textContent = val;
    dec.addEventListener('click', ()=>{ val = Math.max(1, val-1); render(); });
    inc.addEventListener('click', ()=>{ val = val+1; render(); });
  }

  // Datepicker
  if (window.flatpickr){
    document.querySelectorAll("input[type='date'], .js-date").forEach(el => {
      flatpickr(el, { dateFormat:'Y-m-d' });
    });
  }

  // Tooltips
  if (window.bootstrap){
    const triggers = [].slice.call(document.querySelectorAll('[data-bs-toggle=\"tooltip\"]'));
    triggers.forEach(el => new bootstrap.Tooltip(el));
  }
});
