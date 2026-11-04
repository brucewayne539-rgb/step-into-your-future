# Technology helpdesk submission draft

**Subject:** Request district review: Step Into Your Future - Today! (BHS career exploration)

**Request type:** Educational software / web application review. Please route for technical, student-data privacy, curriculum/counseling and accessibility review before school-directed student use.

**Submitted by:** Bruce Wayne Brailsford, BHS paraeducator and creator of this independently developed application. This request is for district consideration; no approval or district endorsement is claimed.

**Application:** Step Into Your Future - Today! | BHS edition, release 23-bhs-no-photo.

**Proposed URL:** https://app.palonious.com/bhs (verify release 23 before review). Privacy: /bhs/privacy. Review information: /bhs/school-review.

**Intended users/grades:** Students in grades 8-12 exploring BHS pathways, including grade 8 preparation for BHS; teachers/counselors supervising use. This edition uses the BHS catalog, not every Branford school's catalog.

**Educational justification:** Connect career interests with actual BHS courses, grade eligibility, stated prerequisites, school opportunities, practical experiences and further education/training. Students select a grade, career, path and priority, then discuss a school-specific roadmap with their counselor. The app does not inspect transcripts or verify completed prerequisites.

**Features and information:** Real-student photos/uploads are disabled in source. No student names, accounts, school logins, transcripts or sensitive records are requested. Roadmaps use local content and make no external AI request. Google Analytics/Tag Manager and advertising are removed. Optional restricted fictional previews use only built-in synthetic people and send a constrained fictional career/age scenario to OpenAI. The district may review/approve roadmaps and fictional previews separately.

**Technology:** Browser-based; no extension/app installation, Google Workspace API permissions or roster integration requested. HTTPS hosting through Render; first-party security cookie and temporary pseudonymous abuse counters. Host/network metadata and optional OpenAI retention/settings require review. Chromebook compatibility and accessibility should be confirmed by the district.

**Cost and ownership:** Branford Public Schools is offered indefinite educational use at no charge, with no subscription, annual fee, automatic billing or paid renewal. Bruce retains his original software, code, branding and intellectual property. Student-data rights remain separate. Hosting/support arrangements remain to be confirmed; no purchase is requested.

**Catalog maintenance:** Currently labeled BHS 2026-27. Coordinate annual review against the latest official Program of Studies with school staff, incorporate verified changes, then update the displayed catalog year. Students confirm current choices with a counselor.

**Privacy agreement:** Attached packet includes proposed written terms addressing CGS 10-234aa through 10-234dd and the state Model Terms of Service Addendum's required subjects. They are drafts for review/signature, not executed agreements. No Software Hub registration, signed pledge or compliance certification is claimed.

**Requested action:** Identify the district sponsor/reviewers, required district addendum or vendor form, provider/security evidence, privacy contacts and any conditions for roadmap-only and/or fictional-preview approval. Please provide a ticket/reference number and next preparation steps.

**Attachment:** Branford_Step_Review_Packet.pdf (includes this ticket draft, free-use/ownership statement, data flow, proposed privacy agreement, security/provider checklist, annual catalog process and approval record).

**Submission route:** District technology support system linked from https://branfordschools.org/technology. This is prepared text only; no ticket or message has been submitted.


<!-- pagebreak -->

# Step Into Your Future - Today!
## Branford Public Schools review packet

Prepared for district consideration | November 4, 2026 | Release 23-bhs-no-photo

**Requested decision:** Whether to approve school-supervised career exploration using the Branford High School course catalog. The district may approve the no-photo roadmap and optional fictional-student preview separately.

**Offered by:** Bruce Wayne Brailsford, creator and proposed permission grantor. The actual operator and authorized district contact must be confirmed before execution of privacy terms. No existing company or district endorsement is assumed.

### Permission and retained ownership

Bruce Wayne Brailsford offers Branford Public Schools nonexclusive permission to use this edition for district educational purposes indefinitely at no charge. There is no annual fee, subscription, automatic billing, paid renewal or scheduled expiration of permission. This offer is limited to Branford Public Schools; it does not give other districts permission on these terms.

