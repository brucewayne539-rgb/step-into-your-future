# School-Pilot Experience Simulation

This update adds three protected presentation routes that follow the regular
student career-exploration flow while using only bundled fictional students:

- `/pilot-demo` — Branford High School
- `/ghs/pilot-demo` — Guilford High School
- `/chs/pilot-demo` — Cumberland High School
- `/armie/pilot-demo` — Armie Army-career exploration

The visitor selects a local photo file to simulate the approved student flow.
The browser does not open, preview, transmit, or store that selected file. The
application substitutes a bundled fictional student based on the selected grade
and sends only that fictional source image to the existing protected preview
endpoint. Every returned portrait retains the permanent fictional-demonstration
watermark.

The routes use the existing administrator access code, API key, generation
limit, course engines, school catalogs, CSRF protection, rate limiting and
privacy headers. Existing BHS, GHS, CHS and Armie routes are unchanged.

Verification completed:

- Full Python suite: 1,301 tests and 265 subtests passed.
- Pilot-page JavaScript parsed successfully after server-side rendering.
- Route protection, return-to-requested-school behavior, simulated upload
  labeling and all three school editions are covered by automated tests.
