(() => {
'use strict';
const amount = document.getElementById('supportAmount');
if (!amount) return;
const wck = document.getElementById('supportWckAmount');
const project = document.getElementById('supportProjectAmount');
const note = document.getElementById('supportAmountNote');
const presets = Array.from(document.querySelectorAll('[data-support-amount]'));
const money = new Intl.NumberFormat('en-US', {style:'currency',currency:'USD'});
function update() {
 const value = amount.value.trim();
 const cents = Math.round(Number(value) * 100);
 const valid = value !== '' && amount.validity.valid && Number.isSafeInteger(cents) && cents > 0;
 presets.forEach(button => button.setAttribute('aria-pressed',String(valid && cents === Number(button.dataset.supportAmount) * 100)));
 amount.setAttribute('aria-invalid',String(!valid));
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
presets.forEach(button => button.addEventListener('click',() => {amount.value=button.dataset.supportAmount;update();}));
update();
})();