Bruce retains ownership of his original application, code, branding and intellectual property. Use does not sell or assign those rights, give the district exclusivity, or authorize resale/sublicensing. Student information and third-party materials retain their respective rights. The district may use and print/save generated educational materials for its educational purposes. No exclusive copyright in AI-generated material is promised.

Indefinite permission to use does not guarantee perpetual third-party hosting, uninterrupted service, ongoing AI-processing capacity or indefinite maintenance. Hosting/support arrangements and any material changes should be confirmed with the district. No future charge is authorized by this permission statement.

### Scope and educational purpose

The app connects selected grades 8-12 and careers with BHS courses, prerequisites, school programs, practical experiences and further education/training. Grade 8 supports planning for BHS. District-wide permission does not mean other Branford schools' course catalogs have been integrated.

This is career discussion support. It does not read transcripts, verify completed prerequisites, measure ability, determine career suitability, or make placement, admission or employment decisions. Students should confirm course choices with their BHS counselor.

**Current catalog label: 2026-27 BHS Program of Studies.** School staff must validate the source, current accuracy and suitability before student use.

### Additional career pathways

The app initially includes 42 career pathways. Additional pathways may be added in response to student interests, teacher or counselor requests, and identified educational needs, subject to content verification and available development capacity.

This packet requests review. It is not a signed permission statement, executed privacy agreement, legal certification or district approval.

<!-- pagebreak -->

# Features, data and providers

### No-photo roadmap

The browser sends four fixed-menu values to the app server: grade to explore, career, path and priority. The server validates the values and constructs a response from local school-course and prepared career data. No OpenAI, Gemini or other external AI request occurs for this feature. No student name, school login, account, transcript, actual age or sensitive student record is requested.

### Optional fictional-student preview

A restricted presenter selects a bundled fictional person, career and future age. The server reads its own bundled synthetic image and sends it with a constrained prompt to the OpenAI image-editing API. No uploaded person/photo, arbitrary image URL or free-text prompt is accepted. Grade and priority support the local roadmap and are not included in the provider prompt. Career and future age in this feature describe a fictional scenario and should not be linked to a named student.

Returned images are permanently marked FICTIONAL AI DEMONSTRATION and NOT A REAL STUDENT / NOT A PREDICTION. Hosted previews require the configured administrator access code and session secret. If not approved, disable ADMIN_PREVIEW_ENABLED and verify the preview API is blocked.

### Real photos and analytics

Real-person uploads are retired in source. Legacy generation URLs reject requests before upload/image processing, even if old environment flags are enabled. BHS pages and the legacy BHS pilot route provide no personal-photo picker or camera controls. Google Analytics/Tag Manager tags are removed from shipped pages; browser connection policy permits only the app's host. No advertising, commercial student profiles, session replay or cross-site analytics are included.

### Storage inventory

- **Browser:** first-party signed session cookie for request security, restricted-preview authorization and usage counts; no menu selections or photos in the cookie. Results remain in the page until navigation/refresh; saved copies remain under device/district control.
- **App memory:** request handling and temporary security counters. No student, selection-history, photo or result database. Rate limits use a keyed hash of connection IP plus timestamps. Idle entries are removed on the next limiter check after 15 minutes or at process restart.
- **Render:** application hosting and delivery. IP/request paths, timestamps and operational/security metadata may be processed. Actual account, region, subprocessors, logs, retention and deletion terms remain to be verified.
- **OpenAI:** only the optional fictional preview. Standard API policy excludes training unless the customer opts in; normal abuse-monitoring retention may be up to 30 days with endpoint/safety exceptions. No Zero Data Retention promise is made. Exact account settings, terms and provider protections require review.
- **School/network:** district filtering, proxy logs, device histories, printouts and exports remain subject to district controls. They are not deleted by the app.

**No zero-retention or anonymous-data guarantee is made.** The absence of an app database does not eliminate the need to review infrastructure and school-held records.

