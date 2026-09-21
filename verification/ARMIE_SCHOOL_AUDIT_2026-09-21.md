# Armie school-course review — 21 September 2026

Scope: 262 selectable Army careers, BHS and GHS, Grades 8–12 (2,620 combinations). Applies to `/armie` and `/armie/pilot-demo`, which share the generation endpoint. CHS and the standalone BHS/GHS explorers retain their existing course logic and appearance.

## Changes

- Explicit assignments to 54 occupational preparation profiles replace the civilian-career shortcut for BHS/GHS Armie results. No keyword or generic fallback is used for these recommendations.
- Separate operational aviation, ATC, aircraft mechanics, electronics, chemical laboratories, biological laboratories, clinical care, nutrition, optical fabrication, languages, music and other occupational needs.
- Original supplied BHS/GHS catalogs used to add missing music, language and nutrition courses and correct selected titles, grades and prerequisites. Source file hashes are in `armie_catalog_sources.json`; overlays cite printed page numbers.
- BHS Chemistry I now shows Algebra I credit; AP Chemistry II shows Chemistry I Honors. BHS PE is split by actual grade instead of a single broad label. GHS Spanish 1 and French 2 are not recommended to seniors.
- Each course retains school-specific grade availability and entry requirements. Grade 8 receives planning options; Grade 12 does not receive courses restricted to earlier grades or future high-school years.
- Recommendations, projects and next steps refer to the selected Army role. They no longer inherit physician, actor or engineer advice from unrelated civilian careers.
- Existing visuals, dropdowns, fictional photos and portrait limits are unchanged.

## Verification

`tests/test_army_school_audit.py` exercises all 2,620 combinations directly AND all 2,620 through the real Flask generation route. Only paid image generation is mocked; course selection, catalog handling and response serialization execute normally. No paid image requests were needed.

Additional tests assert required and forbidden courses for independently specified high-risk examples, original-catalog prerequisites and grade restrictions, and rejection of unmapped future job additions. Existing preview and BHS tests pass. Focused run: **5,306 tests passed plus 4,230 existing subtests**.

Wider repository regression: **6,586 tests passed plus 4,230 subtests; one SDK serialization test could not run because the local OpenAI package is absent**. Installing that existing dependency was blocked by the package network. This does not establish a deployed SDK failure. Runtime dependency requirements and image-generation code were not changed.

A passing structural test is not proof of educational quality; the semantic cases, explicit role manifest and original-catalog review are separate evidence. Original normalized catalog entries are retained where not overridden. This is not an exhaustive new transcription of either catalog or school/Army approval.

## Limits

The app does not collect a transcript, completed prerequisites, language level or instrument proficiency. It must not claim verified enrollment eligibility or recommend repeating completed coursework. Courses are alternatives to discuss with the counselor, not a schedule or required checklist. Confirm current school offerings and placement. Military professional education, selection and qualifications remain role-specific and require official verification.

The UI supports BHS and GHS for Armie. The legacy CHS API compatibility mapping remains outside this audit. No claim is made that this review validates every professional qualification or Army training timeline.

## Deployment identification

`/healthz` returns `armie_course_revision: armie-school-review-2026-09-21-v1` after this build is live. This identifies loaded course code; it does not by itself test an authenticated paid portrait request.
