"""Practical display choices for civilian school career portraits.

These directions are an illustration standard, not a claim that all employers
or aviation authorities have identical grooming regulations.
"""
REVISION = "school-workplace-20260923-v1"

WORKPLACE = """Workplace appearance: preserve the person's recognizable facial identity, natural hair texture and selected adult age while adapting grooming to the work. Show practical job-appropriate clothing, posture and protective equipment, not a fashion or glamour pose. Where hair could interfere with equipment, hygiene, vision or protective gear, secure it neatly away from the face and working area. Contain long hair around machinery, food preparation and clinical procedures. Do not copy loose hair from the reference when unsuitable for the task. Keep jewelry, nails and sleeves appropriate for the work; avoid dangling accessories around tools. Protective equipment must fit and must not be removed just to reveal the face. For an office-only scene, do not add unnecessary industrial protective gear."""

AVIATION = """For any pilot or cockpit depiction, show long hair neatly secured in a compact bun or secured braids with no loose lengths over the shoulders, face, headset, harness or controls. Use a properly fitted aviation headset and practical civilian pilot clothing in a parked unmarked aircraft or simulator. Preserve facial identity and natural hair texture. This is our conservative visual standard for a safe, professional example, not a universal civilian aviation grooming law or an airline-specific uniform claim."""


def portrait_guidance(career):
    # Include the cockpit rule even for broader careers whose generated setting
    # could involve aviation. It is conditional on the image, not a forced scene.
    return WORKPLACE + "\n" + AVIATION
