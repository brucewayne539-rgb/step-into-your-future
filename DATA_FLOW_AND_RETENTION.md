# Data Flow and Retention - BHS Review Release 23

Reviewed November 4, 2026. This file supersedes V20/V21 photo-enablement guidance.

## BHS no-photo roadmap

Browser POSTs only career, grade, path and priority to /api/bhs/roadmap (legacy /api/roadmap remains supported). Fixed allowlists reject extra keys and invalid values; non-JSON and uploads are rejected. Local catalog/career functions build the response. No external AI request, account, name, transcript, photo or student-history database is involved. These four selections still warrant a district privacy review when used for school purposes.

## Optional fictional preview

The restricted presenter selects a bundled fictional sample and fixed-menu values. The server, not the browser, loads the bundled image and calls OpenAI's image-edit endpoint with a constrained career/age prompt. No personal-image URL, upload or free-text prompt is accepted. Grade and priority are not included in the provider prompt. Results receive a permanent fictional/not-a-prediction watermark. Administrator Preview is optional and requires separate district/provider review. Set ADMIN_PREVIEW_ENABLED=0 to block image generation for a roadmap-only approval; a source-controlled real-photo ban remains in force regardless.

## Retired real-person route

/api/generate, /api/bhs/generate, /api/ghs/generate and /api/chs/generate reject before CSRF form parsing, image decoding or provider calls. The upload implementation is removed; old PORTRAITS_ENABLED/approval flags cannot restore it. The BHS UI has no file/camera input, including its legacy /pilot-demo link.

## Inventory and limits

| Location | Handling | Evidence still needed |
| --- | --- | --- |
| Browser | First-party signed session cookie for security/admin authorization/counts; no career selections/photos. In-page selections/results remain until navigation/refresh. Saved copies remain locally. | School browser/device controls and saved-record handling. |
| Flask memory | Requests/results only; no student/choice/photo/result database. IP-derived keyed hashes and timestamps support abuse limits. Idle counters cleared on the next limiter invocation after 15 minutes or on process restart. | Actual process/host controls; no forensic wipe guarantee. |
| Render | No intentional app logging of selections, content, photos, raw IPs or credentials. Host/network may process request/IP metadata. | Account/region/plan, DPA, security, subprocessors, all log categories/retention, deletion/closeout and incident terms. Dashboard availability does not describe all retention. |
| OpenAI | Fictional preview only; bundled synthetic image plus career/age scenario. No Zero Data Retention claim. API training excluded by default unless operator opts in. | Actual project settings (training/sharing off), accepted terms, retention/exceptions, subprocessors, incident and deletion channels. |
| District/device | Downloaded/printed/screenshot results and network records under district/device control. | Retention, access, correction, deletion and family notice. |

Google Analytics/Tag Manager are removed from shipped HTML and the CSP no longer permits their script/connect domains. Browser connections are same-origin; server-side fictional generation is still an external provider call. No advertising/commercial profiles or student-data training is authorized. See docs/BRANFORD_REVIEW_PACKET.md for proposed terms, not an executed agreement.

Free indefinite permission to Branford does not transfer Bruce Wayne Brailsford's original software/IP or create a promise of permanent hosting/maintenance. Annual BHS catalog review is coordinated with school staff; the 2026-27 label must not change until the new data is verified.