<!-- pagebreak -->

# Proposed Student Data Privacy Agreement

**DRAFT FOR DISTRICT REVIEW - NOT EXECUTED.** These proposed procedures supplement the district's chosen agreement; the district may use its own approved Connecticut addendum. The identified operator must accept and be able to perform every agreed obligation. Provider terms must be checked before acceptance. Publishing this packet does not bind the district or a provider.

Board: Branford Board of Education / Branford Public Schools.

Operator legal name: ____________________. Operator privacy/security contact: ____________________.

District privacy/security contact: ____________________. Approved service URLs: ____________________.

### 1. Ownership, control and authorized purpose

Student information, student records and student-generated content are not the property of or under the control of the operator. Student-generated content belongs to the student or parent/guardian. The operator will process student data only under district direction for the agreed educational service and its necessary security. Rights in the software do not grant rights in student data.

### 2. No training, advertising or commercial profiles

The operator will not sell, rent or trade student data, use it for targeted advertising or commercial profiling, or use/disclose it for model training, fine-tuning or shared AI-training datasets. The operator will keep voluntary provider training/data-sharing programs off and document that setting. Provider contracts must restrict use and disclosure to authorized services and applicable lawful exceptions. Generic provider terms are not assumed sufficient.

### 3. Access and correction

Students/parents/guardians may submit access or correction requests through the district. The district verifies authority and forwards only necessary information to the operator's designated contact. Proposed response: acknowledge within two business days and respond/complete within ten business days, or agree a documented extension with the district. The response identifies actual records held, provider involvement and any limits. If no record exists, say so; do not request new student identifiers merely to create a record for a request.

### 4. Deletion and return

The district may request deletion/return through the same designated contact. Proposed procedure: acknowledge within two business days; act within ten business days, subject to a district-approved extension. Coordinate deletion with providers; confirm what was removed, when, any provider ticket and any lawful retention limit. Do not promise deletion from infrastructure that has not been verified. Any retention exception must be legally permitted and documented, including qualifying inaccessible disaster-recovery copies; if restored, covered data again becomes subject to deletion requests.

### 5. End of use

On district discontinuation, return/delete covered operator-held student data by the agreed closeout date so it is not retained or available after the agreement ends, subject only to applicable lawful exceptions. Resolve provider log/backup handling before execution. No separate student accounts or post-contract retention accounts are offered in this edition.

<!-- pagebreak -->

# Proposed privacy terms, continued

### 6. Security and confidentiality

The operator will maintain risk-appropriate technical and organizational safeguards consistent with applicable Connecticut requirements and industry standards, restrict administrative access and require confidentiality. The district must verify actual hosting, access, patching and incident practices. Current source controls do not constitute an independent security audit or a warranty that every provider meets a particular standard.

### 7. Incident response and notices

Proposed commitment: notify the designated district incident contact without unreasonable delay and within 24 hours after discovery of suspected unauthorized access, release, disclosure or acquisition involving covered student data. Initial notice may be preliminary; do not wait for a complete investigation. It should state discovery time, affected service/data, known exposure, containment, contact and next update. Preserve minimal evidence, contact providers, and provide continuing updates and cooperation.

The contract must satisfy CGS 10-234dd and any other applicable notification law; stricter applicable requirements control. The district retains responsibility for its student/family and website notices. Final communication channels and responsible people must be completed before use. Do not represent these proposed deadlines as existing provider commitments.

### 8. FERPA and other applicable law

The operator and district will each ensure their compliance with FERPA as applicable. Where the district relies on a school-official exception, the agreement must establish required district control and use/redisclosure limits. The district determines the proper authorization and notices, including applicable COPPA requirements. No parent checkbox or free-use offer replaces that determination.

### 9. Providers and changes

Before receiving covered data, each relevant provider must have terms supporting the agreed purpose, security, confidentiality, deletion, restricted disclosure and incident obligations. List Render and, only if fictional previews are approved, OpenAI; review their subprocessors. Give the district advance notice of material changes to providers, data collection, retention, AI use or school features and obtain any required approval. Do not enable real photos, tracking, personal accounts or free-text prompts through a routine configuration change.

