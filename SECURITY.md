# Security Notes — V21

This is a teacher-review build, not a security certification.

## Implemented controls

- The no-photo roadmap is the default and makes no OpenAI image request.
- Hosted portraits fail closed unless `PORTRAITS_ENABLED`, `OPENAI_ZDR_CONFIRMED`, and `SCHOOL_PORTRAIT_APPROVED` are explicitly enabled, a privacy contact is published, an access code exists, and a stable session secret is configured.
- API/form writes require a same-session anti-forgery token.
- Hosted cookies use `Secure`, `HttpOnly`, and `SameSite=Lax`; sessions expire after 60 minutes.
- Login, roadmap, portrait, and per-session generation limits reduce casual abuse and cost exposure. In-memory limits are supplemental and are not a distributed production rate limiter.
- Uploads are limited to JPEG, PNG, or WebP; 12 MB request size and 24-megapixel decoded size; images are re-encoded as PNG to remove EXIF metadata.
- Uploaded and generated photos are not intentionally written to an application file or database.
- OpenAI requests use no automatic retry, reducing duplicate submissions after timeouts.
- Logs contain an exception category only; code does not log prompts, selections, photo bytes, access codes, API keys, or raw IP addresses.
- HTML/API responses use no-store caching and headers that restrict framing, referrers, browser capabilities, object embedding, and cross-origin access.
- AI/illustrative language is burned into returned portrait pixels before release.
- Administrator Preview accepts only two bundled fictional sample identifiers, has no upload control, applies a separate generation limit, and burns a fictional-person notice into every returned preview image.

## Known limits requiring external work

- Obtain an independent penetration test and code/dependency review before production.
- Use a district-managed identity system or authenticated reverse proxy for student production access; the demo access code is not SSO or role-based access control.
- Replace the per-process in-memory limiter with a district-approved gateway or shared limiter for multi-instance production.
- The current CSP permits inline scripts/styles because the prototype UI is self-contained. Refactor and test nonce/hash-based CSP before high-assurance production.
- Confirm Render and OpenAI contracts, subprocessors, retention, breach terms, deletion, audit rights, data location, and support contacts in writing.
- Establish vulnerability intake, patch cadence, dependency scanning, backup/restore, incident exercises, and a named security owner.
- Python/browser memory cannot be promised to undergo forensic secure wiping.

## Secret handling

Never commit these values to GitHub:

- `OPENAI_API_KEY`
- `DEMO_ACCESS_CODE`
- `SECRET_KEY`

Rotate a secret immediately if it appears in source, screenshots, logs, email, or chat. Keep teacher and production environments separate.
