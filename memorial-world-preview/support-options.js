(() => {
'use strict';
const amount = document.getElementById('supportAmount');
const choice = document.getElementById('supportAmountChoice');
const custom = document.getElementById('supportCustomAmount');
if (!amount || !choice || !custom) return;
const wck = document.getElementById('supportWckAmount');
const project = document.getElementById('supportProjectAmount');
const note = document.getElementById('supportAmountNote');
const money = new Intl.NumberFormat('en-US', {style:'currency',currency:'USD'});
function update() {
 const isCustom = choice.value === 'other';
 custom.hidden = !isCustom;
 amount.disabled = !isCustom;
 const value = isCustom ? amount.value.trim() : choice.value;
 const cents = Math.round(Number(value) * 100);
 const valid = value !== '' && (!isCustom || amount.validity.valid) && Number.isSafeInteger(cents) && cents > 0;
 amount.setAttribute('aria-invalid',String(isCustom && !valid && value !== ''));
 if (!valid) {
  wck.textContent = '—'; project.textContent = '—';
  note.textContent = 'Enter a positive amount in US dollars with no more than two decimal places. This is only a preview; no payment is taken.';
  return;
 }
 const charityCents = Math.round(cents * .25);
 wck.textContent = money.format(charityCents / 100);
 project.textContent = money.format((cents - charityCents) / 100);
 note.textContent = 'For ' + money.format(cents / 100) + ', Picturepurdle would donate ' + money.format(charityCents / 100) + ' to WCK and retain ' + money.format((cents - charityCents) / 100) + ' before processing fees and expenses. Amounts are rounded to the nearest cent.';
}
amount.addEventListener('input',update);
choice.addEventListener('change',() => {
 update();
 if (choice.value === 'other') amount.focus();
});
update();
})();
