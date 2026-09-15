STEP INTO YOUR FUTURE — TODAY!
SCHOOL-READINESS BUILD V15 — BHS AND GHS

START HERE
1. Keep your present live site unchanged until this build has been uploaded and Render reports a successful deployment.
2. Upload the CONTENTS of this folder to the root of the existing GitHub repository. Preserve the templates folder.
3. GitHub should replace matching files and add the new privacy and GHS icon/manifest files.
4. Wait for Render to complete its automatic deployment.
5. Test the roadmap-only path first at both addresses:
   BHS: https://step-into-your-future.onrender.com/
   GHS: https://step-into-your-future.onrender.com/ghs
6. Then make one optional portrait test. Confirm the disclaimer is visibly burned into the downloaded PNG.

WHAT CHANGED
• The default experience is a career-and-course roadmap that requires no photo and makes no AI image call.
• A future portrait remains optional.
• Portrait mode requires confirmation that the person is at least 13 and that the user has permission to submit the photo.
• Grade 8 is now a planning year; Grades 9–12 retain their school-specific course logic.
• The approved universal blue stairs-and-arrow icon is used by both school editions.
• A Privacy & School Use page accurately describes current processing and the work still required before formal district adoption.
• Browser responses include stronger no-cache, framing, referrer, permissions and content-security protections.
• The returned portrait still has the AI disclaimer permanently burned into its PNG pixels before download.

IMPORTANT LIMITS
• This is a teacher-review prototype, not a legal certification or district approval.
• The application itself does not create a student profile or photo database, but that alone is not the same as verified zero retention across OpenAI, Render and network providers.
• Before formal student use, the operator should obtain written provider-retention commitments where required, complete district legal/security/accessibility review, execute required contracts or DPAs, publish operator contact and incident procedures, and implement production monitoring and spending/rate controls.
• Career and course guidance must be confirmed with a school counselor and the current official course catalog.

SERVER SETTINGS
OPENAI_API_KEY — private server-side API key; never place it in GitHub.
DEMO_ACCESS_CODE — optional teacher-preview access code.
SECRET_KEY — long random server secret used to protect sessions.
MAX_GENERATIONS_PER_SESSION — portrait limit per browser session.

ROLLBACK
The uploaded file named "step-into-your-future-main (1).zip" is the pre-update backup. If necessary, its contents can restore the earlier build.
