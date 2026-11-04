# BHS privacy review - release 23

Prepared November 4, 2026. District approval has not been granted by this report.

## Changes verified

- Real-photo handling removed and legacy endpoints reject before image decoding/provider calls, regardless of retired flags.
- BHS UI and legacy pilot links have no real-photo inputs; fixed fictional samples remain available in the restricted preview.
- Roadmap calls use local data; extra student-information fields and file requests are rejected.
- Analytics tags removed; browser script/connect domains restricted to first-party; no selections added to session.
- Privacy, data flow, incident/security, school checklist and annual-catalog wording revised.
- Branford offer: indefinite use at no charge, creator retains original software/IP; no paid renewal.
- Proposed privacy agreement and district decision checklist prepared in docs/BRANFORD_REVIEW_PACKET.md.

## Validation

- Full pytest suite: 5,319 passed; 4,530 subtests passed.
- Rendered BHS, fictional preview, privacy and school-review routes return HTTP 200 locally; BHS pages expose no file inputs.
- Rendered inline JavaScript passes Node syntax checks.
- Eight-page PDF including helpdesk submission draft rendered and visually inspected for layout.
- Automated browser-screen checks could not run because this environment did not provide a working Chromium binary. Manual browser/accessibility review remains outstanding.

Provider accounts/settings, infrastructure retention/deletion, active contacts, actual operator identity, applicable contracts, independent security/accessibility findings and district signatures remain external approval items. No ZDR or certification claim is made. Confirm live deployment/version separately.
