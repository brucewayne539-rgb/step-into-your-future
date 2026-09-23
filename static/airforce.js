'use strict';
(() => {
  const data = JSON.parse(document.getElementById('career-data').textContent);
  const $ = id => document.getElementById(id);
  const escape = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const categories = ['Aviation and Flight','Combat and Warfare','Healthcare','Intelligence','Law and Order','Logistics and Administration','Maintenance and Repair','Science and Technology'];
  const icons = {propulsion:'↗', atc:'◎', pilot:'↗', engineer:'◇', cyber:'⌘', medical:'+', intelligence:'◉', logistics:'⇄', security:'◇', sere:'△'};
  categories.forEach(category => $('category').add(new Option(category, category)));
  let fictional = false;
  const role = () => data.roles.find(item => item.id === $('career').value);
  function invalidate() { $('roadmap').hidden = true; fictional = false; }
  function preview() {
    invalidate();
    const item = role();
    $('build').disabled = !item;
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
    $('filter-status').textContent = `${items.length} of ${data.roles.length} demo careers shown. Change the filters to explore more.`;
    preview();
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
    $('roadmap').hidden = false;
    $('roadmap').focus({preventScroll:true});
    $('roadmap').scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block:'start'});
  }
  $('category').addEventListener('change', filterCareers);
  $('route').addEventListener('change', filterCareers);
  $('career').addEventListener('change', preview);
  $('grade').addEventListener('change', invalidate);
  $('explorer-form').addEventListener('submit', buildRoadmap);
  document.querySelectorAll('[data-example]').forEach(button => button.addEventListener('click', () => {
    $('category').value = 'all'; $('route').value = 'all'; filterCareers();
    $('grade').value = button.dataset.grade; $('career').value = button.dataset.example; preview();
    fictional = true; buildRoadmap();
  }));
  $('print').addEventListener('click', () => { document.querySelector('.sources').open = true; window.print(); });
  filterCareers();
})();
