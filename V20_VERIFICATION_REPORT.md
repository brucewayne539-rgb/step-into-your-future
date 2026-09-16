# V20 Verification Report

Verified September 16, 2026. This is engineering evidence, not a legal, security, accessibility or procurement certification.

## Automated results

- 7 of 7 Python unit/integration tests pass.
- All 630 BHS career × grade × pathway combinations return a complete, grade-safe roadmap.
- A write request without a CSRF token is rejected.
- Hosted portrait mode fails closed when required school/provider evidence flags are absent.
- The status response exposes no provider key or access code.
- The no-photo roadmap remains available without an OpenAI image request.
- Python compilation passes.
- Installed Python dependencies report no broken requirements.
- Rendered BHS, GHS and privacy pages have no duplicate IDs, missing image alternatives, unlabeled controls, empty buttons or data tables lacking headers under the project’s static audit.
- Extracted BHS and GHS JavaScript passes `node --check`.

## Manual/external verification still required

- District privacy/legal, IT/security, procurement, curriculum/counseling and accessibility approval.
- Project-specific written OpenAI ZDR evidence and provider agreement review before portraits.
- Manual keyboard, screen-reader, zoom/reflow, contrast and user testing.
- Independent vulnerability/dependency review and risk-appropriate security testing.
- Production identity/access, monitoring, cost, support, log and incident procedures.
- Registered patent-counsel and trademark-counsel review.

See `SCHOOL_PILOT_CHECKLIST.md`, `DATA_FLOW_AND_RETENTION.md`, `SECURITY.md`, `ACCESSIBILITY.md`, `OPENAI_ZDR_EVIDENCE_REQUEST.md` and the separate school/IP readiness packet.
