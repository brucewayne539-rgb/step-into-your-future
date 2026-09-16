# V22 Verification Report

## Purpose

Correct the entry routing so each school-specific no-photo explorer opens directly, while keeping the live fictional Administrator Preview protected by `DEMO_ACCESS_CODE`.

## Automated verification

Fifteen tests passed on September 16, 2026:

- 630 BHS grade, career and pathway combinations.
- 630 GHS grade, career and pathway combinations.
- Public BHS and GHS explorer routes with a configured access code.
- Public no-photo roadmap API with a configured access code.
- Protected Administrator Preview entry.
- Correct return to the selected school after successful access.
- Fictional source assets, absence of a photo-upload control, permanent watermark processing and complete school-specific preview results.
- CSRF protection, security headers and fail-closed real-student portrait controls.

## Expected post-deployment behavior

- `/` opens the BHS explorer directly.
- `/ghs` opens the GHS explorer directly.
- `/admin-preview?school=bhs` or `school=ghs` requests the private demo code when necessary.
- The existing Render settings and GoDaddy DNS record remain unchanged.
