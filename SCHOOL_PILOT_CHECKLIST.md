# School Pilot Approval Checklist — V20

## Phase 1 — no-photo teacher review

- [ ] Confirm the app is a teacher-review prototype, not an approved student system.
- [ ] Test BHS and GHS no-photo roadmaps across grades 8–12.
- [ ] Counselor validates course names, grades, prerequisites, and disclaimers against the current official catalog.
- [ ] Curriculum lead approves educational purpose and lesson plan.
- [ ] Accessibility reviewer tests keyboard-only use, screen reader use, zoom/reflow, contrast, errors, print/PDF alternative, and the no-photo equivalent.
- [ ] Privacy/security reviewers complete vendor/provider assessment.

## Phase 2 — controlled no-photo student pilot

- [ ] Written district approval and named owner.
- [ ] Approved acceptable-use, family/student notice, support and incident contacts.
- [ ] District-managed access and device configuration.
- [ ] No portrait environment flags enabled.
- [ ] Evaluation measures exclude sensitive profiling and do not become education records unless approved.
- [ ] Pilot end date, feedback method, deletion/closeout and decision meeting scheduled.

## Phase 3 — optional portrait consideration

- [ ] District counsel/privacy officer confirms the lawful authorization process and Connecticut/Federal contract requirements.
- [ ] OpenAI ZDR evidence record is complete for the exact project/model/endpoint.
- [ ] OpenAI and Render DPAs, security documents, subprocessors, retention/deletion, breach terms and contacts are approved.
- [ ] Operator privacy/security contacts are published.
- [ ] Photo authorization form is approved; no-photo choice is equally available.
- [ ] Under-13 portrait use is prohibited in this build.
- [ ] Independent security and WCAG 2.1 AA testing is complete; critical/high issues are resolved.
- [ ] Spending alerts, shared rate limiting, monitoring and incident drill are in place.
- [ ] Only then set `OPENAI_ZDR_CONFIRMED=1`, `SCHOOL_PORTRAIT_APPROVED=1`, and `PORTRAITS_ENABLED=1`.

## Annual/term review

- [ ] Revalidate school catalog content and career/licensing guidance.
- [ ] Recheck provider policies, contracts, models, endpoints and subprocessors.
- [ ] Recheck accessibility after material UI/content changes.
- [ ] Rotate secrets and review access.
- [ ] Review incidents, requests, costs, feedback and whether the portrait remains educationally necessary.

