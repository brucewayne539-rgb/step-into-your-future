'use strict';
(() => {
  const data = JSON.parse(document.getElementById('career-data').textContent);
  const $ = id => document.getElementById(id);
  const escape = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const categories = ['Aviation and Flight','Combat and Warfare','Healthcare','Intelligence','Law and Order','Logistics and Administration','Maintenance and Repair','Science and Technology'];
  const icons = {propulsion:'↗', atc:'◎', pilot:'↗', engineer:'◇', cyber:'⌘', medical:'+', intelligence:'◉', logistics:'⇄', security:'◇', sere:'△'};
  categories.forEach(category => $('category').add(new Option(category, category)));
  const demo = JSON.parse($('jet-preview-data').textContent);
  let fictional = false, demoMode = false, portraitBusy = false, portraitVersion = 0;
  const draftKey = 'jetforce-demo-choices';
  const selectedStudent = () => document.querySelector('input[name="jet-student"]:checked').value;
  function showStep(step) {
    $('future-age-choice').hidden = !demoMode;
    $('demo-examples').hidden = !demoMode;
    $('explore-lead').textContent = demoMode ? 'Choose your student, grade, career and future age. One button creates your portrait and roadmap.' : 'Choose your grade and career to explore courses and possible next steps.';
    $('roadmap-title').textContent = demoMode ? 'Your Jet Force future' : 'Your Jet Force roadmap';
    updateChoiceState();
    $('start-view').hidden = step !== 1;
    $('explore-view').hidden = step !== 2;
    $('roadmap').hidden = step !== 3;
    $('progress-bar').style.width = `${step / 3 * 100}%`;
    $('step-label').textContent = `${step} OF 3`;
    $('selected-grade').textContent = `GRADE ${$('grade').value}`;
    const target = step === 3 ? $('roadmap') : step === 2 ? $('explore-view') : $('mainContent');
    target.focus({preventScroll:true});
    window.scrollTo({top:0,behavior:'instant'});
  }
  const role = () => data.roles.find(item => item.id === $('career').value);
  function invalidate() { $('roadmap').hidden = true; portraitVersion++; $('portrait-result').hidden = true; $('future-portrait').removeAttribute('src'); $('download-portrait').removeAttribute('href'); $('portrait-error').hidden = true; }
  function preview() {
    invalidate();
    const item = role();
    updateChoiceState();
    if (!item) {
      $('preview-content').innerHTML = '<div class="preview-icon" aria-hidden="true">↗</div><h3>Broaden your view.</h3><p class="description">This small demo has no career for that combination. Choose “All routes” or “All eight areas” to see more options.</p>';
      return;
    }
    $('preview-content').innerHTML = `<div class="preview-icon" aria-hidden="true">${icons[item.id]}</div><span class="pill">${escape(item.route)} route</span><h3>${escape(item.name)}</h3><p class="tagline">${escape(item.tagline)}</p><p class="description">${escape(item.description)}</p><div class="skills">${item.skills.map(skill => `<span>${escape(skill)}</span>`).join('')}</div>`;
  }
  function filterCareers() {
    const prior = $('career').value;
    const items = data.roles.filter(item => ($('category').value === 'all' || item.category === $('category').value) && ($('route').value === 'all' || item.route === $('route').value));
    $('career').replaceChildren(...items.map(item => new Option(item.name, item.id)));
    if (items.some(item => item.id === prior)) $('career').value = prior;
    if (!items.length) $('career').add(new Option('No demo careers in this combination', ''));
    $('career').disabled = !items.length;
    const narrowed = $('category').value !== 'all' || $('route').value !== 'all';
    $('filter-status').textContent = narrowed
      ? `${items.length} of ${data.roles.length} demo careers shown with your filters. Choose “Show all ${data.roles.length} careers” to explore the full demo.`
      : `All ${data.roles.length} demo careers available. Open the Career menu to choose another.`;
    $('clear-filters').hidden = !narrowed;
    preview();
  }
  function clearFilters() {
    $('category').value = 'all';
    $('route').value = 'all';
    filterCareers();
  }
  function courseCard(course) {
    const record = data.courses[course.key];
    const prerequisites = record.prerequisite || 'No prerequisite recorded in this catalog entry; confirm placement with your counselor.';
    return `<article class="course-card"><p class="grade">GRADES ${record.grades.join(', ')}</p><h5>${escape(record.name)}</h5><p>${escape(course.why)}</p><p class="prereq"><strong>Before choosing:</strong> ${escape(prerequisites)}${record.page ? `<br>BHS catalog, p. ${record.page}.` : ''}</p></article>`;
  }
  function buildRoadmap(event) {
    if (event) event.preventDefault();
    const item = role();
    if (!item) return;
    const grade = Number($('grade').value);
    fictional = demoMode;
    $('fictional-portrait').hidden = !demoMode;
    if (demoMode) {
      const id = document.querySelector('input[name="jet-student"]:checked').value;
      $('student-source').src = `/demo-student/${id}.png`;
      $('student-label').textContent = 'Original fictional student · Grade ' + $('grade').value;
      $('future-heading').textContent = `Future at age ${$('future-age').value}`;
      $('portrait-choice').textContent = item.name;
    }
    const current = item.courses.filter(course => data.courses[course.key].grades.includes(grade));
    const future = item.courses.filter(course => !data.courses[course.key].grades.includes(grade) && data.courses[course.key].grades.some(g => g > grade));
    $('roadmap-context').textContent = `Branford High School · Grade ${grade} · ${item.route} route${fictional ? ' · Fictional example' : ''}`;
    $('sample-note').hidden = !fictional;
    $('result-name').textContent = item.name;
    $('result-description').textContent = item.description;
    $('result-route').textContent = `${item.route} route`;
    $('route-summary').textContent = item.route === 'Officer' ? 'Plan for a bachelor’s degree, an officer commission and competitive specialty selection.' : 'Explore high-school preparation, eligibility, Basic Military Training and specialty training.';
    $('current-heading').textContent = grade === 8 ? 'Your next step in grade 8' : `Options listed for grade ${grade}`;
    $('current-courses').innerHTML = current.length ? current.map(courseCard).join('') : `<p class="empty">${grade === 8 ? 'You are planning ahead for high school. Focus on your current math, science and communication skills, then discuss the BHS options alongside this note with your counselor.' : 'No course in this curated set is listed for your current grade. Ask your counselor about suitable alternatives and next steps.'}</p>`;
    $('future-section').hidden = !future.length;
    document.querySelector('.course-columns').classList.toggle('single', !future.length);
    $('future-courses').innerHTML = future.map(courseCard).join('');
    const steps = item.route === 'Officer' ? [
      ['Build a strong foundation','Explore the school courses above and discuss college preparation, communication and leadership experiences.'],
      ['Degree + commissioning',item.id === 'engineer' ? 'Plan for a qualifying engineering bachelor’s degree. Discuss Air Force ROTC, the Air Force Academy and Officer Training School as possible commissioning routes.' : 'Plan for a bachelor’s degree. Explore Air Force ROTC, the Air Force Academy and Officer Training School as possible commissioning routes.'],
      ['Selection + specialty training',item.training]
    ] : [
      ['School + skill building','Work toward high-school graduation. Explore course options and an approved project or job-shadowing experience.'],
      ['Questions + eligibility','A recruiter can explain current education, testing, medical, citizenship and specialty standards, available jobs and service commitments.'],
      ['Military + specialty training',item.training]
    ];
    $('journey-steps').innerHTML = steps.map(([title,text]) => `<li><h4>${escape(title)}</h4><p>${escape(text)}</p></li>`).join('');
    $('project').textContent = item.project;
    $('questions').replaceChildren(...[item.question, 'Which parts of my school plan would you suggest strengthening, and why?', 'What is the service commitment, and how do Active Duty, Guard and Reserve options differ for this career?'].map(text => {const li = document.createElement('li');li.textContent = text;return li;}));
    $('civilian').textContent = item.civilian;
    $('career-source').href = item.url;
    $('career-source').textContent = `${item.name} — official career details ↗`;
    showStep(3);
  }
  function saveDraft() {
    try { sessionStorage.setItem(draftKey, JSON.stringify({sample:selectedStudent(),grade:$('grade').value,career:$('career').value,age:$('future-age').value,expires:Date.now()+3600000})); } catch (_) {}
  }
  function restoreDraft() {
    try {
      const draft = JSON.parse(sessionStorage.getItem(draftKey) || 'null');
      sessionStorage.removeItem(draftKey);
      if (!draft || draft.expires < Date.now()) return;
      if (demo.samples[draft.sample]) document.querySelector(`input[name="jet-student"][value="${draft.sample}"]`).checked = true;
      if (['8','9','10','11','12'].includes(draft.grade)) $('grade').value = draft.grade;
      if (['22','25','28','30','35'].includes(draft.age)) $('future-age').value = draft.age;
      clearFilters();
      if (data.roles.some(item => item.id === draft.career)) $('career').value = draft.career;
      preview();
    } catch (_) {}
  }
  function updateChoiceState() {
    const item = role();
    $('selected-grade').textContent = `GRADE ${$('grade').value}`;
    $('build').textContent = demoMode ? 'Create My Future →' : 'Show My Roadmap →';
    $('build').disabled = !item || portraitBusy || (demoMode && (!demo.ready || demo.remaining <= 0));
    $('selection-login').hidden = !demoMode || demo.authorized;
    $('demo-readiness').hidden = !demoMode;
    $('demo-readiness').textContent = !demo.ready ? demo.status : demo.remaining <= 0 ? 'This session has used its fictional portrait allowance. You can still explore without a portrait.' : `Ready to create your portrait and roadmap. ${demo.remaining} portrait generation(s) remain in this session.`;
    $('selection-summary').textContent = item ? `${demoMode ? 'Fictional student · ' : ''}Grade ${$('grade').value} · ${item.name}${demoMode ? ' · Future age ' + $('future-age').value : ''}` : 'Choose a career to continue.';
  }
  function enterDemo() {
    if (!demo.authorized) { saveDraft(); window.location.assign('/jetforce/demo'); return; }
    demoMode = true; invalidate(); showStep(2);
  }
  function portraitControls() {
    const hasResult = !$('portrait-result').hidden;
    const hasError = !$('portrait-error').hidden;
    $('edit-course').disabled = portraitBusy;
    $('print').disabled = portraitBusy;
    $('retry-portrait').hidden = portraitBusy || !hasError || !demo.authorized || !demo.ready || demo.remaining <= 0;
    $('portrait-login').hidden = demo.authorized;
    $('portrait-placeholder').hidden = hasResult;
    $('portrait-placeholder').classList.toggle('failed', !portraitBusy);
    $('portrait-status').textContent = portraitBusy ? 'Creating your future portrait… Your roadmap is ready below.' : 'The portrait is not ready yet. Your choices and roadmap are still here.';
    updateChoiceState();
  }
  async function generateFuturePortrait() {
    if (portraitBusy || !demoMode || !demo.ready || demo.remaining <= 0 || !role()) return;
    const version = ++portraitVersion;
    const payload = {mode:'jetforce',school:'bhs',sample_id:selectedStudent(),career:role().id,age:$('future-age').value,grade:$('grade').value,path:'explore',priority:'Doing work I enjoy'};
    portraitBusy = true; $('portrait-error').hidden = true; $('portrait-result').hidden = true; portraitControls();
    try {
      const response = await fetch('/api/admin-preview/generate', {method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':demo.csrf},body:JSON.stringify(payload)});
      const result = await response.json();
      if (response.status === 401 || (response.status === 400 && String(result.error || '').startsWith('This request expired'))) { demo.authorized = false; demo.ready = false; demo.status = 'Your demo session expired. Sign in to continue with these choices.'; saveDraft(); }
      if (!response.ok || !result.ok) throw new Error(result.error || 'The portrait could not be completed. Your roadmap is available below.');
      demo.remaining = result.generations_left;
      if (version !== portraitVersion) return;
      $('future-portrait').src = result.image; $('download-portrait').href = result.image;
      $('portrait-result').hidden = false;
    } catch(error) {
      if (version === portraitVersion) { $('portrait-error').textContent = error.message; $('portrait-error').hidden = false; }
    } finally { portraitBusy = false; portraitControls(); }
  }
  $('start-course').addEventListener('click', () => { demoMode = false; invalidate(); showStep(2); });
  $('demo-toggle').addEventListener('click', enterDemo);
  $('back-start').addEventListener('click', () => showStep(1));
  $('edit-course').addEventListener('click', () => { clearFilters(); showStep(2); });
  $('clear-filters').addEventListener('click', () => { clearFilters(); $('career').focus(); });
  $('category').addEventListener('change', filterCareers);
  $('route').addEventListener('change', filterCareers);
  $('career').addEventListener('change', preview);
  $('grade').addEventListener('change', () => { invalidate(); updateChoiceState(); });
  $('future-age').addEventListener('change', () => { invalidate(); updateChoiceState(); });
  document.querySelectorAll('input[name="jet-student"]').forEach(input => input.addEventListener('change', () => { $('grade').value = demo.samples[selectedStudent()].grade; invalidate(); updateChoiceState(); }));
  $('explorer-form').addEventListener('submit', async event => {
    event.preventDefault();
    if ($('build').disabled) return;
    invalidate(); buildRoadmap();
    if (demoMode) await generateFuturePortrait();
  });
  $('retry-portrait').addEventListener('click', generateFuturePortrait);
  $('portrait-login').addEventListener('click', saveDraft);
  $('selection-login').addEventListener('click', saveDraft);
  $('print').addEventListener('click', () => { document.querySelector('.sources').open = true; window.print(); });
  filterCareers();
  if (demo.open) { restoreDraft(); enterDemo(); }
})();
