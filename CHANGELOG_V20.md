# V20 Change Log

- Preserves V19 as a separate rollback package.
- Keeps the complete no-photo roadmap as the default for both BHS and GHS.
- Makes hosted portraits fail closed pending documented OpenAI ZDR, school approval, privacy contact, restricted access and stable session configuration.
- Adds CSRF protection to all write requests.
- Adds login, roadmap, portrait and per-session throttles.
- Adds 60-minute hosted sessions and stronger browser policy headers.
- Adds a second explicit provider/retention acknowledgment; blocks portraits for under-13 users.
- Clears the original photo input/preview after a request and clears result/source references on page exit.
- Continues EXIF stripping, image re-encoding, fixed field allowlists, server-side validation, no automatic provider retry and permanent portrait watermarking.
- Expands the privacy page with a stage-by-stage data-flow/retention explanation and authoritative references.
- Adds ZDR evidence request, optional photo authorization draft, school pilot checklist, incident plan, security notes and accessibility review notes.
- Expands automated tests from 3 to 7, including all 630 BHS career/grade/path combinations, CSRF failure, security headers, fail-closed portrait configuration and credential non-disclosure.

