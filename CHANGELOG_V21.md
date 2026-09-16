# Step Into Your Future V21

## Administrator Preview

### School-specific portrait results

- The fictional-photo result displays the complete grade-aware school-course pathway directly beside the portrait in both BHS and GHS.
- GHS includes strongest matches, supporting courses, future options, catalog prerequisites/pages, programs, experience guidance and a counselor next step.
- BHS presents its detailed prerequisites and grade-aware programs in the same expanded preview format.
- The earlier GHS message directing administrators back to the main explorer has been removed.

- Added a protected **Administrator Preview** button to both BHS and GHS.
- Bundled two entirely fictional, AI-generated sample students: Grade 9 and Grade 11.
- Administrators can choose a fictional student, career, future age, path and priority and watch the portrait transformation occur live.
- Administrator Preview contains no photo-upload control and never accepts a real student photograph.
- Fictional preview results receive a server-burned `FICTIONAL AI DEMONSTRATION / NOT A REAL STUDENT / NOT A PREDICTION` watermark.
- Preview generation has a separate six-portrait allowance per signed-in browser session, so administrators can compare several careers while real-photo limits remain tighter.
- Real-person/student photo mode remains separately blocked by the V20 provider-retention, school-approval and privacy-contact gates.
- `ADMIN_PREVIEW_ENABLED=0` hides the feature after a pilot or contract without deleting the code needed for later presentations.

## Documentation

- Updated the privacy page to distinguish no-photo roadmaps, fictional Administrator Preview and formally approved real-photo portrait use.
- Updated visible version labels and the health-check version to V21.

## Deployment requirement

Administrator Preview must remain behind `DEMO_ACCESS_CODE`. Never place the access code in GitHub or any public document. Set it only in Render's Environment settings.
