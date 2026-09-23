# Independent Air Force career demo

Added September 23, 2026 at `/airforce` (alias `/af`). Public, read-only Flask route with local static assets. No AI generation calls, photo inputs, accounts, saved profiles or form submissions. Existing school and Armie routes retain their behavior.

Ten illustrative careers cover eight interest groupings. Groupings are demo navigation, not assertions about the official taxonomy. The official career URL for every role is in `data/airforce_careers.json` and shown with each roadmap. Public Air Force career pages were checked on September 23, 2026 for role, duties and broad training route. Specific eligibility, AFSCs, training durations, guarantees and current vacancies are not inferred. Cyber terminology must be confirmed with a recruiter. Pilot and developmental engineer use officer routes; engineer specifies a qualifying engineering degree.

School course records reuse `bhs_catalog.py` with per-record corrections from `data/army_catalog_supplement.json`. The catalog source and limitations are visible in the demo. Course connections, project ideas and civilian possibilities are editorial educational suggestions. Grade ranges filter current and future options; prerequisite completion is not assessed. No repeated course or enrollment is prescribed.

Generic AI aviation artwork is labeled in the interface. No Air Force insignia or endorsement claim. Existing patent badge is displayed at 207.5px. The shared True to You wording is included.

Validation: 50 career/grade combinations (10 careers × grades 8–12), officer filter, empty filter combination, all three fictional examples through desktop/mobile coverage, stale-result clearing, official source targets, desktop and 390px mobile layout, no horizontal overflow, print CSS and PDF output, no browser JavaScript errors. Flask responses checked for `/airforce`, `/af`, existing three school pages, privacy and new static assets. Screenshots visually reviewed. Tests used local Chromium and Flask; no production student information or paid services.
