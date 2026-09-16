# Data Flow and Retention — V20

## No-photo roadmap (default)

1. The browser sends four selected values: career, current grade, path, and priority.
2. The Flask app validates each against fixed allowlists.
3. Local BHS/GHS catalog data produces the roadmap.
4. No photo, future age, student name, OpenAI call, profile, or application database record is involved.

## Optional portrait (disabled by default on hosted deployments)

1. The browser previews a selected JPEG, PNG, or WebP locally.
2. The user must acknowledge age/authorization and the photo/provider notice.
3. The server validates file size, decoded dimensions, and actual image format.
4. The server rotates the image as required and re-encodes it as PNG, excluding EXIF metadata.
5. The cleaned image plus a constrained career prompt is sent to the OpenAI image-editing API.
6. The server burns an AI-generated/not-a-prediction notice into the returned PNG pixels.
7. The response is shown in the browser. The original file input and preview object URL are cleared after the request; the result is cleared when the page is left.

## Retention truth table

| Location | Intentional app storage | What must still be verified |
|---|---|---|
| Browser/device | No account/profile. A selected photo and result can remain in memory during the page session. Downloads, prints, screenshots, browser/device backups remain until locally deleted. | District device/browser configuration and deletion procedure. |
| Flask process | In-memory request handling only; no application photo file/database write. References and buffers are released after the request. | No secure-wipe guarantee; independent test and host memory controls. |
| OpenAI | V20 blocks hosted portraits until the operator records ZDR confirmation for the project. | Written approval, effective project/org, supported endpoint/model, exceptions, DPA/security terms, deletion/incident contacts. |
| Render | The app avoids logging student selections, prompts, photo bytes, and raw IPs. | Request/operational metadata, plan-specific 7/14/30-day dashboard log retention, contract/DPA, subprocessors and incident terms. |
| School | Not controlled by this app. | Paper/electronic authorization records, printed/downloaded results, retention schedule, access, correction, deletion, and records requests. |

Do not describe the system as “zero retention,” “certified compliant,” or “securely wiped.” The supportable statement is narrower: the application does not intentionally create a student/profile/photo database and its hosted portrait route is disabled until specified evidence flags are deliberately enabled.

