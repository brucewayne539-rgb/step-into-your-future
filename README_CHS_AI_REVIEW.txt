PALONIOUS — CUMBERLAND EDUCATIONAL INTELLIGENCE
Review candidate • 20 September 2026 • Not yet approved for demonstrations

WHAT CHANGED
Cumberland now uses AI educational reasoning and a second AI review on every
Generate request. The old career-keyword matcher has been removed. Course
names, grades, prerequisites and page references come from the supplied CHS
2025–26 Program of Studies. The source contains 157 detailed course entries;
152 can be suggested without making an unsupported placement assumption.
Prerequisites contained in graphics were checked visually and incorporated.
Current-year course availability has NOT been verified.

The same engine serves /chs, /api/chs/roadmap, /api/chs/generate and the
CHS Administrator Demo. A rejected or unavailable roadmap stops the request;
it never substitutes a generic list or starts a paid portrait first.

The approved CHS hero/icon, both fictional students, BHS and GHS pages and
catalog data are preserved. Armie's career data is unchanged. Path/priority
questions were removed from the CHS student screen to honor the prior decision
to personalize from school, grade and career. Legacy API fields remain accepted.

TEST STATUS
748 local tests and 262 subtests passed. These include 15 human-authored
priority-career examples, adversarial catalog/grade/sequence checks, API failure
handling, all 210 CHS route combinations, 420 existing BHS/GHS combinations,
CHS administrator/portrait integration and real SDK HTTP serialization using a
mock transport. Simulated AI is clearly isolated in tests/ and never used at runtime.
15 result screens also passed DOM interaction checks, including prerequisites,
supporting choices, senior-year sections, escaping and failed-request recovery.
Browser screenshot checks could not run because the browser download failed.

LIVE AI QUALITY STATUS: NOT TESTED. This development workspace has no API key.
Local passing tests do not establish that live model recommendations are good.
The included live runner creates real results and a readable educational-review
packet; it must be run and reviewed before this candidate is demonstration-ready.

SIMPLE GITHUB / RENDER TEST INSTRUCTIONS
1. In your existing GitHub repository, create a new branch named chs-ai-review.
2. Extract this ZIP. On that branch, upload the contents of the extracted folder,
   including data/, templates/, tests/ and scripts/. Upload the files, not the ZIP.
3. In Render, create a separate Web Service connected to chs-ai-review. Use:
   Build: pip install -r requirements.txt
   Start: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 300
   Configure its OPENAI_API_KEY and SECRET_KEY in Render. Keep the existing
   portrait/privacy settings. ROADMAP_MODEL defaults to gpt-4.1;
   ROADMAP_REVIEW_MODEL defaults to the same model.
4. Open the test service's /chs and /admin-preview?school=chs pages.
   In the test service's Render Shell, run:
   python scripts/evaluate_chs_live.py --scope priority --output chs-live-review
   This evaluates the three priority careers in grades 8–12 and writes
   chs-live-review/review.html and results.json. Open the HTML for educational review.
   It makes up to 30 paid text API calls and no portrait calls.
5. After priority defects are resolved, run the full career bank:
   python scripts/evaluate_chs_live.py --scope all --output chs-live-review-all
   This makes up to 420 paid text API calls; --repeat 2 or 3 tests consistency.
   Review the actual outputs before considering a merge into the live branch.

Do not replace the current demonstration site with this candidate yet.
No GitHub or Render deployment has been performed for you.

LOCAL TEST COMMAND
pip install -r requirements-test.txt
python -m pytest -q

PRIVACY / OPERATIONS CHANGE
CHS photo-free roadmaps now use paid text API calls. Only school, grade, career,
public catalog information and generated roadmap text are sent; no student name,
photo or transcript is sent to the text planner. Calls set store=false. This is
not a claim of provider zero retention. The privacy page was updated accordingly.
The existing real-photo approval gates remain in effect. Text timeouts have no
automatic paid retry, and the server timeout allows planning/review before images.

SOURCE NOTES
Detailed course entries take precedence over suggested pathway-chart timing.
Printed-page numbers differ from PDF viewer page numbers by one.
The Biomedical Innovation prerequisite graphic contains inconsistent wording;
the record flags this for department confirmation. CNA says it begins Fall 2026;
the app does not assume that confirms present availability.

Implementation references:
https://developers.openai.com/api/docs/guides/structured-outputs
https://developers.openai.com/api/docs/models/gpt-4.1
Career training anchors:
https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm
https://www.bls.gov/ooh/healthcare/nurse-anesthetists-nurse-midwives-and-nurse-practitioners.htm
https://www.bls.gov/ooh/computer-and-information-technology/information-security-analysts.htm

OPTIONAL DOM TEST (requires Node.js)
npm install --no-save jsdom
python scripts/render_chs_test_html.py
node tests/test_chs_ui.cjs
This tests DOM behavior with simulated API responses, not visual browser rendering.
