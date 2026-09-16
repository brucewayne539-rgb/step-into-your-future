# Incident Response Quick Plan — V20

This is an operational starting point; the district/operator must assign named people and align it with contractual and legal deadlines.

## Events covered

Suspected exposure of a photo, API key, access code, session secret, student information, provider account, unauthorized portrait use, public posting, malicious upload, unexpected provider retention, service compromise, or material accessibility failure.

## Immediate actions

1. Stop portrait processing by setting `PORTRAITS_ENABLED=0` and redeploying. Keep the no-photo roadmap available if safe.
2. Preserve relevant timestamps, Render request IDs, deployment/version, provider ticket IDs, and configuration evidence without copying student photo content into the incident log.
3. Rotate any exposed `OPENAI_API_KEY`, `DEMO_ACCESS_CODE`, and `SECRET_KEY`.
4. Restrict access or take the service offline if the no-photo route is also affected.
5. Notify the designated district privacy/security lead and operator incident lead.
6. Contact OpenAI/Render through the approved contractual channel when provider investigation, preservation, deletion, or containment is needed.

## Assessment

- What data/content was involved, whose data, and how many people?
- Was the event source-photo, generated-image, metadata, credential, device, browser, log, contract, or accessibility related?
- When did it begin/end; who accessed it; was it downloaded or disclosed?
- Which legal/contractual notification timelines apply?
- Can affected data be deleted, access revoked, or results recalled?

## Communication

Use district-approved notices. State verified facts, actions taken, remaining uncertainty, contact information, and protective steps. Do not claim “no impact” or “fully deleted” without evidence.

## Recovery and lessons

Require written approval before re-enabling portraits. Document root cause, control changes, tests, policy/form updates, provider responses, responsible owner, completion dates, and a follow-up exercise.

