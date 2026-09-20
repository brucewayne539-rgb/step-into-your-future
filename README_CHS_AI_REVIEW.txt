CUMBERLAND TEST BRANCH — EDUCATIONAL REVIEW IN PROGRESS

Use chs-ai-review and the separate palonious-chs-test service.
This update is not approved for the live demonstration.

LIVE FINDINGS
The test service now returns real AI output. Direct inspection found a clipped
Cybersecurity summary and unclear AP readiness. Nurse Practitioner failed grade
eligibility; Neurosurgeon exceeded the supporting-elective limit.
None of these three live cases is counted as an educational pass.

THIS CORRECTION
The model output contract now permits only course/year pairs from CHS's actual
catalog, with at most two supporting electives. Course choices and source evidence
are generated before the summary. Unfinished prose is rejected. The second AI
review must assess six separate educational criteria before approving a roadmap.
One correction is allowed, followed by all the same validation and review checks.

TESTS
The included tests use the actual rejected live summary as a regression case,
check every selectable course against remaining grade eligibility, and check
that an overall AI approval cannot override an individual failed review criterion.
These local checks do not establish live educational quality. Live retesting of
this revision and review across grades 8–12 remain required.

INSTALL ON THE TEST BRANCH
Upload the extracted files and folders to chs-ai-review and commit.
Render's separate test service should deploy that commit automatically.
No API key, environment change, paid hosting upgrade or Render Shell is needed.
Keep main and the existing demonstration service unchanged.

The source remains the supplied CHS 2025–26 Program of Studies.
Current-year availability needs school confirmation.