### 10. Governing law, severability and precedence

Connecticut law governs operator/district rights and duties. If a provision/application is invalid, the remainder remains effective where it can operate independently. The executed student privacy addendum controls over inconsistent website terms or other service terms. The operator acknowledges applicable duties under CGS 10-234aa through 10-234dd. The agreement should include any other mandatory provisions selected by district counsel.

### Separate approvals

No-photo roadmap approved: Yes / No / Conditions: ____________________.

Fictional preview approved: Yes / No / Conditions: ____________________.

District authorized signature/title/date: ____________________.

Operator authorized signature/date: ____________________.

**All signature lines are blank. No execution or approval is represented.**

<!-- pagebreak -->

# Security, hosting and readiness record

### Implemented in this release

- BHS no-photo controls; local catalog roadmaps; no third-party AI calls for roadmaps.
- Server rejection of retired real-photo endpoints; four-field roadmap allowlist and menu-value validation; 16 KiB request limit.
- Built-in fictional sample identifiers only; no arbitrary photo URL/prompt accepted by preview API; marked fictional outputs.
- Same-session anti-forgery tokens; hosted secure/HttpOnly/SameSite cookies; preview access code and session controls.
- First-party browser connection policy; no-store HTML/API responses; no referrers; framing and camera/microphone/geolocation restrictions.
- Minimal diagnostic content; no intentional logging of student choices/photos; temporary pseudonymous abuse counters.
- Google Analytics/Tag Manager removed from shipped HTML.

### Complete before school-directed use

1. **People:** confirm operator legal identity, active privacy/security contact, district sponsor, authorized signers and backup contacts. Do not assume a previously used company remains the operator.
2. **Host:** record Render service/account, region, plan, subprocessors, DPA, security evidence, log categories/retention, incident channels and deletion/closeout process. Dashboard log availability is not proof of every provider retention period.
3. **Optional AI:** if approved, record OpenAI organization/project identifiers (never API keys), covered image endpoint/model, accepted terms, data-sharing settings, standard retention/exceptions and incident/deletion channels. No real student images or records may be introduced.
4. **Configuration:** verify deployed source version, HTTPS/cookie behavior, access restrictions, minimal logs, no analytics, no upload processing and whether fictional previews are enabled. Disable the preview if only roadmaps are approved.
5. **Security:** review dependencies, account access/MFA, secret storage, patch owner, vulnerability handling and testing appropriate to the district's risk review. Per-process rate limits are supplemental, not a distributed firewall. Inline scripts/styles remain a known CSP limitation.
6. **Access:** agree approved URLs, school filtering and supervision. The current public roadmap is not district SSO. A district may require a gateway, restriction or other change before approval.
7. **Continuity:** confirm hosting availability/support contacts and what happens if hosting or AI generation stops. The local roadmap does not depend on OpenAI; a fictional preview outage should not prevent roadmap use.

### Incident procedure

Contain exposure; suspend the affected feature/service; preserve minimal timestamps, version and provider references; rotate exposed credentials; notify the district through agreed channels; investigate with providers; coordinate lawful notices/remediation. Do not copy student content into public GitHub issues or ordinary diagnostic logs. Resume only after a documented review. No automatic student/family messages are sent by this work.

### Remaining evidence

Provider settings/agreements, active contact details, independent security/accessibility findings, counselor validation and actual district approval are not supplied merely by this code update. The district should record unresolved conditions and approve only the scope supported by evidence.

<!-- pagebreak -->

# Annual curriculum review and family notice

### Annual BHS catalog process

The app currently labels its source as the BHS 2026-27 Program of Studies. Before each new school year's scheduling cycle, the district's designated curriculum/counseling contact should provide or identify the latest official catalog and changes. The creator and school staff can coordinate a review of course names, availability, grade eligibility, prerequisite language, pathways, school programs and real-world opportunities.

