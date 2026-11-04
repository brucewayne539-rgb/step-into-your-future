# Security Notes - BHS Review Release 23

November 4, 2026. Implemented safeguards are not a security/legal certification.

## Implemented

- Real-person image routes are retired in source and rejected before upload parsing/decoding. Old environment flags cannot enable them.
- Roadmap endpoints accept only JSON fixed-menu career/grade/path/priority values; no external AI call for roadmaps. Global request limit is 16 KiB.
- Optional preview reads only a bundled fictional image, applies constrained choices, and watermarks the result. Hosted access requires configured teacher/admin code and stable session secret; generation limits apply.
- Google Analytics/Tag Manager removed. Browser CSP connections/scripts/fonts stay first-party; framing, object embedding, referrers, camera/microphone/geolocation are restricted.
- Same-session anti-forgery protection; Secure hosted cookies, HttpOnly, SameSite=Lax; 60-minute persistent admin sessions. Session contains no career choices/photos.
- HTML/API use no-store. Output text is escaped in BHS rendering. No student/selection/photo/result database.
- In-memory rate limits retain IP-derived keyed hashes/timestamps without selections; idle entries are cleared on the next limiter check after 15 minutes or process restart.
- Minimal content-free diagnostic categories; no intentional logging of student choices, images, raw IPs or credentials. No automatic AI retry.

## District verification and remaining limitations

Confirm deployed release, HTTPS/proxy settings, administrative access/MFA, provider DPAs/security/subprocessors, retention/deletion/closeout, privacy contact and incident channels. For approved fictional previews, confirm OpenAI data-sharing/training opts remain off. No ZDR claim is made. Actual provider terms may require additional work before acceptance.

Use security/dependency/accessibility review appropriate to district risk. Inline script/style CSP remains; per-process rate limits are supplemental, not a distributed firewall. Current roadmap pages are public, not district SSO; the district may require an access gateway. Review host metadata even without an app database. Do not promise zero retention or forensic memory wiping.

Never commit API keys, access codes, session secrets or student records. Rotate exposed secrets. Do not use public GitHub issues for personal information. Record patch/monitoring/support owners before student use. See INCIDENT_RESPONSE.md and docs/BRANFORD_REVIEW_PACKET.md.
