# V21 Verification Report

## Scope

This report covers the BHS/GHS V21 school-readiness build and its protected Administrator Preview.

## Verified behavior

- The no-photo roadmap remains available for Grades 8–12.
- The Administrator Preview offers only two bundled, entirely fictional AI-generated sample students.
- The preview page contains no photograph upload control.
- The server accepts only the two known fictional sample identifiers.
- Career, future age, pathway and priority are validated server-side.
- Each preview output receives a pixel-level fictional-demonstration watermark before it is returned.
- Preview generations use a separate per-session limit, defaulting to six.
- Real-student portrait mode remains disabled by the three fail-closed approval flags.
- BHS school-course data continues to use the official catalog-derived index and grade-aware matching logic.
- GHS retains its complete course, prerequisite and program explorer in the main Guilford edition.

## Automated checks

- Python syntax compilation for `app.py` and `bhs_catalog.py`.
- Existing BHS catalog and route test suite.
- Administrator Preview fictional-source asset checks.
- Administrator Preview page check confirming that no file input exists.
- Mocked live image-generation response, fictional watermark processing, session counter and BHS course-result checks.

## Required human deployment checks

1. Confirm a private `DEMO_ACCESS_CODE` and strong `SECRET_KEY` are configured in Render.
2. Confirm `ADMIN_PREVIEW_ENABLED=1` and `MAX_ADMIN_PREVIEW_GENERATIONS=6`.
3. Confirm all three real-student portrait flags remain `0`.
4. Test one fictional preview in BHS and one in GHS.
5. Confirm the visible fictional watermark in both the web result and downloaded PNG.
6. Confirm the no-photo roadmap remains available in both editions.
7. Confirm `/privacy` and `/healthz` load successfully.

## Limitations

Passing these checks is not a legal compliance certification, district approval, penetration test, accessibility conformance report or guarantee of provider-side retention behavior. Formal school adoption still requires the reviews and agreements described in the accompanying checklist and technical documentation.