After verified changes are incorporated, run all-career/all-grade checks, have the school contact review examples, then update the visible catalog-year label and record the source/version, review date, change summary and reviewer. Until verification, keep the older year clearly displayed; do not relabel an unreviewed catalog as current. Pause or qualify affected recommendations when a material discrepancy is reported.

This establishes a review process, not automatic ingestion, guaranteed yearly delivery or an indefinite unpaid maintenance obligation. Any requested work and timing should be coordinated. Students should always confirm prerequisites, eligibility, availability and scheduling with their counselor.

Catalog year/source URL: ____________________. School reviewer/date: ____________________.

Updates verified/release reference: ____________________. Next review: ____________________.

### Accessibility review

Test keyboard navigation/focus, labels and errors, screen-reader use, contrast, mobile layout and 200-400% zoom/reflow. Check print/saved-roadmap usability and the equivalent roadmap without image generation. Record browser/assistive technology, findings, fixes and retest. Arrange an accessible alternative where needed. Source-level controls do not establish WCAG conformance.

### Proposed family/student notice - district to approve

"Step Into Your Future - Today! helps students explore careers and connect them with courses and opportunities in the Branford High School catalog. It uses a selected grade, career, path and priority; no student account, name, transcript or personal photograph is required. Roadmaps use local content, and Google Analytics and advertising are disabled.

If separately approved by the district, an optional supervised preview uses fictional people supplied by the app. It sends a synthetic image and a career/age scenario to OpenAI; it does not accept a real student photo. Fictional results are illustrations, not predictions. Students can use the complete roadmap without this preview.

The app does not confirm completed prerequisites or guarantee eligibility. Discuss choices with your BHS counselor. For privacy, correction, deletion or accessibility questions, contact the district representative named in the district's notice. Host and provider metadata/retention are described in the approved privacy information."

<!-- pagebreak -->

# District decision and reference record

### Approval record - to be completed by the district

Educational sponsor/role: ____________________. Technical/privacy reviewer: ____________________.

Operator identity/contact verified: Yes / No. Privacy agreement executed: Yes / No.

Render provider review complete: Yes / No. Optional OpenAI review complete: Yes / No / Not applicable.

Curriculum/counselor review complete: Yes / No. Accessibility/security conditions resolved: Yes / No.

Approved URLs: ____________________. Approved users/supervision: ____________________.

No-photo roadmap decision: Approve / Decline / Conditional. Conditions: ____________________.

Fictional preview decision: Approve / Decline / Conditional. Conditions: ____________________.

Decision date/signatory: ____________________. Review date: ____________________.

Free indefinite permission accepted: Yes / No. Software ownership remains with the creator; student-data ownership/control remains separate. No annual fee or paid renewal is proposed for Branford.

### Official reference links reviewed

- Connecticut statute: https://www.cga.ct.gov/current/PUB/chap_170.htm#sec_10-234aa
- Connecticut student privacy guidance and model addendum: https://portal.ct.gov/DAS/CTEdTech/Commission-for-Educational-Technology/Initiatives/Student-Data-Privacy
- Model addendum: https://portal.ct.gov/-/media/das/ctedtech/documents/ct_model_tos_addendum.pdf
- OpenAI API data controls: https://developers.openai.com/api/docs/guides/your-data
- Render logs: https://render.com/docs/logging
- Render DPA: https://render.com/dpa
- Branford technology review route: https://branfordschools.org/technology

The packet is an independently drafted review aid, not the official state addendum and not a substitute for the district's legal/privacy decision. Proposed duties must be finalized and accepted by the actual operator and authorized district representative. No submission, signature, email or approval has been made on anyone's behalf.

### Application locations

BHS explorer: https://app.palonious.com/bhs

Privacy notice: https://app.palonious.com/bhs/privacy

District review page: https://app.palonious.com/bhs/school-review

Fictional-only preview: https://app.palonious.com/admin-preview?school=bhs

The source repository contains editable technical documents and the packet source. Verify that the live service shows release 23-bhs-no-photo before relying on these addresses for district review.
