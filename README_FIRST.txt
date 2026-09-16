STEP INTO YOUR FUTURE — TODAY!
BHS + GHS SCHOOL-READINESS BUILD V20

DO NOT TURN ON HOSTED PORTRAITS YET
V20 intentionally deploys with the complete no-photo roadmap working and hosted portraits blocked. This is the safest school-review configuration.

UPLOAD
1. Keep V19 unchanged as the rollback package.
2. Upload the CONTENTS of this folder to the root of the existing GitHub repository. Preserve the templates folder and all .md evidence/checklist files.
3. Render should deploy automatically.
4. In a private/incognito window, test:
   BHS: https://step-into-your-future.onrender.com/
   GHS: https://step-into-your-future.onrender.com/ghs
5. Create no-photo roadmaps for Grade 8 and at least one Grade 9–12 selection in both editions.
6. Confirm the portrait choice says unavailable pending approval.
7. Open /privacy and /healthz.

REQUIRED SERVER SETTINGS
OPENAI_API_KEY — private server-side key; never commit it.
DEMO_ACCESS_CODE — required before any hosted portrait can be enabled.
SECRET_KEY — long random server session secret; Render blueprint generates it.
MAX_GENERATIONS_PER_SESSION — default 2.
PRIVACY_CONTACT_EMAIL — required before any hosted portrait can be enabled.
OPERATOR_NAME — public operator name on the privacy notice.

FAIL-CLOSED PORTRAIT FLAGS
PORTRAITS_ENABLED=0
OPENAI_ZDR_CONFIRMED=0
SCHOOL_PORTRAIT_APPROVED=0

Keep all three at 0 while the school/provider review is incomplete. Only an authorized operator should set all three to 1 after the corresponding evidence in SCHOOL_PILOT_CHECKLIST.md and OPENAI_ZDR_EVIDENCE_REQUEST.md is complete. The flags document configuration; they do not create legal approval.

WHAT V20 ADDS
• Default no-photo route remains local to the app and uses no OpenAI image request.
• Hosted portraits fail closed until provider-retention, school-approval, contact, access and session conditions are recorded.
• CSRF protection, login/request throttling, 60-minute hosted sessions and stronger browser policy headers.
• Explicit provider-retention acknowledgment and an under-13 portrait prohibition.
• Source-photo browser preview cleared after a request; image references cleared on page exit.
• Expanded technical privacy notice and school-review evidence forms.
• Seven automated test groups; all 630 BHS career/grade/path combinations pass.

DO NOT CLAIM
Do not describe V20 as certified compliant, district approved, patented, patent pending, guaranteed zero retention or securely wiped. Formal adoption requires district legal/privacy/security/accessibility/curriculum review, applicable agreements, provider evidence, authorization procedures, named contacts and production operations.

ROLLBACK
Restore the separate V19 package if a deployment problem occurs. V20 does not overwrite that package.
