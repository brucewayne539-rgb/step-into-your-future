"""Conservative display guidance, not certification of generated-image compliance.

Reviewed 2026-09-23 against Army's uniforms/grooming guide and DAFI 36-2903
guidance. Exact uniform insignia remain outside these generic demonstrations.
https://www.army.mil/uniforms/
https://www.afpc.af.mil/Career-Management/Dress-and-Appearance/
"""
from army_school_pathways import DATA as ARMY_PROFILES

REVISION = "military-workplace-20260923-v1"

COMMON = """Military career display: portray a credible working professional, not a fashion or glamour portrait. Preserve the reference person's facial identity, natural hair texture and believable selected adult age; do not preserve an unsuitable student hairstyle. Keep grooming neat and practical. Secure long hair in a compact bun or secured braids, clear of the face, collar, controls and equipment; fully contain any trailing lengths near machinery. Do not use a painfully tight hairstyle. Short hair should be neatly trimmed and compatible with headgear. For the male sample use a clean-shaven face and neat tapered hair without changing natural texture. Show short, practical unpainted nails, understated natural makeup if any, no exaggerated lashes, beauty retouching or fashion pose. Avoid dangling jewelry, loose accessories and clothing that could catch in equipment. Clothing and protective equipment must fit the actual job and task, with headgear, headset and eye protection fitting correctly without hair obstructing them. Show a calm, safe training or paused-work moment; never sacrifice necessary protection to expose the face. Do not invent rank, decorations or credentials. These are generic illustrative scenes, not certified depictions of an official uniform."""

TASKS = {
    "office": "Show a practical office, communications or planning workspace with understated work clothing. Do not add workshop protective gear to a desk-only scene. Keep hair secured and clear of any working headset.",
    "maintenance": "Show a maintenance inspection beside stationary, powered-down equipment. Use fitted work coveralls or a practical work shirt and trousers, safety glasses and sturdy footwear if visible. Fully secure hair; no jewelry, loose sleeves, tie or glamour clothing. Use gloves only when appropriate to the depicted task, never near rotating machinery. For tire work show the vehicle safely supported, never a person beneath a vehicle held only by a jack.",
    "construction": "Show a safe engineering or construction inspection, with task-appropriate hard hat, eye protection, sturdy workwear and boots if visible. Keep hair contained. Avoid active heavy equipment, exposed live wiring or staged dangerous work.",
    "flight": "Show a parked unmarked aircraft or flight simulator. Use practical plain flight-work clothing, a properly fitted aviation headset, and fully secured hair clear of headset, controls and harness. No flowing hair, jewelry or business-fashion outfit. Do not invent an operational helmet or oxygen system.",
    "atc": "Show an air traffic control training console, a correctly worn communications headset and practical duty clothing. Secure long hair in a compact bun or secured braids, with no trailing lengths over shoulders, headset or microphone. Do not copy the student's loose hairstyle.",
    "clinical": "Show a calm clinical training or consultation setting with clean practical clinical attire and secured hair. Keep nails short and unpainted, jewelry absent and sleeves appropriate for hygiene. Use task-appropriate clinical protection when a procedure is depicted; prefer a non-procedural scene without patients, blood or injury.",
    "laboratory": "Show a safe laboratory training setting with a closed lab coat, safety eyewear, secured hair and gloves only as appropriate to the task. No food, exposed hazardous substances or unsafe handling.",
    "food": "Show a hygienic food-service or food-inspection setting with clean work clothing and hair fully contained in a suitable hair restraint. Short unpainted nails, no hand jewelry, no loose hair near food. Show safe handling rather than a glamour kitchen pose.",
    "field": "Show safe outdoor training or readiness preparation with practical fitted outdoor workwear, secured hair and footwear suited to the terrain. Equipment and protective gear should fit the task. No combat, weapons, injury or dangerous stunt.",
    "logistics": "Show safe logistics planning or inventory inspection with practical workwear and secured hair. In a warehouse use suitable footwear and task-appropriate visibility or head protection; keep clear of moving vehicles and suspended loads.",
}

ARMY_TASK_GROUPS = {
    "maintenance": {"mechanical", "aircraft_mechanical", "electronics", "fabrication", "utilities"},
    "construction": {"construction", "engineering", "electrical_power", "plumbing", "construction_equipment"},
    "flight": {"flight"},
    "atc": {"atc"},
    "clinical": {"clinical", "nursing", "animal", "dental", "behavioral", "rehabilitation", "optical", "pharmacy", "hearing_vision", "mortuary", "radiological"},
    "laboratory": {"life_science", "chemistry_lab", "environment"},
    "food": {"culinary", "food_safety"},
    "field": {"field", "rigging", "diving", "cbrn", "emergency", "policing", "animal_handling", "fire_support", "air_defense"},
    "logistics": {"logistics", "transport"},
}

JETFORCE_TASKS = {
    "propulsion": "maintenance", "atc": "atc", "pilot": "flight",
    "engineer": "office", "cyber": "office", "medical": "clinical",
    "intelligence": "office", "logistics": "logistics", "security": "field", "sere": "field",
}


def portrait_guidance(mode, career):
    """Common guidance covers every role; explicit profiles tailor the work scene."""
    if mode == "army":
        profile = ARMY_PROFILES["roles"][career]
        task = next((name for name, profiles in ARMY_TASK_GROUPS.items() if profile in profiles), "office")
    elif mode == "jetforce":
        task = JETFORCE_TASKS.get(career, "office")
    else:
        return ""
    return COMMON + "\nWorkplace detail: " + TASKS[task]
