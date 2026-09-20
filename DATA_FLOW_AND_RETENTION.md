## Cumberland catalog-backed roadmap — 20 September 2026

Cumberland uses explicit, grade-specific pathways and the local CHS catalog. The current runtime does not call the OpenAI text API for roadmaps. The historical chs_roadmap module is retained for shared definitions and regression records; its AI planning functions are not used by the current routes. Portrait behavior and privacy gates are unchanged.

## No-photo roadmap (default)

1. The browser sends four selected values: career, current grade, path, and priority.
2. The Flask app validates each against fixed allowlists.
3. Local BHS/GHS/CHS catalog data produces the roadmap.
4. No photo, future age, student name, OpenAI call, profile, or application database record is involved.

## Optional portrait (disabled by default on hosted deployments)

1. The browser previews a selected JPEG, PNG, or WebP locally.
2. The user must acknowledge age/authorization and the photo/provider notice.
3. The server validates file size, decoded dimensions, and actual image format.
4. The server rotates the image as required and re-encodes it as PNG, excluding EXIF metadata.
5. The cleaned image plus a constrained career prompt is sent to the OpenAI image-editing API.
6. The server burns an AI-generated/not-a-prediction notice into the returned PNG pixels.
7. The response is shown in the browser. The original file input and preview object URL are cleared after the request; the result is cleared when the page is left.

## Administrator Preview (fictional students only)

1. The signed-in administrator chooses one of two bundled, entirely fictional AI-generated sample students.
2. The browser sends only the approved sample identifier plus career, future age, path and priority selections. There is no photo-upload control.
3. The server resolves the identifier to the bundled synthetic image and validates every selection against fixed allowlists.
4. The bundled image and constrained demonstration prompt are sent to the image-editing API.
5. The server burns FICTIONAL AI DEMONSTRATION and NOT A REAL STUDENT | NOT A PREDICTION into the returned PNG pixels.
6. A separate per-session limit, defaulting to six generations, controls demonstration use and cost.

The Administrator Preview uses the provider's standard API data controls and is not represented as a Zero Data Retention workflow. It contains no real student image or student record.

## Retention truth table

| Location | Intentional app storage | What must still be verified |
|---|---|---|
| Browser/device | No account/profile. A selected photo and result can remain in memory during the page session. Downloads, prints, screenshots, browser/device backups remain until locally deleted. | District device/browser configuration and deletion procedure. |
| Flask process | In-memory request handling only; no application photo file/database write. References and buffers are released after the request. | No secure-wipe guarantee; independent test and host memory controls. |
| OpenAI | V21 blocks real-student hosted portraits until the operator records ZDR confirmation for the project. The fictional Administrator Preview uses standard API controls. | Written approval, effective project/org, supported endpoint/model, exceptions, DPA/security terms, deletion/incident contacts before real-student use. |
| Render | The app avoids logging student selections, prompts, photo bytes, and raw IPs. | Request/operational metadata, plan-specific 7/14/30-day dashboard log retention, contract/DPA, subprocessors and incident terms. |
| School | Not controlled by this app. | Paper/electronic authorization records, printed/downloaded results, retention schedule, access, correction, deletion, and records requests. |

Do not describe the system as “zero retention,” “certified compliant,” or “securely wiped.” The supportable statement is narrower: the application does not intentionally create a student/profile/photo database and its hosted portrait route is disabled until specified evidence flags are deliberately enabled.
