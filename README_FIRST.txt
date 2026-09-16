STEP INTO YOUR FUTURE — TODAY!
BHS + GHS SCHOOL-READINESS BUILD V21

V21 provides three clearly separated experiences:
1. No-photo career and course roadmap — available for Grades 8–12.
2. Administrator Preview — live portraits using only two bundled, entirely fictional AI-generated students.
3. Real-student portrait mode — intentionally blocked until provider-retention and school approvals are documented.

UPLOAD
1. Keep the prior V20 ZIP unchanged as the rollback package.
2. Upload the CONTENTS of this folder to the root of the existing GitHub repository. Preserve the templates folder and all documentation files.
3. Commit the upload. Render should deploy automatically.
4. In Render Environment, privately confirm these settings:
   DEMO_ACCESS_CODE = a private administrator/teacher preview code
   SECRET_KEY = a long random session secret
   ADMIN_PREVIEW_ENABLED = 1
   MAX_ADMIN_PREVIEW_GENERATIONS = 6
5. Keep the real-student portrait flags at 0:
   PORTRAITS_ENABLED = 0
   OPENAI_ZDR_CONFIRMED = 0
   SCHOOL_PORTRAIT_APPROVED = 0
6. Open a private/incognito browser window and test:
   BHS: https://step-into-your-future.onrender.com/
   GHS: https://step-into-your-future.onrender.com/ghs
7. Sign in with the private preview code. Confirm the Administrator Preview button appears.
8. Open Administrator Preview, choose either fictional Grade 9 or Grade 11 student, then select a career and future age.
9. Generate one preview in BHS and one in GHS. Try the same fictional student with a second career to demonstrate how the portrait and pathway are changed by the selection.
10. Confirm the generated image is permanently marked FICTIONAL AI DEMONSTRATION and NOT A REAL STUDENT | NOT A PREDICTION.
11. Create no-photo roadmaps for Grade 8 and at least one Grade 9–12 selection in both editions.
12. Open /privacy and /healthz.

REQUIRED PRIVATE SERVER SETTINGS
OPENAI_API_KEY — private server-side key; never commit it to GitHub.
DEMO_ACCESS_CODE — protects the teacher and administrator demonstration.
SECRET_KEY — long random server session secret; Render may already have generated it.
ADMIN_PREVIEW_ENABLED — 1 enables only the fictional Administrator Preview.
MAX_ADMIN_PREVIEW_GENERATIONS — default 6 per signed-in browser session.
MAX_GENERATIONS_PER_SESSION — default 2; applies to future approved real-photo mode.
PRIVACY_CONTACT_EMAIL — required before any real-student portrait can be enabled.
OPERATOR_NAME — public operator name shown on the privacy notice.

IMPORTANT PRIVACY DISTINCTION
Administrator Preview does not accept, upload or process a real student photograph. Its two sample faces are bundled fictional images made for demonstration. Each live transformation still uses the configured image API and is therefore described under the provider's standard API data controls; V21 does not call that a Zero Data Retention workflow.

Real-student portrait mode remains fail-closed. Only an authorized operator should change all three portrait flags to 1 after the evidence and approvals listed in SCHOOL_PILOT_CHECKLIST.md and OPENAI_ZDR_EVIDENCE_REQUEST.md are complete. The flags record configuration; they do not themselves create legal approval.

WHAT V21 ADDS
• Password-protected Administrator Preview for BHS and GHS.
• Two clearly labeled, entirely fictional AI-generated sample students: Grade 9 and Grade 11.
• Live career and future-age transformations without any photo upload control.
• Permanent pixel-level fictional-demo watermark on every preview portrait.
• Separate six-generation administrator-preview limit per signed-in browser session.
• Existing no-photo Grades 8–12 roadmap remains available.
• Existing real-student portrait mode remains privacy-gated and disabled.
• Automated tests cover fictional assets, the upload-free preview page, live mocked generation, watermark handling and BHS school-course results.

DO NOT CLAIM
Do not describe V21 as certified compliant, district approved, patented, patent pending, guaranteed Zero Data Retention or securely wiped. Formal adoption requires district legal, privacy, security, accessibility and curriculum review; applicable agreements; provider evidence; authorization procedures; named contacts; and production operations.

ROLLBACK
Restore the separate V20 package if a deployment problem occurs.
