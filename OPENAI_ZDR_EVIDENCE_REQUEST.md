# OpenAI Zero Data Retention Evidence Request

Use this as a request template. It is not a waiver and does not itself change OpenAI settings or contractual obligations.

## Draft request

Subject: Request for project-specific Zero Data Retention confirmation — K–12 image editing

We are evaluating a supervised K–12 career-exploration application, “Step Into Your Future,” for possible school use. The optional portrait feature may process an authorized photograph of a person age 13 or older using the OpenAI image-editing API and `gpt-image-2`. The no-photo roadmap is the default and does not call OpenAI.

Please evaluate our organization/project for Zero Data Retention and provide written confirmation addressing:

1. the exact organization and project to which ZDR applies (IDs only; never send an API key);
2. the effective date and whether image-edit requests using `gpt-image-2` are covered;
3. whether submitted image bytes, prompts, generated images, safety classifications, request metadata, or support records are retained, and for how long;
4. any abuse-monitoring, CSAM, legal, security, backup, support, or other exceptions;
5. whether API data is used for training or human review under this configuration;
6. applicable DPA, security reports, subprocessors, breach-notification terms, deletion/return terms, data location and audit materials;
7. the process/contact for a school or operator to request access, correction, preservation, deletion, or incident support; and
8. whether any console setting, endpoint parameter, account tier, or technical control is also required after approval.

Context: users are students/teachers; portrait users are restricted to age 13+; photos are not intentionally stored by our application; EXIF is removed before submission; no student name, email, ID, grades, disability information, or school login is sent in the image request.

## Evidence record

- OpenAI organization ID: ______________________________
- OpenAI project ID: ___________________________________
- Request/ticket number: _______________________________
- Request date: ________________________________________
- Approval/response date: ______________________________
- Covered model/endpoint: ______________________________
- Effective configuration date: ________________________
- Exceptions summarized: _______________________________
- DPA/security/subprocessor documents saved at: _________
- Screenshot/export of project control saved at: ________
- Verified by (name/title): _____________________________
- Reverification date: _________________________________

Only after this evidence is complete should an authorized operator set `OPENAI_ZDR_CONFIRMED=1`; school approval and the other V20 portrait gates remain separately required.

