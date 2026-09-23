# Career-fair readiness review — September 23, 2026

Status: PARTIAL — not a full live-demo sign-off.

Reviewed production source at e32abaf60488d9a13d3ac573255831c98f014ae4.
Scope: BHS, Armie, Jet Force.

## Checks completed in this review
- Jet Force JavaScript literal element references all have matching template IDs.
- All 10 Jet Force roles have required display, route, training, project, question, civilian and source fields; IDs are unique.
- Shared ATC profile exists and has explanations for each connected course.
- All 262 Army role mappings reference an existing school profile.
- Reviewed sign-in redirects, session settings, portrait quota checks, prompt integration, error handling, roadmap rendering and print handlers in source.
- These are source/data consistency checks, not verification of every catalog claim.
- Added beforeprint/afterprint handlers to the shared BHS/Army fictional-demo template: expand course details for printing and restore their original state afterward. Executed the handlers with plain-object fixtures; open/restore behavior passed. Actual browser PDF output remains unverified.

## Observed presentation dependencies
- BHS fictional preview and Armie obtain portrait and roadmap in the same provider-dependent request. A failed or delayed image prevents a new result appearing.
- Jet Force renders its roadmap before requesting the fictional portrait.
- Shared demo login expires after 60 minutes without session refresh on each request. Sign in shortly before presenting.
- Per-session image allowance and short-window rate limits apply across the fictional demo API. Heavy pre-presentation generation can consume the same session's allowance.
- Image provider output may still require visual review for identity, age progression, attire, grooming and equipment.

## Still required before declaring ready
1. Live desktop and mobile click-through: login, both students, grades 8–12, career/category changes, ages 22–35, back/edit/retry, no-photo paths.
2. Re-run repository Python tests (school/Army catalog combinations, auth, watermarking, portrait prompts and API responses).
3. Confirm representative live image generations and review the resulting images.
4. Inspect actual print-to-PDF and downloaded PNG output, including all collapsed course sections.
5. Confirm deployed revision and inspect browser console/network errors.
6. Rehearse on the presentation laptop and school network; retain previously generated portraits and PDFs as an offline backup.

## Why incomplete
The local execution environment and browser runtime both returned environment_offline / Environment is not connected. Reconnection attempts failed. The public web reader also could not open the app URLs. GitHub source access worked, so source review continued, but no claim of a fresh live browser rehearsal or fresh Python-suite pass is made.

Earlier successful portrait tests and deployment checks are useful history but are not substitutes for this pending full rehearsal.
