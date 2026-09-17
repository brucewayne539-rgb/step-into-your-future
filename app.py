import os, io, base64, socket, json, secrets, time, hashlib, hmac
from collections import defaultdict, deque
from datetime import timedelta
from pathlib import Path
from bhs_catalog import (
    CAREER_COURSES as BHS_CAREER_COURSES,
    COURSES as BHS_CATALOG,
    OWNERSHIP_COURSES as BHS_OWNERSHIP_COURSES,
    PROGRAMS as BHS_PROGRAMS,
)
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory, render_template_string, make_response
from markupsafe import escape
from PIL import Image, ImageDraw, ImageFont, ImageOps, UnidentifiedImageError

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

APP_DIR = Path(__file__).resolve().parent
LEGACY_CONFIG_FILE = APP_DIR / "config.json"

def config_file():
    """Store secrets outside Desktop/OneDrive whenever possible."""
    base = os.environ.get("LOCALAPPDATA")
    if base:
        folder = Path(base) / "StepIntoYourFuture"
    else:
        folder = Path.home() / ".step_into_your_future"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "config.json"

CONFIG_FILE = config_file()

WATERMARK_TITLE = "AI-GENERATED CAREER VISUALIZATION"
WATERMARK_NOTICE = "NOT A PREDICTION | STEP INTO YOUR FUTURE - TODAY!"
DEMO_WATERMARK_TITLE = "FICTIONAL AI DEMONSTRATION"
DEMO_WATERMARK_NOTICE = "NOT A REAL STUDENT | NOT A PREDICTION"


def _watermark_font(text, maximum_width, preferred_size, minimum_size=18):
    """Return a bundled Pillow font sized to fit the available image width."""
    size = preferred_size
    while size >= minimum_size:
        font = ImageFont.load_default(size=size)
        left, top, right, bottom = font.getbbox(text)
        if right - left <= maximum_width:
            return font
        size -= 2
    return ImageFont.load_default(size=minimum_size)


def burn_portrait_watermark(encoded_png, fictional_demo=False):
    """Burn the standardized disclaimer into returned portrait pixels.

    This happens server-side before the image reaches the browser, so the
    displayed, downloaded, and printed portrait all use the same marked PNG.
    Any failure is allowed to stop the request rather than release an
    unmarked portrait.
    """
    portrait_bytes = base64.b64decode(encoded_png, validate=True)
    with Image.open(io.BytesIO(portrait_bytes)) as source:
        source.load()
        portrait = source.convert("RGBA")

    width, height = portrait.size
    if width < 320 or height < 320:
        raise ValueError("generated portrait is too small to watermark safely")

    horizontal_padding = max(24, width // 28)
    vertical_padding = max(18, width // 42)
    line_spacing = max(8, width // 100)
    available_width = width - (horizontal_padding * 2)

    title_text = DEMO_WATERMARK_TITLE if fictional_demo else WATERMARK_TITLE
    notice_text = DEMO_WATERMARK_NOTICE if fictional_demo else WATERMARK_NOTICE

    title_font = _watermark_font(
        title_text,
        available_width,
        preferred_size=max(28, width // 26),
    )
    notice_font = _watermark_font(
        notice_text,
        available_width,
        preferred_size=max(22, width // 34),
        minimum_size=16,
    )

    measure = ImageDraw.Draw(portrait)
    title_box = measure.textbbox((0, 0), title_text, font=title_font)
    notice_box = measure.textbbox((0, 0), notice_text, font=notice_font)
    title_height = title_box[3] - title_box[1]
    notice_height = notice_box[3] - notice_box[1]
    band_height = vertical_padding * 2 + title_height + line_spacing + notice_height
    band_top = height - band_height

    overlay = Image.new("RGBA", portrait.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, band_top, width, height), fill=(5, 52, 40, 226))
    draw.rectangle((0, band_top, width, band_top + max(3, width // 300)), fill=(126, 216, 184, 255))

    def draw_centered(text, font, box, top):
        text_width = box[2] - box[0]
        x = (width - text_width) // 2 - box[0]
        y = top - box[1]
        draw.text(
            (x, y),
            text,
            font=font,
            fill=(255, 255, 255, 255),
            stroke_width=1,
            stroke_fill=(0, 24, 18, 255),
        )

    title_top = band_top + vertical_padding
    draw_centered(title_text, title_font, title_box, title_top)
    notice_top = title_top + title_height + line_spacing
    draw_centered(notice_text, notice_font, notice_box, notice_top)

    marked = Image.alpha_composite(portrait, overlay).convert("RGB")
    output = io.BytesIO()
    marked.save(output, format="PNG", optimize=True)
    return base64.b64encode(output.getvalue()).decode("ascii")

app = Flask(__name__)


def env_flag(name, default=False):
    """Read a conservative boolean environment flag."""
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


HOSTED = bool(os.environ.get("RENDER") or env_flag("HTTPS_ONLY"))
SECRET_KEY_CONFIGURED = bool((os.environ.get("SECRET_KEY") or "").strip())
PORTRAITS_ENABLED = env_flag("PORTRAITS_ENABLED", default=not HOSTED)
ADMIN_PREVIEW_ENABLED = env_flag("ADMIN_PREVIEW_ENABLED", default=True)
OPENAI_ZDR_CONFIRMED = env_flag("OPENAI_ZDR_CONFIRMED")
SCHOOL_PORTRAIT_APPROVED = env_flag("SCHOOL_PORTRAIT_APPROVED")
PRIVACY_CONTACT_EMAIL = (os.environ.get("PRIVACY_CONTACT_EMAIL") or "").strip()
OPERATOR_NAME = (os.environ.get("OPERATOR_NAME") or "Step Into Your Future").strip()
RATE_BUCKETS = defaultdict(deque)

@app.route("/app-icon.png")
def app_icon():
    return send_from_directory(app.root_path, "app-icon.png", mimetype="image/png")
@app.route("/bhs-hero.svg")
def bhs_hero():
    return send_from_directory(app.root_path, "bhs-hero.svg", mimetype="image/svg+xml")
@app.route("/apple-touch-icon.png")
def apple_touch_icon():
    return send_from_directory(app.root_path, "app-icon.png", mimetype="image/png")
@app.route("/manifest.json")
def manifest():
    return send_from_directory(app.root_path, "manifest.json", mimetype="application/manifest+json")
@app.route("/ghs-manifest.json")
def ghs_manifest():
    return send_from_directory(app.root_path, "ghs-manifest.json", mimetype="application/manifest+json")
@app.route("/ghs-app-icon.png")
def ghs_app_icon():
    return send_from_directory(app.root_path, "ghs-app-icon.png", mimetype="image/png")
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024
app.config["MAX_FORM_MEMORY_SIZE"] = 13 * 1024 * 1024
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_NAME"] = "siyf_session"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=60)
app.config["SESSION_REFRESH_EACH_REQUEST"] = False
if HOSTED:
    app.config["SESSION_COOKIE_SECURE"] = True

ACCESS_CODE = (os.environ.get("DEMO_ACCESS_CODE") or "").strip()
GHS_DATA = json.loads((APP_DIR / "ghs_data.json").read_text(encoding="utf-8"))
GHS_CAREERS = GHS_DATA["careers"]


def load_ghs_embedded_json(constant_name):
    """Load catalog-backed GHS data embedded in the self-contained GHS page."""
    source = (APP_DIR / "templates" / "ghs.html").read_text(encoding="utf-8")
    marker = f"const {constant_name}="
    start = source.find(marker)
    if start < 0:
        raise RuntimeError(f"Missing GHS data constant: {constant_name}")
    value, _ = json.JSONDecoder().raw_decode(source[start + len(marker):])
    return value


GHS_COURSE_CATALOG = load_ghs_embedded_json("COURSE_CATALOG")
GHS_CAREER_MATCHES = load_ghs_embedded_json("CAREER_MATCHES")
DEMO_STUDENTS = {
    "grade9": {
        "grade": "9",
        "label": "Fictional Sample Student — Grade 9",
        "file": "demo-student-grade-9.png",
    },
    "grade11": {
        "grade": "11",
        "label": "Fictional Sample Student — Grade 11",
        "file": "demo-student-grade-11.png",
    },
}

ARMIE_PRIORITIES = {
    "Technology and cyber",
    "Helping and protecting people",
    "Aviation",
    "Hands-on mechanical work",
    "Leadership",
    "Logistics and organization",
}

# Student-friendly Army career families. Exact job availability, eligibility,
# training and service commitments must be confirmed with official Army sources.
ARMY_CAREERS = {
    "Cyber Operations Specialist": {
        "school_match": "Cybersecurity Specialist",
        "summary": "Help protect Army networks, systems and information while building advanced cyber and technical skills.",
        "steps": [
            ["Build the foundation", "Strengthen computer science, algebra, writing and careful problem-solving in high school."],
            ["Explore service options", "Compare enlisted, officer, Active Duty, Army Reserve and Army National Guard pathways with trusted adults and official Army sources."],
            ["Confirm eligibility", "Review current age, education, citizenship, medical, testing and security requirements with an official recruiter."],
            ["Complete training", "If selected, complete required initial military training and job-specific cyber training."],
            ["Grow your skills", "Pursue approved certifications, leadership experience and civilian-transferable technical skills while serving."],
        ],
        "scene": "a secure modern military cyber operations center, working at computer displays, wearing a neat generic U.S. Army-style operational uniform without readable insignia, rank, name tape or unit markings",
        "timeline": "Preparation can begin in high school. Training length and service commitment depend on the exact pathway and current Army requirements.",
        "keys": ["Computer systems", "Analytical thinking", "Attention to detail", "Ethics and teamwork"],
    },
    "Combat Medic Specialist": {
        "school_match": "Registered Nurse",
        "summary": "Provide emergency medical support and patient care as part of an Army healthcare team.",
        "steps": [
            ["Build the foundation", "Focus on biology, anatomy, health, communication and physical readiness."],
            ["Explore the role", "Learn how military medical work differs from civilian nursing, EMT and other healthcare careers."],
            ["Confirm eligibility", "Review current medical, physical, testing and service requirements with an official recruiter."],
            ["Complete training", "If selected, complete required initial military training and job-specific medical instruction."],
            ["Keep learning", "Maintain required skills and explore approved credentials or later civilian healthcare education."],
        ],
        "scene": "a clean military medical clinic, wearing a neat generic U.S. Army-style operational uniform without readable insignia, calmly preparing medical equipment, no injury, blood, emergency or weapon visible",
        "timeline": "High-school preparation can start now. The exact training sequence and commitment depend on the current role and service option.",
        "keys": ["Medical knowledge", "Calm decision-making", "Compassion", "Teamwork"],
    },
    "Army Aviation Specialist": {
        "school_match": "Engineer",
        "summary": "Support Army aviation through flight operations, aircraft systems, maintenance or a future pilot pathway.",
        "steps": [
            ["Build the foundation", "Strengthen math, physics, technology, communication and disciplined study habits."],
            ["Compare aviation paths", "Explore enlisted aviation jobs, warrant officer flight paths and commissioned officer options."],
            ["Confirm eligibility", "Ask official sources about current testing, medical, vision, education and selection requirements."],
            ["Complete training", "If selected, complete the military and aviation training required for the exact role."],
            ["Develop expertise", "Build safety, technical, leadership and aviation skills through continuing training."],
        ],
        "scene": "inside a bright Army aviation hangar beside a generic utility helicopter, wearing appropriate aviation work clothing without readable insignia, rank, name tape, logos or unit markings",
        "timeline": "Aviation pathways vary widely. Officer and flight routes may require additional education, testing and selection.",
        "keys": ["Math and physics", "Safety mindset", "Technical precision", "Communication"],
    },
    "Intelligence Analyst": {
        "school_match": "Data Scientist / AI Specialist",
        "summary": "Organize and analyze information to help Army leaders understand situations and make informed decisions.",
        "steps": [
            ["Build the foundation", "Take strong history, geography, writing, statistics and technology courses."],
            ["Practice analysis", "Learn to compare sources, identify bias, explain evidence and protect sensitive information."],
            ["Confirm eligibility", "Review current testing, citizenship and security-screening requirements with official sources."],
            ["Complete training", "If selected, complete initial military training and job-specific intelligence instruction."],
            ["Grow professionally", "Develop research, briefing, language, regional or technical specialties as opportunities allow."],
        ],
        "scene": "a professional military analysis center with maps and data displays containing no sensitive or readable information, wearing a generic U.S. Army-style operational uniform without readable insignia or rank",
        "timeline": "Preparation can begin in high school; selection and training depend on current eligibility and security requirements.",
        "keys": ["Research", "Critical thinking", "Clear briefing", "Discretion"],
    },
    "Wheeled Vehicle Mechanic": {
        "school_match": "Automotive Technician",
        "summary": "Inspect, maintain and repair Army vehicles while developing practical mechanical and diagnostic skills.",
        "steps": [
            ["Build the foundation", "Study automotive systems, power technology, algebra, electronics and shop safety."],
            ["Get hands-on", "Practice tool use, maintenance routines, troubleshooting and teamwork in approved settings."],
            ["Confirm eligibility", "Discuss current testing, medical and service requirements with an official recruiter."],
            ["Complete training", "If selected, complete initial military training and job-specific mechanical instruction."],
            ["Build credentials", "Explore approved technical certifications and civilian-transferable maintenance experience."],
        ],
        "scene": "a clean Army vehicle maintenance bay beside a generic wheeled utility vehicle, using professional diagnostic tools and wearing safe work clothing without readable insignia, logos or rank",
        "timeline": "Technical preparation can start in high school; exact training and commitments vary by service option and assignment.",
        "keys": ["Diagnostics", "Tool safety", "Mechanical systems", "Reliability"],
    },
    "Signal Support Systems Specialist": {
        "school_match": "Software Developer",
        "summary": "Help teams stay connected by supporting communications equipment, networks and information systems.",
        "steps": [
            ["Build the foundation", "Study computer science, electronics, algebra, communication and structured troubleshooting."],
            ["Explore systems", "Practice networking, hardware setup, documentation and responsible technology use."],
            ["Confirm eligibility", "Review current testing, citizenship and security requirements through official channels."],
            ["Complete training", "If selected, complete initial military training and job-specific signal instruction."],
            ["Keep advancing", "Build technical expertise, approved certifications and leadership experience."],
        ],
        "scene": "a modern military communications workspace with radios and network equipment, no readable screens, wearing a generic U.S. Army-style operational uniform without readable insignia, rank or name tape",
        "timeline": "Preparation can start now; exact training length and service requirements depend on the selected communications role.",
        "keys": ["Networking", "Troubleshooting", "Communication", "Team reliability"],
    },
    "Logistics and Supply Specialist": {
        "school_match": "Business Administration / Manager",
        "summary": "Coordinate equipment, inventory and supplies so Army teams have what they need when they need it.",
        "steps": [
            ["Build the foundation", "Strengthen organization, spreadsheets, business math, communication and accountability."],
            ["Practice logistics", "Learn inventory control, scheduling, documentation and safe material handling."],
            ["Confirm eligibility", "Review current role availability and entry requirements with official Army sources."],
            ["Complete training", "If selected, complete initial military training and job-specific logistics instruction."],
            ["Lead and improve", "Build supervisory, planning and civilian-transferable supply-chain skills."],
        ],
        "scene": "a bright organized military logistics center with labeled generic containers and inventory tablets showing no readable data, wearing a generic U.S. Army-style operational uniform without insignia or rank",
        "timeline": "Preparation can begin in high school; exact training and duties vary across supply and logistics roles.",
        "keys": ["Organization", "Inventory accuracy", "Planning", "Accountability"],
    },
    "Public Affairs Specialist": {
        "school_match": "TV News Reporter / Local Anchor",
        "summary": "Tell Army stories accurately through writing, photography, video, interviews and digital communication.",
        "steps": [
            ["Build the foundation", "Take writing, journalism, public speaking, photography and digital media courses."],
            ["Create a portfolio", "Practice interviewing, fact-checking, video editing and ethical storytelling."],
            ["Confirm eligibility", "Review current testing and job requirements with an official recruiter."],
            ["Complete training", "If selected, complete initial military training and job-specific public affairs instruction."],
            ["Grow your voice", "Build reporting, visual, social-media and leadership experience while maintaining accuracy."],
        ],
        "scene": "a professional military media workspace while preparing a camera interview, wearing a generic U.S. Army-style operational uniform without readable insignia, with no logos or readable screens",
        "timeline": "A strong school media portfolio can begin now; exact training and assignments depend on current Army needs.",
        "keys": ["Writing", "Interviewing", "Visual storytelling", "Accuracy"],
    },
    "Human Resources Specialist": {
        "school_match": "Business Administration / Manager",
        "summary": "Support Soldiers and units by maintaining personnel information and helping manage administrative services.",
        "steps": [
            ["Build the foundation", "Develop business, writing, spreadsheet, customer-service and confidentiality skills."],
            ["Practice service", "Learn accurate recordkeeping, professional communication and respectful problem-solving."],
            ["Confirm eligibility", "Check current testing and entry requirements through official Army sources."],
            ["Complete training", "If selected, complete initial military training and job-specific personnel instruction."],
            ["Advance", "Build administrative, leadership and civilian-transferable human-resources skills."],
        ],
        "scene": "a professional military personnel office, helping a colleague with paperwork at a modern workstation, wearing a generic U.S. Army-style operational uniform without readable insignia, rank or name tape",
        "timeline": "Preparation can start with business and communication courses; exact training varies by role and service option.",
        "keys": ["Accuracy", "Confidentiality", "Customer service", "Organization"],
    },
    "Culinary Specialist": {
        "school_match": "Chef / Restaurant Owner",
        "summary": "Prepare safe, nutritious meals and support food-service operations for Army teams.",
        "steps": [
            ["Build the foundation", "Study culinary arts, food safety, nutrition, measurement and teamwork."],
            ["Practice the craft", "Develop knife skills, sanitation, timing, volume preparation and inventory habits."],
            ["Confirm eligibility", "Review current role availability and entry requirements with official Army sources."],
            ["Complete training", "If selected, complete initial military training and job-specific culinary instruction."],
            ["Keep developing", "Build leadership, food-service management and civilian-transferable culinary skills."],
        ],
        "scene": "a spotless large-scale military kitchen preparing a healthy meal, wearing professional culinary clothing with subtle generic Army styling and no readable logos or insignia",
        "timeline": "Culinary skills can begin in high school; exact training and assignments depend on the current Army pathway.",
        "keys": ["Food safety", "Timing", "Teamwork", "Consistency"],
    },
}

try:
    MAX_GENERATIONS_PER_SESSION = max(0, min(10, int(os.environ.get("MAX_GENERATIONS_PER_SESSION", "2"))))
except ValueError:
    MAX_GENERATIONS_PER_SESSION = 2
try:
    MAX_ADMIN_PREVIEW_GENERATIONS = max(1, min(10, int(os.environ.get("MAX_ADMIN_PREVIEW_GENERATIONS", "6"))))
except ValueError:
    MAX_ADMIN_PREVIEW_GENERATIONS = 6


def csrf_token():
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def request_has_valid_csrf():
    supplied = request.headers.get("X-CSRF-Token", "")
    if not supplied:
        supplied = request.form.get("_csrf_token", "")
    expected = session.get("csrf_token", "")
    return bool(expected and supplied and secrets.compare_digest(supplied, expected))


def anonymous_client_key():
    """Create an in-memory, rotating pseudonymous client key; never log the IP."""
    address = (request.headers.get("X-Forwarded-For") or request.remote_addr or "unknown").split(",", 1)[0].strip()
    return hmac.new(app.secret_key.encode("utf-8"), address.encode("utf-8"), hashlib.sha256).hexdigest()[:24]


def rate_limited(bucket_name, limit, window_seconds):
    if len(RATE_BUCKETS) > 10_000:
        RATE_BUCKETS.clear()
    now = time.monotonic()
    bucket = RATE_BUCKETS[(bucket_name, anonymous_client_key())]
    while bucket and bucket[0] <= now - window_seconds:
        bucket.popleft()
    if len(bucket) >= limit:
        return True
    bucket.append(now)
    return False


def portrait_gate():
    """Return a supportable hosted-portrait status without claiming legal approval."""
    if not PORTRAITS_ENABLED:
        return False, "Portrait mode is disabled. The no-photo career roadmap remains available."
    if HOSTED and not SECRET_KEY_CONFIGURED:
        return False, "Portrait mode requires a configured server session secret."
    if HOSTED and not ACCESS_CODE:
        return False, "Portrait mode requires restricted teacher access on a hosted deployment."
    if HOSTED and not OPENAI_ZDR_CONFIRMED:
        return False, "Portrait mode is awaiting written confirmation that Zero Data Retention is enabled for the OpenAI project."
    if HOSTED and not SCHOOL_PORTRAIT_APPROVED:
        return False, "Portrait mode is awaiting the school's documented privacy and authorization approval."
    if HOSTED and ("@" not in PRIVACY_CONTACT_EMAIL or len(PRIVACY_CONTACT_EMAIL) > 254):
        return False, "Portrait mode requires a published privacy contact for family and school requests."
    if not load_key() or OpenAI is None:
        return False, "Portrait service setup is incomplete. The no-photo roadmap remains available."
    return True, "Portrait mode is enabled for this approved deployment."


def admin_preview_gate():
    """Allow only synthetic, bundled faces in the protected sales preview."""
    if not ADMIN_PREVIEW_ENABLED:
        return False, "Administrator Preview has been hidden for this deployment."
    if HOSTED and not SECRET_KEY_CONFIGURED:
        return False, "Administrator Preview requires a configured server session secret."
    if HOSTED and not ACCESS_CODE:
        return False, "Administrator Preview requires restricted teacher/admin access."
    if not load_key() or OpenAI is None:
        return False, "The image service setup is incomplete."
    return True, "Administrator Preview is ready for fictional sample students."


@app.before_request
def verify_mutating_request():
    if request.method in {"POST", "PUT", "PATCH", "DELETE"} and not request_has_valid_csrf():
        if request.path.startswith("/api/"):
            return jsonify(ok=False, error="This request expired or did not come from this app. Refresh the page and try again."), 400
        return "This form expired. Return to the app, refresh the page, and try again.", 400

CAREERS = {
    "Architect": {
        "summary":"Design buildings and spaces by combining creativity, math, technology, codes and collaboration.",
        "steps":[
            ["High School","Geometry, algebra, physics, art/design, CAD or technology courses when available."],
            ["College / Degree","Explore an accredited architecture degree or another approved route toward professional licensure."],
            ["Experience","Job-shadow, intern, build a portfolio, and seek design/engineering exposure."],
            ["Licensure","Complete required professional experience and licensing examinations for the state where you plan to practice."],
            ["Launch","Join a design firm, specialize, or eventually create your own practice."]
        ],
        "scene":"a modern architectural studio with drawings, scale models, blueprints, and a contemporary building visible through windows"
    },
    "Electrician": {
        "summary":"Install, troubleshoot and maintain electrical systems in homes, businesses, industry and new construction.",
        "steps":[
            ["High School","Algebra, physics, technology/shop courses, measurement, safety and problem solving."],
            ["Apprenticeship","Apply for a registered apprenticeship or employer/union training route combining paid work and classroom instruction."],
            ["Licensing","Complete required hours and state examinations for the appropriate electrical credential."],
            ["Experience","Build residential, commercial or industrial troubleshooting, code and customer-service skills."],
            ["Business Option","With experience and proper licensing, explore estimating, insurance, accounting and owning a company."]
        ],
        "scene":"a clean commercial electrical work site, wearing appropriate professional electrician work clothing and safety equipment, with tools and electrical panels in the background"
    },
    "Registered Nurse": {
        "summary":"Provide direct patient care, coordinate treatment, and educate patients and families.",
        "steps":[
            ["High School","Biology, chemistry, algebra, health sciences and strong English courses."],
            ["Nursing Program","Complete an approved ADN or BSN nursing program."],
            ["Clinical Experience","Complete supervised clinical rotations in approved healthcare settings."],
            ["Licensure","Pass the NCLEX-RN and satisfy state licensing requirements."],
            ["Launch","Work in hospitals, clinics, schools, community health or a specialty area."]
        ],
        "scene":"a bright modern hospital or medical center, wearing professional nursing scrubs with no visible logos, in a realistic clinical environment"
    },
    "Veterinarian": {
        "summary":"Diagnose and treat animals while advising owners about health, prevention and care.",
        "steps":[
            ["High School","Biology, chemistry, physics, math and animal-care experiences."],
            ["Bachelor's Preparation","Complete college prerequisites and gain animal/veterinary experience."],
            ["Veterinary School","Complete an accredited Doctor of Veterinary Medicine program."],
            ["Licensure","Complete applicable national and state licensing requirements."],
            ["Launch","Work in a clinic, specialty practice, public health, research or eventually own a practice."]
        ],
        "scene":"a welcoming modern veterinary clinic, wearing professional veterinary clothing, with a friendly dog nearby and medical equipment subtly in the background"
    },
    "Software Developer": {
        "summary":"Design and build software, websites, apps and digital systems.",
        "steps":[
            ["High School","Algebra, computer science, technology and logic-rich courses; build small coding projects."],
            ["Build Skills","Programming fundamentals, Git, web development, databases and problem solving."],
            ["Education","Compare computer science, software engineering, IT, community college, certificates or validated training routes."],
            ["Portfolio","Build real projects, internships, hackathons or open-source work."],
            ["Launch","Apply for junior developer roles, apprenticeships or internships and keep building a portfolio."]
        ],
        "scene":"a modern software development workspace with code on monitors, collaborative technology office setting, professional casual clothing"
    },
    "Teacher": {
        "summary":"Help students learn, grow and build skills in a classroom or specialized educational setting.",
        "steps":[
            ["High School","Strong writing, communication, subject-area knowledge and experience working with younger students."],
            ["College","Complete an approved educator-preparation program and degree appropriate to the intended subject/grade level."],
            ["Student Teaching","Complete supervised field experiences and student teaching."],
            ["Certification","Meet state educator certification requirements for the intended endorsement."],
            ["Launch","Apply to districts, continue professional learning and consider additional endorsements."]
        ],
        "scene":"a bright contemporary high school classroom, standing near a smart board and student desks, dressed as a professional educator"
    },
    "Firefighter": {
        "summary":"Respond to fires, medical emergencies, rescues and community safety needs.",
        "steps":[
            ["High School","Physical fitness, science, communication, teamwork and public-service experience."],
            ["Emergency Skills","EMT training is commonly valuable or required depending on department."],
            ["Hiring","Meet department testing, background, medical and physical ability standards."],
            ["Academy","Complete required fire academy/recruit training."],
            ["Grow","Advance through experience, EMS/fire certifications and specialty training."]
        ],
        "scene":"outside a modern fire station beside a fire engine, wearing clean professional firefighter turnout gear with helmet held at the side, no active emergency or flames"
    },
    "Police Officer": {
        "summary":"Protect the community, respond to emergencies, investigate incidents and work with residents.",
        "steps":[
            ["High School","Strong writing, fitness, communication, civics and decision-making skills."],
            ["Preparation","Explore criminal justice, public safety, military service or community-college pathways if useful."],
            ["Hiring Process","Meet agency age, education, background, medical, physical and examination requirements."],
            ["Academy","Complete an approved police academy and field training."],
            ["Grow","Develop expertise in community policing, investigations, youth services or leadership."]
        ],
        "scene":"a professional community-policing setting outside a civic building, wearing a generic police uniform with no real department insignia, calm non-confrontational scene"
    },
    "TV News Reporter / Local Anchor": {
        "summary":"Research, report and explain news stories clearly on camera and across digital platforms.",
        "steps":[
            ["High School","Writing, English, history/current events, public speaking, video production and media literacy."],
            ["College / Training","Explore journalism, communications, broadcasting, political science or a related field."],
            ["Create a Reel","Work on school media, podcasts or video projects; learn interviewing, editing and fact-checking."],
            ["Internships","Seek newsroom, local-TV, radio, digital-media or communications internships."],
            ["Launch","Build an on-air/digital portfolio and begin in reporting, production or multimedia journalism."]
        ],
        "scene":"a polished local television newsroom and anchor desk, professional broadcast attire, studio cameras and screens in the background with generic graphics and no real station logo"
    },
    "Broadway Director / Actor": {
        "summary":"Build a professional life in theatre through acting, directing, auditions, rehearsal and production experience.",
        "steps":[
            ["High School","Theatre, English, music, dance, public speaking and production courses; perform whenever possible."],
            ["Training","Consider BFA/BA theatre programs, conservatory study, workshops, voice, movement and directing training."],
            ["Portfolio","Develop headshots, résumé, reels, directing materials and a record of productions."],
            ["Experience","Audition, assist directors, join productions, pursue internships and build professional relationships."],
            ["Launch","Pursue regional theatre, touring and New York opportunities; understand representation and union pathways."]
        ],
        "scene":"inside a beautiful professional Broadway-style theatre during rehearsal, stage lights glowing, dressed in stylish theatre-professional clothing, with stage and empty seats visible"
    },
    "Chef / Restaurant Owner": {
        "summary":"Create food, lead kitchen teams and potentially build a restaurant or food business.",
        "steps":[
            ["High School","Culinary, business, math and food-safety courses; seek restaurant experience."],
            ["Training","Choose culinary school, community college or direct kitchen apprenticeship/work experience."],
            ["Experience","Learn prep, line cooking, inventory, costing, sanitation and customer service."],
            ["Business Skills","Study bookkeeping, pricing, purchasing, staffing, marketing and licensing."],
            ["Ownership Option","Develop a concept and business plan; verify local food-service, health and business requirements."]
        ],
        "scene":"a beautiful modern restaurant kitchen, wearing professional chef attire, plated food and culinary workspace visible, clean and realistic"
    },
    "Automotive Technician": {
        "summary":"Diagnose, repair and maintain cars and light trucks using mechanical and computerized systems.",
        "steps":[
            ["High School","Automotive, technology, algebra, physics and shop safety courses where available."],
            ["Training","Consider technical school, community college, manufacturer programs or employer apprenticeship."],
            ["Hands-On Practice","Build diagnostic, electrical, brake, engine and computer-scanning skills."],
            ["Credentials","Work toward recognized industry certifications as experience requirements are met."],
            ["Launch","Join a dealership, independent shop, fleet operation or eventually operate a repair business."]
        ],
        "scene":"a clean modern automotive service center beside a vehicle on a lift, wearing professional technician workwear, diagnostic equipment visible"
    },
    "Physical Therapist": {
        "summary":"Help people restore movement, strength and function after injury or illness.",
        "steps":[
            ["High School","Biology, anatomy, chemistry, physics and math; volunteer around healthcare or athletics."],
            ["Bachelor's Degree","Complete prerequisite coursework for Doctor of Physical Therapy programs."],
            ["DPT Program","Complete an accredited Doctor of Physical Therapy program and clinical rotations."],
            ["Licensure","Pass required national/state examinations and satisfy state licensing rules."],
            ["Launch","Work in hospitals, outpatient clinics, schools, sports medicine, home care or specialty practice."]
        ],
        "scene":"a bright modern physical therapy clinic with rehabilitation equipment, dressed as a healthcare professional, calm positive environment"
    },
    "Plumber": {
        "summary":"Install, repair and maintain water, drainage and piping systems in homes, businesses and construction projects.",
        "steps":[
            ["High School","Build math, measurement, mechanical reasoning, blueprint-reading and shop-safety skills."],
            ["Apprenticeship","Pursue a registered apprenticeship or approved employer/union training route with paid on-the-job learning."],
            ["Licensing","Complete required training hours and state or local licensing examinations where required."],
            ["Experience","Develop strong service, code, troubleshooting, estimating and customer-communication skills."],
            ["Business Option","With experience and proper licensing, explore estimating, insurance, bookkeeping and owning a plumbing company."]
        ],
        "scene":"a clean residential or commercial plumbing work site, wearing professional trade workwear and safety equipment, with piping, tools and fixtures visible"
    },
    "Business Administration / Manager": {
        "summary":"Plan, organize and lead people, budgets and operations so an organization can reach its goals.",
        "steps":[
            ["High School","Strengthen writing, math, economics, technology, teamwork and public-speaking skills."],
            ["Education","Explore business administration, management, accounting, marketing or related college and certificate pathways."],
            ["Experience","Seek internships, part-time work, clubs or projects that build leadership and customer-service experience."],
            ["Build Skills","Learn budgeting, spreadsheets, project management, hiring, communication and data-informed decision making."],
            ["Launch","Begin in an entry-level business role and grow toward supervision, operations, department leadership or entrepreneurship."]
        ],
        "scene":"a modern business office or conference room, dressed in professional business attire, leading a collaborative team meeting with charts and laptops visible"
    },
    "Carpenter": {
        "summary":"Build, install and repair structures and finishes using wood and other construction materials.",
        "steps":[
            ["High School","Focus on measurement, geometry, construction technology, drafting and safe tool use."],
            ["Training","Consider a registered apprenticeship, technical program or supervised employer training route."],
            ["Hands-On Skills","Develop framing, finish carpentry, blueprint reading, layout, installation and job-site safety skills."],
            ["Experience","Build a strong work record and learn estimating, scheduling, codes and customer service."],
            ["Business Option","With experience, explore specialty work, foreperson roles, contracting requirements and business ownership."]
        ],
        "scene":"a bright active construction or custom woodworking site, wearing professional carpenter workwear and safety gear, with framing, quality tools and plans visible"
    },
    "Graphic Designer": {
        "summary":"Create visual communications for print, digital media, brands, campaigns, products and organizations.",
        "steps":[
            ["High School","Take art, design, photography, technology and communication courses; practice composition and typography."],
            ["Training","Explore graphic design, visual communication, digital media or related college/certificate programs."],
            ["Portfolio","Create strong examples of logos, layouts, posters, social media, web and motion/digital design."],
            ["Experience","Seek school projects, internships, freelance assignments and real-client work while learning feedback and deadlines."],
            ["Launch","Apply for junior design roles, agency/in-house positions or build a freelance design practice."]
        ],
        "scene":"a stylish contemporary graphic design studio, professional creative attire, large monitor showing abstract design layouts with no readable brand names, sketchbook and design tools nearby"
    },
    "Neurosurgeon": {
        "summary":"Diagnose and surgically treat complex conditions affecting the brain, spine and nervous system.",
        "steps":[
            ["High School","Take challenging biology, chemistry, physics and math courses; build study, teamwork and communication skills."],
            ["College","Complete a bachelor's degree and required pre-medical coursework while gaining healthcare, research or service experience."],
            ["Medical School","Complete medical school and earn an MD or DO degree."],
            ["Residency","Complete a highly competitive neurosurgery residency and required licensing examinations; some physicians pursue additional fellowship training."],
            ["Career","Become licensed and credentialed, practice in a hospital or specialty group, and continue extensive professional education."]
        ],
        "scene":"a state-of-the-art neurosurgery operating room or surgical planning suite, wearing appropriate sterile surgical attire, sophisticated medical imaging visible, calm professional non-graphic scene"
    },
    "Cybersecurity Specialist": {
        "summary":"Protect computers, networks and information from attacks, misuse and security failures.",
        "steps":[
            ["High School","Build computer science, networking, math, logic and ethical problem-solving skills."],
            ["Training","Explore cybersecurity, IT, computer science, community college, university or respected certification pathways."],
            ["Practice","Use legal training labs, competitions and home labs to learn networking, operating systems, cloud and defensive security."],
            ["Experience","Pursue help-desk, IT, security operations, internship or apprenticeship experience and document projects."],
            ["Launch","Apply for security analyst, SOC, cloud security or related roles and continue earning experience and credentials."]
        ],
        "scene":"a modern cybersecurity operations center with multiple monitors showing generic network and security dashboards, professional technology workplace, no hacking imagery or readable private data"
    },
    "Data Scientist / AI Specialist": {
        "summary":"Use statistics, programming and machine learning to find patterns in data and build useful predictive or AI systems.",
        "steps":[
            ["High School","Take algebra, statistics, calculus when available, computer science and science courses."],
            ["Education","Explore data science, statistics, computer science, mathematics, engineering or related college pathways."],
            ["Technical Skills","Learn Python, SQL, statistics, data visualization, machine learning and responsible AI practices."],
            ["Portfolio","Build projects using public or authorized data and explain both the method and business/social value."],
            ["Launch","Seek internships and analyst/data roles; continue developing specialty expertise as tools change."]
        ],
        "scene":"a sophisticated data science and artificial intelligence workspace, professional casual attire, large displays with generic charts, models and data visualizations"
    },
    "Dental Hygienist": {
        "summary":"Provide preventive oral-health care, clean teeth, assess patients and teach healthy dental habits.",
        "steps":[
            ["High School","Biology, chemistry, health science, math and communication courses are useful preparation."],
            ["Program","Complete an accredited dental hygiene education program and required clinical experiences."],
            ["Licensure","Pass the examinations and satisfy the licensing requirements for the state where you plan to work."],
            ["Experience","Develop strong patient-care, prevention, documentation and teamwork skills in clinical settings."],
            ["Launch","Work in dental practices, public-health settings or other approved oral-health roles."]
        ],
        "scene":"a bright modern dental office, wearing professional clinical attire and protective equipment, standing beside a dental chair in a clean non-procedural setting"
    },
    "Doctor / Physician": {
        "summary":"Diagnose illness, provide treatment and guide patients in maintaining or restoring health.",
        "steps":[
            ["High School","Build a strong foundation in biology, chemistry, physics, math, writing and service."],
            ["College","Complete a bachelor's degree and pre-medical requirements while gaining healthcare, research or service experience."],
            ["Medical School","Complete an accredited MD or DO program and required licensing examinations."],
            ["Residency","Train in a chosen specialty through a supervised residency; some specialties require fellowship training."],
            ["Practice","Complete licensing/credentialing requirements and practice in hospitals, clinics, academic medicine or other settings."]
        ],
        "scene":"a bright modern medical center, wearing professional physician attire with a white coat and no logos, calmly reviewing a patient chart or medical image"
    },
    "HVAC Technician": {
        "summary":"Install, maintain and repair heating, ventilation, air-conditioning and refrigeration systems.",
        "steps":[
            ["High School","Take algebra, physics, electronics, shop/technology and safety courses when available."],
            ["Training","Explore technical school, community college, apprenticeship or employer-based HVAC training."],
            ["Credentials","Earn required refrigerant-handling and other applicable certifications and licenses."],
            ["Experience","Build diagnostic, electrical, airflow, controls and customer-service skills."],
            ["Grow","Advance into commercial systems, controls, estimating, supervision or properly licensed business ownership."]
        ],
        "scene":"a clean commercial HVAC service setting, wearing professional technician workwear and safety equipment, with modern heating and cooling equipment and diagnostic tools visible"
    },
    "Lawyer / Attorney": {
        "summary":"Advise clients, interpret laws, research issues and advocate in negotiations, transactions or court proceedings.",
        "steps":[
            ["High School","Strengthen writing, reading, research, history/civics, debate and public-speaking skills."],
            ["College","Complete a bachelor's degree in a field that develops strong reasoning, research and communication skills."],
            ["Law School","Complete an accredited law degree program and gain practical experience through clinics, internships or summer work."],
            ["Licensure","Meet character-and-fitness and bar-examination requirements for the jurisdiction where you plan to practice."],
            ["Launch","Begin in a firm, government, nonprofit, corporate legal department or another legal setting and build specialty expertise."]
        ],
        "scene":"a polished law office or courthouse conference setting, wearing professional legal attire, law books and case materials visible, no readable client information"
    },
    "Marketing / Advertising Professional": {
        "summary":"Connect products, services and causes with audiences through research, strategy, storytelling and campaigns.",
        "steps":[
            ["High School","Build writing, design, statistics, business, media-literacy and presentation skills."],
            ["Education","Explore marketing, business, communications, advertising, analytics or related college/certificate programs."],
            ["Portfolio","Create campaigns, social content, research projects and measurable examples of audience growth or engagement."],
            ["Experience","Seek internships, school organizations, local businesses or nonprofit projects to learn real deadlines and clients."],
            ["Launch","Apply for marketing coordinator, content, digital, account or analytics roles and develop a specialty."]
        ],
        "scene":"a creative marketing agency or brand strategy meeting, professional modern attire, presentation boards and generic campaign visuals in the background"
    },
    "Medical & Health Services Manager": {
        "summary":"Lead the business and operational side of healthcare organizations, departments and services.",
        "steps":[
            ["High School","Take business, math, health science, technology, writing and leadership courses."],
            ["Education","Explore healthcare administration, business, public health or related bachelor's programs; some roles value graduate study."],
            ["Experience","Seek healthcare, office, customer-service, internship or project-management experience."],
            ["Build Skills","Learn budgeting, compliance, staffing, data, quality improvement and healthcare operations."],
            ["Launch","Begin in healthcare administration or operations and advance toward department or facility leadership."]
        ],
        "scene":"a modern hospital administrative office or healthcare leadership meeting, professional business attire, clinical facility visible through glass in the background"
    },
    "Nurse Practitioner": {
        "summary":"Provide advanced nursing care, assess patients and diagnose and manage many health conditions within state scope-of-practice rules.",
        "steps":[
            ["High School","Biology, chemistry, algebra, health science, communication and service experiences."],
            ["Become an RN","Complete an approved nursing program, clinical training and RN licensure requirements."],
            ["Graduate Nursing","Complete an accredited graduate nurse-practitioner program in a population focus or specialty."],
            ["Certification / Licensure","Meet national certification and state advanced-practice licensing requirements."],
            ["Launch","Practice in clinics, hospitals, specialty care or community settings and maintain continuing education."]
        ],
        "scene":"a bright contemporary clinic, wearing professional advanced-practice nursing attire, reviewing a tablet in a calm patient-care setting with no visible logos"
    },
    "Occupational Therapist": {
        "summary":"Help people develop or regain the everyday skills they need for school, work, home and independent living.",
        "steps":[
            ["High School","Biology, psychology, health science, communication and volunteer/service experiences are useful."],
            ["College Preparation","Complete bachelor's-level prerequisites for an accredited occupational therapy graduate program."],
            ["OT Program","Complete an accredited occupational therapy graduate program and required fieldwork."],
            ["Certification / Licensure","Meet national certification and state licensing requirements."],
            ["Launch","Work in hospitals, schools, rehabilitation, pediatrics, mental health, home care or specialty practice."]
        ],
        "scene":"a warm modern occupational therapy clinic with adaptive and rehabilitation equipment, professional healthcare attire, positive non-procedural setting"
    },
    "Physician Assistant": {
        "summary":"Provide medical care on healthcare teams by evaluating patients, diagnosing conditions and helping manage treatment.",
        "steps":[
            ["High School","Biology, chemistry, anatomy, math and communication courses; explore healthcare service opportunities."],
            ["College / Prerequisites","Complete a bachelor's degree and the science/experience prerequisites required by PA programs."],
            ["PA Program","Complete an accredited physician-assistant graduate program and supervised clinical rotations."],
            ["Certification / Licensure","Pass required national certification and meet state licensing requirements."],
            ["Launch","Work in primary care, hospitals, surgery, emergency medicine or a specialty and maintain continuing education."]
        ],
        "scene":"a modern hospital or outpatient clinic, wearing professional medical attire, confidently collaborating with a healthcare team in a calm setting"
    },
    "School Counselor / Mental Health Counselor": {
        "summary":"Support people with academic, career, social-emotional or mental-health goals through counseling and guidance.",
        "steps":[
            ["High School","Psychology, sociology, health, writing, communication and service/peer-support experiences."],
            ["College","Complete a bachelor's degree with relevant coursework in psychology, education, human services or related areas."],
            ["Graduate Program","Complete the appropriate accredited master's-level counseling program for the intended role."],
            ["Credentialing","Complete supervised experience and state certification/licensure requirements for school or clinical counseling."],
            ["Launch","Work in schools, agencies, clinics, community programs or related settings and continue supervised professional development."]
        ],
        "scene":"a welcoming school counseling or professional counseling office, calm supportive atmosphere, professional attire, books and planning materials visible"
    },
    "Web / Digital Designer": {
        "summary":"Design useful, attractive websites and digital experiences by combining visual design, user needs and technology.",
        "steps":[
            ["High School","Take art/design, computer science, technology, writing and media courses; build simple websites."],
            ["Training","Explore web design, UX/UI, digital media, graphic design or front-end development pathways."],
            ["Skills","Learn layout, accessibility, responsive design, prototyping, HTML/CSS basics and user-centered design."],
            ["Portfolio","Create several polished websites or app prototypes and explain the design decisions behind them."],
            ["Launch","Apply for junior web, UI/UX or digital-design roles or begin carefully scoped freelance work."]
        ],
        "scene":"a modern UX and web design studio, professional creative attire, large screens showing generic website wireframes and colorful interface layouts with no readable brands"
    },
    "Welder / Fabricator": {
        "summary":"Join and shape metal to build, repair and manufacture structures, equipment and products.",
        "steps":[
            ["High School","Develop measurement, blueprint-reading, shop math, manufacturing and safety skills."],
            ["Training","Explore technical school, community college, apprenticeship or employer welding programs."],
            ["Hands-On Skills","Practice appropriate welding processes, cutting, fabrication, inspection and safe equipment use."],
            ["Credentials","Earn employer- or industry-recognized qualifications needed for the type of welding you want to do."],
            ["Launch","Work in construction, manufacturing, shipbuilding, repair or specialty fabrication and continue developing advanced skills."]
        ],
        "scene":"a professional metal fabrication shop, wearing complete welding protective equipment with welding helmet raised, metalwork and fabrication tables visible, no active sparks near the face"
    },
    "Engineer": {
        "summary":"Use math, science and design to solve practical problems and create systems, products, structures or technology.",
        "steps":[
            ["High School","Take strong math and science courses plus CAD, coding, robotics or engineering electives when available."],
            ["College","Explore an accredited engineering program in a field such as mechanical, civil, electrical, chemical or biomedical engineering."],
            ["Projects","Join design teams, labs, competitions, co-ops or internships and build evidence of hands-on problem solving."],
            ["Professional Path","Learn whether your specialty benefits from or requires engineering-in-training and professional licensure steps."],
            ["Launch","Begin as an entry-level engineer, develop technical expertise and grow toward project or team leadership."]
        ],
        "scene":"a modern engineering lab or design center, professional technical attire, prototypes, CAD displays and testing equipment visible"
    },
    "Accountant / Financial Manager": {
        "summary":"Help people and organizations understand money, budgets, reporting, controls and financial decisions.",
        "steps":[
            ["High School","Build algebra, statistics, spreadsheet, economics, business and communication skills."],
            ["Education","Explore accounting, finance or business degree pathways and understand credential requirements for your goals."],
            ["Experience","Seek internships or entry-level work involving bookkeeping, budgeting, audit, tax, banking or financial analysis."],
            ["Credentials","For accounting roles that require or value CPA licensure, verify the education, exam and experience rules in your state."],
            ["Launch","Start in accounting or finance and grow toward senior analyst, controller, financial manager or advisory roles."]
        ],
        "scene":"a polished finance or accounting office, professional business attire, working with generic financial charts and spreadsheets on large monitors with no private data"
    },
    "Entrepreneur / Business Owner": {
        "summary":"Create and grow a business by solving a customer problem, managing money and leading day-to-day operations.",
        "steps":[
            ["High School","Build communication, math, technology, marketing and leadership skills; try small supervised projects."],
            ["Learn the Industry","Gain real work experience in the field where you might eventually start a business."],
            ["Business Skills","Learn pricing, bookkeeping, taxes, insurance, marketing, sales, customer service and hiring basics."],
            ["Test the Idea","Research customers and competitors, estimate startup costs and test a small version before taking large risks."],
            ["Launch / Grow","Create a realistic business plan, meet legal/licensing requirements, track cash flow and grow carefully."]
        ],
        "scene":"a confident small-business owner in a contemporary office or storefront, professional attire, collaborating with a small team with generic business materials visible"
    }
}


# Seven additional careers shared with the GHS edition. Their roadmaps and
# portrait scenes are school-independent; Branford course guidance is below.
BHS_ADDITIONAL_CAREERS = [
    "Special Education Teacher",
    "Military / Armed Forces",
    "Customer Service Representative",
    "Elected Official / Politician",
    "Caregiver / Personal Care Aide",
    "Construction Manager",
    "Psychologist",
]
CAREERS.update({career: GHS_CAREERS[career] for career in BHS_ADDITIONAL_CAREERS})


ROADMAP_META = {
"Architect":("Usually 5–8+ years after high school to independent licensed practice, depending on degree and state route.",["Creative problem-solving","Math + spatial thinking","CAD/design communication","Persistence through licensure"]),
"Electrician":("Often about 4–5 years of paid apprenticeship/training before journey-level work; licensing rules vary.",["Safety first","Hands-on problem solving","Electrical code knowledge","Reliability + customer service"]),
"Registered Nurse":("Common entry routes are roughly 2–4 years after high school, followed by RN licensure.",["Science foundation","Calm communication","Clinical judgment","Compassion + teamwork"]),
"Veterinarian":("Typically 8+ years after high school: undergraduate preparation plus veterinary school and licensure.",["Strong sciences","Animal-care experience","Communication with owners","Resilience + precision"]),
"Software Developer":("Entry timing varies: college, certificate, self-directed and portfolio routes can all lead to first roles.",["Coding fundamentals","Build real projects","Debugging/problem solving","Keep learning new tools"]),
"Teacher":("Often about 4 years for a bachelor's/teacher-preparation route, plus state certification requirements.",["Communication","Patience + adaptability","Subject knowledge","Classroom leadership"]),
"Firefighter":("Entry can begin after high school; academy, EMT/medical, testing and department requirements vary.",["Physical readiness","Teamwork","Emergency judgment","Service mindset"]),
"Police Officer":("Entry timing varies by agency; eligibility, testing, academy and field training are typical milestones.",["Integrity","Communication","Sound judgment","Physical + mental readiness"]),
"TV News Reporter / Local Anchor":("Often 4 years of college plus internships/student media, though strong portfolio and experience matter greatly.",["Writing under deadline","On-camera communication","News judgment","Portfolio + networking"]),
"Broadway Director / Actor":("There is no single clock: training can start now, while credits, auditions, portfolio and professional relationships build over years.",["Consistent training","Audition resilience","Collaboration","Create + document your work"]),
"Chef / Restaurant Owner":("Entry can begin after high school; culinary school is optional for many, while experience and business skills build over time.",["Technique + food safety","Speed and consistency","Leadership","Cost control + hospitality"]),
"Automotive Technician":("Often 1–2 years of technical preparation plus paid shop experience; certifications can grow throughout a career.",["Diagnostics","Hands-on precision","Electronics/technology","Customer trust"]),
"Physical Therapist":("Typically 7 years after high school: undergraduate preparation plus a Doctor of Physical Therapy program and licensure.",["Anatomy/science","Patient communication","Clinical reasoning","Encouragement + persistence"]),
"Plumber":("Often about 4–5 years through apprenticeship and supervised experience; licensing rules vary by state.",["Safety + code knowledge","Measurement","Troubleshooting","Reliability"]),
"Business Administration / Manager":("Entry routes vary from direct work experience to a 2- or 4-year degree; leadership grows with results and experience.",["Communication","Organization","Data/financial literacy","Leadership"]),
"Carpenter":("Entry can begin after high school through apprenticeship or paid training; mastery grows through years of projects.",["Measurement accuracy","Tool safety","Blueprint reading","Craftsmanship"]),
"Graphic Designer":("Portfolio strength is crucial; college, certificate and self-directed routes can lead to entry-level work.",["Visual communication","Design software","Portfolio quality","Take feedback well"]),
"Neurosurgeon":("A very long medical pathway—commonly well over a decade after high school including college, medical school and residency.",["Exceptional science foundation","Precision","Stamina","Teamwork + patient care"]),
"Cybersecurity Specialist":("Entry can range from certificates and experience to a 4-year degree; hands-on labs and credentials can accelerate progress.",["Networking/IT fundamentals","Ethical problem solving","Hands-on labs","Continuous learning"]),
"Data Scientist / AI Specialist":("Often a 4-year quantitative/technical degree; some roles favor graduate study plus a strong project portfolio.",["Math + statistics","Programming","Data storytelling","Responsible AI thinking"]),
"Dental Hygienist":("Commonly about 2–3 years in an accredited dental-hygiene program followed by required licensing.",["Science + anatomy","Fine-motor precision","Patient communication","Preventive-care mindset"]),
"Doctor / Physician":("Typically 11+ years after high school including college, medical school and residency; specialty training may add more.",["Strong sciences","Patient communication","Discipline","Clinical judgment"]),
"HVAC Technician":("Often months to 2 years of technical training plus paid field experience; certifications/licensing vary by work and location.",["Mechanical troubleshooting","Electrical basics","Safety","Customer service"]),
"Lawyer / Attorney":("Typically about 7 years after high school: bachelor's degree, law school and bar/licensing requirements.",["Reading + writing","Reasoning","Research","Advocacy + ethics"]),
"Marketing / Advertising Professional":("Often a 4-year degree or portfolio-driven route; internships and measurable campaign experience help launch careers.",["Audience insight","Writing/storytelling","Analytics","Creative collaboration"]),
"Medical & Health Services Manager":("Often a 4-year degree plus healthcare experience; some leadership roles favor graduate education.",["Leadership","Healthcare systems knowledge","Budget/data skills","Communication"]),
"Nurse Practitioner":("Typically RN preparation followed by graduate APRN education, national certification and state licensure.",["Advanced clinical judgment","Patient communication","Leadership","Lifelong learning"]),
"Occupational Therapist":("Typically undergraduate preparation plus an accredited graduate OT program, fieldwork and licensure.",["Creativity in problem solving","Anatomy/science","Empathy","Clinical observation"]),
"Physician Assistant":("Typically a bachelor's/prerequisite pathway plus an accredited graduate PA program, clinical rotations and certification/licensure.",["Strong sciences","Patient communication","Team medicine","Clinical reasoning"]),
"School Counselor / Mental Health Counselor":("Usually a bachelor's followed by a relevant master's program, supervised experience and state credentialing.",["Listening","Trust + confidentiality","Crisis awareness","Communication"]),
"Web / Digital Designer":("College, certificate and self-taught routes can work; a polished portfolio of real sites/products is especially important.",["Visual design","HTML/CSS/web literacy","User-centered thinking","Portfolio + iteration"]),
"Welder / Fabricator":("Training can begin in high school or a technical program; certifications and process specialties grow with experience.",["Safety","Steady technique","Blueprint reading","Quality control"]),
"Engineer":("Often about 4 years for an engineering bachelor's; some specialties or licensed practice add exams and supervised experience.",["Math + physics","Design problem solving","Teamwork","Technical communication"]),
"Accountant / Financial Manager":("Often a 4-year degree; professional credentials and experience can open advanced accounting/finance leadership roles.",["Accuracy","Financial literacy","Ethics","Analysis + communication"]),
"Entrepreneur / Business Owner":("No single timeline: students can start building skills and small ventures now, then scale with experience and market demand.",["Solve a real problem","Know your numbers","Customer service","Adapt + persist"])
}


# The same reviewed timelines and skill summaries apply at both schools.
ROADMAP_META.update({career: tuple(GHS_DATA["meta"][career]) for career in BHS_ADDITIONAL_CAREERS})


# BHS 2026-27 career-to-school mapping. Keep this compact and update annually from the Program of Studies.
BHS_META = {'Architect': {'courses': ['Introductory Drafting & Design', 'Advanced Drafting & Design', 'Hands-On Engineering Workshop'], 'experience': 'BHS Job Shadowing; later consider the Senior Internship.', 'good': 'Advanced Drafting & Design specifically prepares students for architecture, engineering, design and drafting.', 'next': 'Ask your counselor whether Drafting & Design fits your schedule.'}, 'Electrician': {'courses': ['Introductory Power Technology', 'Advanced Power Technology', 'Residential Construction'], 'experience': 'Use BHS Job Shadowing to observe an electrician or electrical contractor.', 'good': 'BHS does not list a dedicated electrician course, so these are strong foundations—not a substitute for apprenticeship training.', 'next': 'Ask your counselor about Power Technology and a trade-focused job shadow.'}, 'Registered Nurse': {'courses': ['Anatomy & Physiology', 'Medical Terminology / UConn ECE', 'Certified Nursing Assistant (CNA) Program'], 'experience': 'Explore the BHS Health Science Program Pathway and clinical experiences; later consider a Senior Internship.', 'good': 'The Health Science Pathway is designed for students considering nursing and other healthcare careers.', 'next': 'Ask your counselor about the Health Science Program Pathway and which science course comes next for you.'}, 'Veterinarian': {'courses': ['Biology', 'Chemistry', 'Anatomy & Physiology'], 'experience': 'Use BHS Job Shadowing to explore a veterinary clinic or animal-care setting.', 'good': 'BHS has no animal-specific course listed, so strong science preparation plus real-world observation is the best school-based start.', 'next': 'Ask your counselor which science course best strengthens a future veterinary path.'}, 'Software Developer': {'courses': ['Exploration of Computer Science', 'AP Computer Science Principles', 'Robotics Foundations'], 'experience': 'Use Capstone STEM or a self-directed project to build an app, website or other software project.', 'good': 'Exploration of Computer Science includes programming, websites, apps, games and physical computing.', 'next': 'Ask your counselor whether Exploration of Computer Science fits your schedule.'}, 'Teacher': {'courses': ['Introductory Child Development', 'Advanced Child Development', 'Public Speaking'], 'experience': 'Grades 11–12 can explore the Classroom Aide option or BHS Internal Internship in Education.', 'good': 'The Classroom Aide option includes daily classroom experience, tutoring and helping a teacher.', 'next': 'Ask your counselor about Child Development now and the Classroom Aide/Internal Internship options later.'}, 'Firefighter': {'courses': ['Anatomy & Physiology', 'Dealing with Natural Disasters', 'Physical Education / Wellness'], 'experience': 'Use BHS Job Shadowing to explore fire service, EMS or emergency-response work.', 'good': 'BHS does not list a firefighter/EMT course, so science, fitness, teamwork and real-world career exploration are the strongest matches.', 'next': 'Ask your counselor about a public-safety job shadow and a science course that fits your plan.'}, 'Police Officer': {'courses': ['Criminal Justice', 'Current Issues', 'Psychology'], 'experience': 'Use BHS Job Shadowing to explore community policing, public safety or related justice careers.', 'good': 'Criminal Justice covers law enforcement, courts, constitutional issues, arrests and the justice system.', 'next': 'Ask your counselor whether Criminal Justice fits your schedule.'}, 'TV News Reporter / Local Anchor': {'courses': ['Digital Media Communication', 'Advanced Digital Media Communication', 'Public Speaking'], 'experience': 'Publications/Yearbook and BHS Job Shadowing can add reporting, editing and newsroom-style experience.', 'good': 'Advanced Digital Media builds camera, lighting, sound, broadcast and portfolio skills.', 'next': 'Ask your counselor whether Digital Media Communication fits your schedule.'}, 'Broadway Director / Actor': {'courses': ['Acting Workshop: The Art of Acting', 'Boundless Theater', 'Public Speaking'], 'experience': 'Explore Music offerings, Film as Literature, ACES Educational Center for the Arts, and performance opportunities.', 'good': 'Boundless Theater lets students research, direct, perform, design and write toward an actual performance.', 'next': 'Ask your counselor about Acting Workshop or Boundless Theater for your next schedule.'}, 'Chef / Restaurant Owner': {'courses': ['Culinary Arts', 'Advanced Culinary Arts', 'Foundations of Business'], 'experience': 'Explore Baking/Pastry, Principles of Food Preparation and later a hospitality-related internship when appropriate.', 'good': 'BHS combines hands-on culinary study with business courses that can support a future ownership goal.', 'next': 'Ask your counselor which Culinary Arts course is the best starting point for you.'}, 'Automotive Technician': {'courses': ['Introductory Power Technology', 'Advanced Power Technology', 'Automotive Mechanics Technology I & II'], 'experience': 'Use BHS Job Shadowing; later consider the Senior Internship for real workplace experience.', 'good': 'Advanced Power Technology and Automotive Mechanics may provide Gateway Community College credit opportunities.', 'next': 'Ask your counselor which automotive or Power Technology course fits your grade and schedule.'}, 'Physical Therapist': {'courses': ['Anatomy & Physiology', 'Medical Terminology / UConn ECE', 'Biology'], 'experience': 'Explore the BHS Health Science Program Pathway, clinical opportunities and a healthcare job shadow.', 'good': 'The BHS Health Science Pathway specifically identifies physical therapy among careers students can explore.', 'next': 'Ask your counselor about Anatomy & Physiology and the Health Science Program Pathway.'}, 'Plumber': {'courses': ['Residential Construction', 'Introductory Woodworking', 'Introductory Drafting & Design'], 'experience': 'Use BHS Job Shadowing to observe a plumber, plumbing contractor or construction trade professional.', 'good': 'BHS does not list a dedicated plumbing course, so construction, blueprint and measurement skills are the strongest school-based foundation.', 'next': 'Ask your counselor about Residential Construction and a plumbing-focused job shadow.'}, 'Business Administration / Manager': {'courses': ['Foundations of Business', 'AP Business with Personal Finance', 'Accounting/Computerized Accounting I'], 'experience': 'Use BHS Job Shadowing or an Internal/Senior Internship to explore management, operations or customer service.', 'good': 'BHS Business & Finance courses emphasize real-world business, decision-making, communication and entrepreneurship.', 'next': 'Ask your counselor whether Foundations of Business fits your schedule.'}, 'Carpenter': {'courses': ['Introductory Woodworking', 'Advanced Woodworking', 'Residential Construction'], 'experience': 'Use BHS Job Shadowing to explore carpentry, contracting or residential construction.', 'good': 'Residential Construction includes blueprint reading, framing, roofing, finishing, codes and career exploration.', 'next': 'Ask your counselor about Introductory Woodworking as a starting point.'}, 'Graphic Designer': {'courses': ['Graphic Design', 'Advanced Graphic Design', 'Photography'], 'experience': 'Build a portfolio through class projects, Publications/Yearbook and later AP Art & Design if appropriate.', 'good': 'Graphic Design uses Photoshop, InDesign and Illustrator; Advanced Graphic Design focuses on branding and portfolio work.', 'next': 'Ask your counselor whether Graphic Design fits your schedule.'}, 'Neurosurgeon': {'courses': ['Biology / AP-ECE Biology', 'Chemistry', 'Anatomy & Physiology'], 'experience': 'Explore the BHS Health Science Program Pathway, healthcare job shadowing and later clinical/internship opportunities.', 'good': 'BHS offers a strong health-science sequence that can begin building the science foundation for medicine.', 'next': 'Ask your counselor which advanced science course best fits your current preparation.'}, 'Cybersecurity Specialist': {'courses': ['Exploration of Computer Science', 'AP Computer Science Principles', 'Robotics Foundations'], 'experience': 'Use Capstone STEM or a supervised technology project to demonstrate problem-solving and computing skills.', 'good': 'BHS computer science courses build programming, data, algorithms, problem-solving and technology foundations useful for cybersecurity.', 'next': 'Ask your counselor whether Exploration of Computer Science or AP Computer Science Principles is right for you.'}, 'Data Scientist / AI Specialist': {'courses': ['Statistics & Probability', 'AP Computer Science Principles', 'Exploration of Computer Science'], 'experience': 'Use Capstone STEM to build a project involving data, programming or AI-related problem solving.', 'good': 'Statistics & Probability emphasizes collecting, analyzing and interpreting data for evidence-based decisions.', 'next': 'Ask your counselor about Statistics & Probability and a computer science course.'}, 'Dental Hygienist': {'courses': ['Anatomy & Physiology', 'Medical Terminology / UConn ECE', 'Certified Nursing Assistant (CNA) Program'], 'experience': 'Use the Health Science Program Pathway and healthcare job shadowing to explore patient-care settings.', 'good': 'Although BHS does not list a dental-specific course, its health-science sequence builds strong patient-care and science preparation.', 'next': 'Ask your counselor about Anatomy & Physiology and the Health Science Program Pathway.'}, 'Doctor / Physician': {'courses': ['Biology / AP-ECE Biology', 'Chemistry', 'Anatomy & Physiology'], 'experience': 'Explore the BHS Health Science Program Pathway, clinical placements and healthcare job shadowing.', 'good': 'Medical Terminology and UConn ECE health-science opportunities can add advanced preparation when prerequisites are met.', 'next': 'Ask your counselor which science sequence best supports a future medical path.'}, 'HVAC Technician': {'courses': ['Introductory Power Technology', 'Advanced Power Technology', 'Residential Construction'], 'experience': 'Use BHS Job Shadowing to observe an HVAC, refrigeration or building-systems technician.', 'good': 'BHS does not list a dedicated HVAC course; Power Technology and construction provide relevant mechanical, electrical and safety foundations.', 'next': 'Ask your counselor about Power Technology and an HVAC-focused job shadow.'}, 'Lawyer / Attorney': {'courses': ['Business Law', 'Public Speaking', 'Current Issues'], 'experience': 'Explore Model Congress at BHS, plus Job Shadowing or a later internship in law, government or public service.', 'good': 'Public Speaking includes argumentation and debate; Business Law and Current Issues strengthen legal and civic understanding.', 'next': 'Consider BHS Model Congress and ask your counselor whether Business Law or Public Speaking fits your schedule.'}, 'Marketing / Advertising Professional': {'courses': ['Foundations of Business', 'Graphic Design', 'Digital Media Communication'], 'experience': 'Use Publications/Yearbook, Entrepreneurship, AP Business with Personal Finance or a local-business job shadow to build real examples.', 'good': 'BHS offers an unusually useful mix of business, visual design and digital-media courses for marketing.', 'next': 'Ask your counselor which of Business, Graphic Design or Digital Media is the best first course for you.'}, 'Medical & Health Services Manager': {'courses': ['Foundations of Business', 'Anatomy & Physiology', 'AP Business with Personal Finance'], 'experience': 'Combine the Health Science Program Pathway with a healthcare or administration job shadow/internship.', 'good': 'This career sits at the intersection of healthcare and business, and BHS offers useful preparation in both areas.', 'next': 'Ask your counselor about pairing a business course with a health-science course.'}, 'Nurse Practitioner': {'courses': ['Anatomy & Physiology', 'Medical Terminology / UConn ECE', 'Certified Nursing Assistant (CNA) Program'], 'experience': 'Explore the BHS Health Science Program Pathway, clinical placements and later healthcare internships.', 'good': 'The CNA program can provide hands-on healthcare training and serve as a stepping stone toward nursing study.', 'next': 'Ask your counselor about the Health Science Program Pathway and the courses needed before Medical Terminology/CNA.'}, 'Occupational Therapist': {'courses': ['Anatomy & Physiology', 'Psychology', 'Medical Terminology / UConn ECE'], 'experience': 'Explore the Health Science Program Pathway and job shadowing in rehabilitation, schools or healthcare settings.', 'good': 'Anatomy plus Psychology is a particularly useful BHS combination for exploring occupational therapy.', 'next': 'Ask your counselor whether Anatomy & Physiology or Psychology fits your next schedule.'}, 'Physician Assistant': {'courses': ['Anatomy & Physiology', 'Medical Terminology / UConn ECE', 'Biology / Chemistry'], 'experience': 'Use the Health Science Program Pathway, clinical opportunities and a healthcare job shadow.', 'good': 'BHS health-science courses can build both medical vocabulary and the science foundation needed for later PA preparation.', 'next': 'Ask your counselor about Anatomy & Physiology and the Health Science Program Pathway.'}, 'School Counselor / Mental Health Counselor': {'courses': ['Psychology', 'Sociology', 'Child Development'], 'experience': 'Explore the Internal Internship in Education, Classroom Aide option, community service or a relevant job shadow.', 'good': 'BHS Psychology covers the brain, behavior, disorders and therapy; education experiences can add valuable people-centered practice.', 'next': 'Ask your counselor whether Psychology or Child Development fits your schedule.'}, 'Web / Digital Designer': {'courses': ['Web Design and Computer Applications', 'Advanced Web Design and Computer Applications', 'Graphic Design'], 'experience': 'Use Digital Media Communication, Publications/Yearbook or Capstone STEM to build a portfolio.', 'good': 'BHS Web Design includes web graphics and website creation; Advanced Web Design adds interactive site management and more complex digital work.', 'next': 'Ask your counselor whether Web Design or Graphic Design is available in your schedule year.'}, 'Welder / Fabricator': {'courses': ['Hands-On Engineering Workshop', 'Introductory Drafting & Design', 'Advanced Woodworking / shop-based technology'], 'experience': 'Use BHS Job Shadowing to explore welding, metal fabrication or manufacturing with a qualified workplace.', 'good': 'BHS does not list a dedicated welding course, so engineering, drafting, measurement and shop-safety skills are the closest school-based foundation.', 'next': 'Ask your counselor about Hands-On Engineering and a welding/fabrication job shadow.'}, 'Engineer': {'courses': ['Hands-On Engineering Workshop', 'Robotics Foundations', 'Advanced Drafting & Design'], 'experience': 'Use Capstone STEM for a substantial self-directed engineering project; later consider Job Shadowing or Senior Internship.', 'good': 'BHS offers hands-on engineering, robotics, CAD/design and advanced math/science options that fit many engineering specialties.', 'next': 'Ask your counselor which engineering, drafting or robotics course best fits your current level.'}, 'Accountant / Financial Manager': {'courses': ['Accounting/Computerized Accounting I', 'Accounting/Computerized Accounting II', 'AP Business with Personal Finance'], 'experience': 'Use a business/finance job shadow or internship to explore bookkeeping, banking, budgeting or financial operations.', 'good': 'BHS Accounting includes journals, ledgers, financial statements, payroll, inventory and financial analysis.', 'next': 'Ask your counselor whether Accounting I fits your schedule.'}, 'Entrepreneur / Business Owner': {'courses': ['Foundations of Business', 'Entrepreneurship', 'AP Business with Personal Finance'], 'experience': 'Use Job Shadowing, an internship or a small supervised project to learn how a real business operates.', 'good': 'BHS Entrepreneurship has students develop an entrepreneurial business after Foundations of Business.', 'next': 'Ask your counselor about Foundations of Business—the gateway to Entrepreneurship.'}}

# Course names, grade access and prerequisites were checked against the
# Branford High School 2026-27 Program of Studies supplied September 13, 2026.
BHS_META.update({
    "Special Education Teacher": {
        "courses": ["Child Development", "Psychology", "Sociology", "Advanced Child Development", "Public Speaking", "Classroom Aide"],
        "experience": "Explore the Internal Internship in Education (Grades 11-12), Classroom Aide, Job Shadowing, and supervised work with students. These experiences support exploration; they do not replace an approved educator-preparation program.",
        "good": "Advanced Child Development recommends Child Development. Classroom Aide and the Internal Internship have placement/approval requirements. Becoming a special education teacher normally requires an approved degree and state certification/endorsement.",
        "next": "Ask your counselor about Child Development or Psychology now and the education internship/Classroom Aide options later.",
    },
    "Military / Armed Forces": {
        "courses": ["Current Issues / Current Issues Honors", "Public Speaking", "Hands-On Engineering Workshop", "Exploration of Computer Science", "Financial Literacy", "Lifetime Fitness & Wellness"],
        "experience": "Use BHS Job Shadowing to explore a civilian field related to a military specialty, and compare official branch information carefully with family, counselors, veterans and recruiters.",
        "good": "BHS does not list JROTC or a military-preparation course. Military jobs vary widely, so the most useful school preparation depends on the specialty: technical, medical, aviation, logistics, communications and many others.",
        "next": "Choose a possible specialty first, then ask your counselor which academic, technical and fitness preparation fits it.",
    },
    "Customer Service Representative": {
        "courses": ["Foundations of Business – Research", "21st Century Communication", "Public Speaking", "Digital Media Communication", "Financial Literacy"],
        "experience": "Use Job Shadowing, an Internal Internship in Hospitality or Technology Support (Grades 11-12), volunteer work, or a part-time service role to practice communication and problem solving.",
        "good": "Customer service can be an entry-level career, but strong communication, digital skills, reliability and knowledge of the employer's field affect advancement.",
        "next": "Ask your counselor about Foundations of Business or a communication course and identify one supervised service experience.",
    },
    "Elected Official / Politician": {
        "courses": ["Current Issues / Current Issues Honors", "Public Speaking", "Business Law", "Digital Journalism", "Financial Literacy", "Psychology"],
        "experience": "Explore BHS Model Congress, attend local public meetings, volunteer on a community issue or campaign, and use Job Shadowing or a later Senior Internship in public service when available.",
        "good": "Current Issues satisfies Connecticut's civics requirement for Grade 11. Public Speaking includes argumentation and debate. Eligibility rules for elected office depend on the office and jurisdiction.",
        "next": "Ask your counselor about Model Congress and plan a course or community experience that strengthens public speaking and civic knowledge.",
    },
    "Caregiver / Personal Care Aide": {
        "courses": ["Anatomy & Physiology", "Certified Nursing Assistant (CNA) Program", "Psychology", "Child Development", "Unified PE and Health", "Medical Terminology / UConn ECE"],
        "experience": "Explore the BHS Health Science Program Pathway, CNA clinical training, Job Shadowing, community service, or a supervised placement supporting older adults or people with disabilities.",
        "good": "The CNA program is offered in Grades 11-12. Medical Terminology also begins in Grade 11 and requires successful completion of Anatomy & Physiology. Job requirements vary by care setting.",
        "next": "Ask your counselor which health-science or human-development course fits now and what preparation the CNA option requires.",
    },
    "Construction Manager": {
        "courses": ["Introductory Woodworking", "Residential Construction", "Introductory Drafting & Design", "Advanced Woodworking", "Advanced Drafting & Design", "Hands-On Engineering Workshop", "Foundations of Business – Research", "Accounting/Computerized Accounting I"],
        "experience": "Use BHS Job Shadowing to observe a contractor, superintendent or project manager; later consider a construction-focused Senior Internship.",
        "good": "Residential Construction requires a C or better in Introductory Woodworking. Advanced Drafting requires Introductory Drafting, and Accounting I starts in Grade 10. Construction management also requires scheduling, cost, safety and team-leadership skills.",
        "next": "Ask your counselor about Introductory Woodworking or Drafting and a construction-management job shadow.",
    },
    "Psychologist": {
        "courses": ["Psychology", "Statistics & Probability", "Sociology", "AP Psychology", "Child Development", "Public Speaking"],
        "experience": "Use Job Shadowing, community service, a research project, or an education/human-services internship to explore how psychologists study behavior and support people.",
        "good": "BHS Psychology is open in Grades 9-12. AP Psychology has prior-course grade recommendations. Independent clinical psychologist practice typically requires doctoral training, supervised experience and state licensure.",
        "next": "Ask your counselor about Psychology now, then build research, statistics and human-development preparation over time.",
    },
})

# Firefighter preparation is intentionally broad: science, fitness, technical
# aptitude and communication. The course order follows Connecticut's public-
# safety pathway guidance while remaining limited to courses in the BHS catalog.
BHS_META["Firefighter"] = {
    "courses": [
        "Biology",
        "Physical Education / Wellness",
        "Introductory Power Technology",
        "Chemistry",
        "Anatomy & Physiology",
        "Public Speaking",
        "Dealing with Natural Disasters",
        "Residential Construction",
    ],
    "experience": "Use BHS Job Shadowing to explore fire service, EMS or emergency-response work. Ask about approved First Aid/CPR/AED training and an age-appropriate local fire/EMS youth or cadet opportunity if one is available.",
    "good": "BHS does not list a dedicated firefighter/EMT course. Biology, health and fitness, technical courses, communication and approved real-world exploration provide useful preparation; actual department, CPAT and EMS requirements vary.",
    "next": "Ask your counselor which science, wellness and technical courses fit your grade, and whether an approved fire/EMS exploration opportunity is available.",
}

# Exact grade availability for the newly added recommendations. Courses not in
# this table continue to use the established BHS grade rules below.
BHS_COURSE_GRADES = {
    "Child Development": {9, 10, 11, 12},
    "Advanced Child Development": {9, 10, 11, 12},
    "Psychology": {9, 10, 11, 12},
    "Sociology": {9, 10, 11, 12},
    "Public Speaking": {10, 11, 12},
    "Classroom Aide": {11, 12},
    "Current Issues / Current Issues Honors": {11},
    "Hands-On Engineering Workshop": {9, 10, 11, 12},
    "Exploration of Computer Science": {9, 10, 11, 12},
    "Financial Literacy": {10, 11, 12},
    "Lifetime Fitness & Wellness": {11, 12},
    "Foundations of Business – Research": {9, 10, 11, 12},
    "21st Century Communication": {10, 11, 12},
    "Digital Media Communication": {9, 10, 11, 12},
    "Business Law": {10, 11, 12},
    "Digital Journalism": {10, 11, 12},
    "Anatomy & Physiology": {10, 11, 12},
    "Certified Nursing Assistant (CNA) Program": {11, 12},
    "Unified PE and Health": {10, 11, 12},
    "Medical Terminology / UConn ECE": {11, 12},
    "Introductory Woodworking": {9, 10, 11, 12},
    "Residential Construction": {9, 10, 11, 12},
    "Introductory Drafting & Design": {9, 10, 11, 12},
    "Advanced Woodworking": {9, 10, 11, 12},
    "Advanced Drafting & Design": {9, 10, 11, 12},
    "Accounting/Computerized Accounting I": {10, 11, 12},
    "Statistics & Probability": {10, 11, 12},
    "AP Psychology": {11, 12},
}


BHS_GRADE_LABELS = {
    "8": "8th — Preparing for High School",
    "9": "9th — Freshman",
    "10": "10th — Sophomore",
    "11": "11th — Junior",
    "12": "12th — Senior",
}

def bhs_for_grade(career, grade, path="employee"):
    """Return ranked, catalog-backed BHS recommendations for one grade/path."""
    base = dict(BHS_META.get(career, {}))
    grade = str(grade or "9")
    current_grade = int(grade)
    mapping = BHS_CAREER_COURSES.get(career, {"direct": [], "support": []})
    direct = list(mapping.get("direct", []))
    support = list(mapping.get("support", []))
    if path == "owner":
        for name in BHS_OWNERSHIP_COURSES:
            if name not in direct and name not in support:
                support.append(name)

    def available_now(name):
        return current_grade != 8 and current_grade in BHS_CATALOG[name]["grades"]

    def available_later(name):
        return any(option_grade > current_grade for option_grade in BHS_CATALOG[name]["grades"])

    direct_now = [name for name in direct if available_now(name)]
    support_now = [name for name in support if available_now(name)]
    ranked_now = direct_now + support_now
    visible = ranked_now[:3]
    supporting = ranked_now[3:]
    future = [name for name in direct + support if not available_now(name) and available_later(name)]

    def detail(name):
        data = BHS_CATALOG[name]
        grades = data["grades"]
        grade_text = str(grades[0]) if len(grades) == 1 else f"{grades[0]}–{grades[-1]}"
        return {
            "name": name,
            "grades": grade_text,
            "department": data["department"],
            "focus": data["focus"],
            "prerequisite": data.get("prerequisite", ""),
        }

    # Relevant BHS programs are grade-filtered just like courses.
    program_names = ["Job Shadowing", "Senior Internship"]
    if career in {"Registered Nurse", "Physical Therapist", "Dental Hygienist", "Doctor / Physician", "Medical & Health Services Manager", "Nurse Practitioner", "Occupational Therapist", "Physician Assistant", "Caregiver / Personal Care Aide", "Neurosurgeon"}:
        program_names.insert(1, "Health Science Program Pathway")
    if career in {"Teacher", "Special Education Teacher", "School Counselor / Mental Health Counselor"}:
        program_names[1:1] = ["Classroom Aide", "Internal Internship"]
    elif career in {"Software Developer", "Cybersecurity Specialist", "TV News Reporter / Local Anchor", "Chef / Restaurant Owner", "Business Administration / Manager", "Customer Service Representative"}:
        program_names.insert(1, "Internal Internship")
    programs = []
    for name in dict.fromkeys(program_names):
        item = BHS_PROGRAMS[name]
        state = "available now" if current_grade in item["grades"] else "plan ahead"
        if current_grade == 12 and max(item["grades"]) < 12:
            continue
        programs.append({"name": name, "grades": f"Grades {item['grades'][0]}–{item['grades'][-1]}" if len(item["grades"]) > 1 else f"Grade {item['grades'][0]}", "detail": item["detail"], "state": state})

    # Career exploration opportunities change substantially by grade at BHS.
    if grade == "8":
        experience = "Use eighth grade to explore the work, review high-school graduation requirements and plan a ninth-grade schedule with your middle- or high-school counselor. BHS Job Shadowing becomes available in grades 9–12."
        next_step = f"Ask your counselor which Grade 9 courses can help you begin exploring {career}, and which later courses require advance planning."
    elif grade == "9":
        experience = "Start with BHS Job Shadowing, which is open to grades 9–12. Use freshman year to sample the field and learn which later courses or programs you may want to build toward."
        next_step = f"Ask your counselor whether {visible[0]} is a realistic course to explore now, and identify one job-shadow possibility connected to {career}." if visible else base.get("next", "Talk with your BHS counselor about one first step this year.")
    elif grade == "10":
        experience = "Use BHS Job Shadowing now and begin building the course sequence that will open stronger junior/senior options."
        next_step = f"Ask your counselor which course should come next after your current preparation—starting with {visible[0]} if appropriate—and plan a career-focused job shadow." if visible else base.get("next", "Talk with your BHS counselor about the best next course and a job shadow.")
    elif grade == "11":
        experience = "Use BHS Job Shadowing now. Juniors may also be eligible for an Internal Internship in selected areas, and this is the right year to begin planning a Senior Internship for next year."
        next_step = f"Ask your counselor which of these courses best strengthens your senior-year plan, and begin discussing a Senior Internship or other real-world experience related to {career}."
    else:
        experience = "Prioritize real-world experience now. BHS Senior Internship is a Grade 12 opportunity, and Job Shadowing remains available to seniors."
        next_step = f"Ask your counselor which remaining course or experience has the greatest value this year, and make a concrete post-graduation plan for training, college, apprenticeship or employment in {career}."

    # Lead with the career-specific opportunity, then explain what the
    # student's present grade makes possible.
    specific_experience = base.get("experience", "").strip()
    if specific_experience:
        experience = specific_experience + " " + experience

    result = {
        "courses": visible,
        "supporting_courses": supporting,
        "future_courses": future,
        "course_details": [detail(name) for name in visible],
        "supporting_course_details": [detail(name) for name in supporting],
        "future_course_details": [detail(name) for name in future],
        "programs": programs,
        "experience": experience,
        "good": base.get("good", ""),
        "next": next_step,
        "grade_note": f"For a current {BHS_GRADE_LABELS.get(grade, grade + 'th grade')} student",
    }
    return result


def ghs_for_grade(career, grade, path="employee", priority="Doing work I enjoy"):
    """Return the same catalog-backed GHS choices shown in the main explorer."""
    grade = str(grade or "9")
    current_grade = int(grade)
    match = GHS_CAREER_MATCHES[career]
    primary = list(match["primary"])
    support = list(match["support"])
    if path == "owner":
        for course_id in ("business", "accounting", "enterprise", "bizlaw"):
            if course_id not in primary and course_id not in support:
                support.append(course_id)

    def course_state(course_id):
        grades = GHS_COURSE_CATALOG[course_id]["grades"]
        if current_grade in grades:
            return "current"
        if min(grades) > current_grade:
            return "future"
        return "past"

    primary_now = [course_id for course_id in primary if course_state(course_id) == "current"]
    support_now = [course_id for course_id in support if course_state(course_id) == "current"]
    future = [course_id for course_id in primary + support if course_state(course_id) == "future"]

    def course_detail(course_id, planned=False):
        item = GHS_COURSE_CATALOG[course_id]
        return {
            "name": item["name"],
            "why": item["why"],
            "prerequisite": item["prerequisite"],
            "grades": ", ".join(str(option) for option in item["grades"]),
            "page": item["page"],
            "planned": planned,
        }

    programs = [
        {
            "name": "Community Service for Credit — Grades 9–12",
            "detail": "An approved proposal is required before service starts. GHS lists 60 hours for 0.5 credit or 120 hours for 1.0 credit. Ask whether a project can connect to this career interest. (Catalog p. 13.)",
        },
        {
            "name": "Capstone Project / Internship — Grades 11–12",
            "detail": "With an advisor and mentor, a student may design an approved career-related internship or project. Ask about scheduling, deadlines and eligibility. (Catalog p. 13.)",
        },
        {
            "name": "Mastery Based Diploma Program — Grades 11–12",
            "detail": "Connect career exploration, an action-research project, résumé development and a mock interview to this pathway. (Catalog p. 11.)",
        },
    ]

    arts = {"Broadway Director / Actor", "Graphic Designer", "TV News Reporter / Local Anchor", "Web / Digital Designer"}
    if career in arts:
        programs.append({
            "name": "ACES Educational Center for the Arts (ECA)",
            "detail": "Explore visual arts, theatre, creative writing, music or dance where relevant. Admission uses a competitive interview or audition; discuss scheduling with a counselor. (Catalog p. 14.)",
        })

    academic = {
        "Architect", "Registered Nurse", "Veterinarian", "Software Developer", "Teacher",
        "Special Education Teacher", "Physical Therapist", "Business Administration / Manager",
        "Neurosurgeon", "Cybersecurity Specialist", "Data Scientist / AI Specialist",
        "Dental Hygienist", "Doctor / Physician", "Lawyer / Attorney",
        "Marketing / Advertising Professional", "Medical & Health Services Manager",
        "Nurse Practitioner", "Occupational Therapist", "Physician Assistant",
        "School Counselor / Mental Health Counselor", "Engineer", "Accountant / Financial Manager",
        "Construction Manager", "Psychologist",
    }
    if career in academic:
        programs.append({
            "name": "High School Partnership Programs",
            "detail": "Ask whether a relevant college course or enrichment opportunity fits your preparation. Administrative approval and each program's entry requirements apply. (Catalog p. 14.)",
        })

    all_ids = primary + support
    ib_subjects = []
    for course_id, subject in (("bio", "IB Biology"), ("chem", "IB Chemistry"), ("physics", "IB Physics"), ("theatre", "IB Theatre")):
        if course_id in all_ids:
            ib_subjects.append(subject)
    if "human" in all_ids and "ibpsych" not in all_ids:
        ib_subjects.append("IB Psychology")
    if career in {"Teacher", "Lawyer / Attorney", "TV News Reporter / Local Anchor"}:
        ib_subjects.append("IB Literature")
    if ib_subjects:
        programs.append({
            "name": "Optional IB study: " + ", ".join(dict.fromkeys(ib_subjects)),
            "detail": "GHS permits individual IB courses as well as the full diploma. Discuss readiness, scheduling and the two-year sequence with a counselor or IB coordinator. (Catalog pp. 15–16.)",
        })

    good_notes = {
        "Electrician": "Electrical knowledge, practical tool skills and understanding building plans complement one another. GHS courses are preparation; they do not replace apprenticeship training.",
        "Registered Nurse": "Anatomy and Physiology and Healthcare ECE have different entry requirements. Confirm Biology and Chemistry preparation with a counselor.",
        "Teacher": "Choose the subject and age group you may want to teach. Strengthen those subject foundations alongside communication and supervised teaching experience.",
        "Special Education Teacher": "Each peer-support option has its own entry requirements. Peer Tutor is not listed as a prerequisite for every adaptive aide course.",
        "Chef / Restaurant Owner": "GHS offers useful business and supporting-science courses but does not list a dedicated culinary program; hands-on culinary and food-safety training require a separate route.",
    }

    grade_actions = {
        "8": "Use eighth grade to review graduation requirements and plan a ninth-grade schedule. Identify one foundation course and one later option to discuss with your counselor.",
        "9": "With your counselor, choose one realistic foundation course or supervised experience to discuss now. Identify a later option and the preparation it needs.",
        "10": "With your counselor, review what you have completed. Choose a useful next course or supervised experience and plan prerequisites for junior-year options.",
        "11": "With your counselor, review your remaining schedule. Ask about a relevant course, service project or Capstone opportunity this year, if available.",
        "12": "With your counselor, review graduation requirements and useful remaining options. Focus on applications, deadlines and a realistic post-graduation plan.",
    }
    next_step = grade_actions[grade] + " " + match["launch"]
    questions = {
        "Doing work I enjoy": "Which everyday tasks in this career would you enjoy practicing?",
        "Helping people": "Who would your work help, and how?",
        "High income potential": "How would training costs, time and starting pay affect your plan?",
        "Creativity": "Where could you use creativity in the everyday work?",
        "Job stability": "What qualifications and adaptable skills could strengthen your options?",
        "Being my own boss": "What experience, customers, costs and responsibilities would ownership involve?",
    }

    return {
        "primary_course_details": [course_detail(course_id) for course_id in primary_now],
        "supporting_course_details": [course_detail(course_id) for course_id in support_now],
        "future_course_details": [course_detail(course_id, planned=True) for course_id in future],
        "programs": programs,
        "experience": match["experience"],
        "good": good_notes.get(career, "Choose courses for the skills they build, and confirm preparation, availability and prerequisites before enrolling."),
        "next": next_step,
        "reflection": questions.get(priority, "What would you like to learn about this work?"),
        "grade_note": f"For a current {BHS_GRADE_LABELS.get(grade, grade + 'th grade')} student",
    }


def rich_roadmap(career, steps):
    out=[]
    for i,(title,detail) in enumerate(steps):
        t=title.lower()
        bullets=[detail]
        if 'high school' in t:
            bullets += ["Meet with your school counselor to connect electives, graduation requirements and postsecondary options to this goal.","Look for a club, job-shadow, volunteer role, project or part-time experience that lets you test the career before graduating."]
        elif any(k in t for k in ['college','degree','program','school','education','preparation']):
            bullets += ["Compare programs for admission requirements, cost, completion time, hands-on experience and job placement—not just the school name.","Ask about scholarships, financial aid, dual-enrollment/early-college credit and other ways to reduce cost where available."]
        elif any(k in t for k in ['apprentice','training','academy']):
            bullets += ["Favor training that includes substantial hands-on practice with qualified instructors or experienced professionals.","Build a record of attendance, safety, reliability and skill growth—employers notice these habits."]
        elif any(k in t for k in ['experience','clinical','portfolio','intern']):
            bullets += ["Turn experiences into evidence: keep examples of projects, responsibilities, feedback and accomplishments for a résumé or portfolio.","Ask supervisors and mentors what separates an average beginner from someone they would enthusiastically hire again."]
        elif any(k in t for k in ['licen','certif','credential','exam','professional path']):
            bullets += ["Check the current Connecticut/state board, employer or professional-body requirements before choosing a program or paying for an exam.","Keep copies of completed hours, transcripts, certifications and renewal dates so credentials stay easy to verify."]
        elif any(k in t for k in ['business','owner','entrepreneur']):
            bullets += ["Learn estimating/pricing, budgeting, taxes, insurance, marketing and customer service in addition to the technical craft.","Gain field experience and understand the customer problem before taking on the cost and responsibility of ownership."]
        else:
            bullets += ["Target entry-level roles that provide mentoring, feedback and increasing responsibility.","Keep building skills, professional relationships and evidence of good work; use each early role as a launchpad for the next one."]
        out.append({"title":title,"bullets":bullets})
    timeline,keys=ROADMAP_META.get(career,("The timeline depends on education, training, credentials and the route you choose.",["Show up reliably","Build real skills","Ask for feedback","Keep learning"]))
    return out,timeline,keys

def load_key():
    env = os.environ.get("OPENAI_API_KEY", "").strip()
    if env:
        return env
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8")).get("openai_api_key","").strip()
        except Exception:
            pass
    # Upgrade path: if an older copy stored config.json beside app.py,
    # move that key into the safer local Windows profile location.
    if LEGACY_CONFIG_FILE.exists():
        try:
            key = json.loads(LEGACY_CONFIG_FILE.read_text(encoding="utf-8")).get("openai_api_key","").strip()
            if key:
                save_key(key)
                try:
                    LEGACY_CONFIG_FILE.unlink()
                except Exception:
                    pass
                return key
        except Exception:
            pass
    return ""

def save_key(key):
    CONFIG_FILE.write_text(json.dumps({"openai_api_key": key.strip()}, indent=2), encoding="utf-8")

def local_ip():
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80))
        ip=s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


# GHS shares the existing hosting and image service, with separate course content.
GHS_LOGIN = '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n<title>Step Into Your Future — Teacher Demo</title>\n<style>\n*{box-sizing:border-box}body{margin:0;font-family:Arial,Helvetica,sans-serif;background:linear-gradient(135deg,#eaf5fd,#f7fbff);color:#0b3558;min-height:100vh;display:grid;place-items:center;padding:24px}.card{width:min(620px,100%);background:#fff;border:1px solid #d6e6f3;border-radius:24px;box-shadow:0 18px 60px #0b355822;overflow:hidden}.head{background:linear-gradient(120deg,#073f2d,#218663);padding:34px;color:#fff}.school{font-size:13px;letter-spacing:3px;font-weight:800}.brand{font-size:38px;font-weight:900;line-height:1.05;margin-top:16px}.brand span{color:#54c6ff}.body{padding:34px}.body h2{font-size:27px;margin:0 0 10px}.body p{line-height:1.55;color:#536d83}.notice{background:#eaf6ff;border-left:5px solid #40b9f4;padding:14px 16px;border-radius:12px;margin:18px 0}label{font-weight:800;display:block;margin:22px 0 8px}input{width:100%;padding:16px;border:2px solid #cfe0ed;border-radius:12px;font-size:18px}button{margin-top:16px;width:100%;padding:16px;border:0;border-radius:12px;background:#087049;color:#fff;font-size:18px;font-weight:900;cursor:pointer}.error{background:#fff0f0;color:#a32626;padding:12px 14px;border-radius:10px;margin:14px 0}.small{font-size:12px;color:#6d7f8f;margin-top:16px}\n</style></head><body>\n<div class="card"><div class="head"><div class="school">GUILFORD HIGH SCHOOL • TEACHER PREVIEW</div><div class="brand">STEP INTO YOUR FUTURE <span>— TODAY!</span></div></div><div class="body">\n<h2>Welcome to the teacher demo.</h2><p>This preview lets educators try the career-and-course roadmap before any wider student rollout.</p>\n<div class="notice"><strong>Privacy:</strong> the no-photo roadmap is the default. Hosted portraits remain blocked until the required provider-retention and school approvals are documented.</div>\n{% if error %}<div class="error" role="alert">{{ error }}</div>{% endif %}\n<form method="post" action="/ghs/login"><input type="hidden" name="_csrf_token" value="{{ csrf_token }}"><label for="access_code">Teacher demo access code</label><input id="access_code" name="access_code" type="password" autocomplete="current-password" required><button type="submit">Enter Demo</button></form>\n<div class="small">Illustrative career visualization only — not a prediction of appearance or career outcome.<br><a href="/privacy">Privacy &amp; School Use</a></div>\n</div></div></body></html>\n'
GHS_LOGIN = GHS_LOGIN.replace(
    "Hosted portraits remain blocked until the required provider-retention and school approvals are documented.",
    "The Administrator Preview uses only fictional AI-generated sample students. Real-student portraits remain blocked until the required provider-retention and school approvals are documented.",
)
GHS_LOGIN = (GHS_LOGIN
    .replace("Step Into Your Future — Teacher Demo", "Step Into Your Future — Administrator Preview")
    .replace("GUILFORD HIGH SCHOOL • TEACHER PREVIEW", "GUILFORD HIGH SCHOOL • ADMINISTRATOR PREVIEW")
    .replace("Welcome to the teacher demo.", "Administrator Preview Access")
    .replace("This preview lets educators try the career-and-course roadmap before any wider student rollout.", "Enter the demonstration code to create fictional future-career portraits and compare their complete GHS course pathways.")
    .replace("Teacher demo access code", "Administrator Preview access code")
    .replace(">Enter Demo</button>", ">Enter Administrator Preview</button>")
    .replace('<a href="/privacy">Privacy &amp; School Use</a>', '<a href="/ghs">Return to the GHS pathway explorer</a> &nbsp;•&nbsp; <a href="/privacy">Privacy &amp; School Use</a>')
)

@app.route("/ghs")
@app.route("/ghs/")
def ghs_home():
    portrait_enabled, portrait_status = portrait_gate()
    page = (APP_DIR / "templates" / "ghs.html").read_text(encoding="utf-8")
    page = page.replace("__CSRF_TOKEN_JSON__", json.dumps(csrf_token()))
    page = page.replace("__PORTRAIT_ENABLED_JSON__", "true" if portrait_enabled else "false")
    page = page.replace("__PORTRAIT_STATUS__", str(escape(portrait_status)))
    page = page.replace("__ADMIN_PREVIEW_DISPLAY__", "inline-flex" if ADMIN_PREVIEW_ENABLED else "none")
    return make_response(page)

@app.route("/ghs/login", methods=["POST"])
def ghs_login():
    if rate_limited("ghs-login", 10, 15 * 60):
        return render_template_string(GHS_LOGIN, csrf_token=csrf_token(), error="Too many sign-in attempts. Wait 15 minutes and try again."), 429
    code = (request.form.get("access_code") or "").strip()
    if not ACCESS_CODE or secrets.compare_digest(code, ACCESS_CODE):
        session["demo_access"] = True
        session.permanent = True
        session["generation_count"] = 0
        session["admin_preview_count"] = 0
        school = session.pop("pending_admin_school", "ghs")
        return redirect(url_for("admin_preview", school=school))
    return render_template_string(GHS_LOGIN, csrf_token=csrf_token(), error="That access code is not correct."), 403

@app.route("/api/ghs/status")
def ghs_status():
    enabled, reason = portrait_gate()
    return jsonify(ok=True, ready=enabled, portrait_enabled=enabled, portrait_status=reason,
                   generations_left=max(0, MAX_GENERATIONS_PER_SESSION-int(session.get("generation_count", 0))),
                   limit=MAX_GENERATIONS_PER_SESSION)

@app.after_request
def school_readiness_headers(response):
    """Reduce browser leakage and restrict this self-contained application."""
    if (request.path.startswith("/api/") or request.path.startswith("/ghs")
            or request.path in {"/", "/login", "/logout", "/privacy"}
            or response.mimetype == "text/html"):
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["Pragma"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    response.headers["Permissions-Policy"] = "camera=(), geolocation=(), microphone=(), payment=(), usb=(), accelerometer=(), gyroscope=(), magnetometer=()"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    response.headers["Origin-Agent-Cluster"] = "?1"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'; "
        "object-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: blob:; connect-src 'self'; font-src 'self'; media-src 'none'"
    )
    if request.is_secure or os.environ.get("RENDER") or os.environ.get("HTTPS_ONLY") == "1":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

@app.route("/privacy")
def privacy_notice():
    return render_template("privacy.html", operator_name=OPERATOR_NAME,
                           privacy_contact=PRIVACY_CONTACT_EMAIL or "Not yet designated — portrait mode remains blocked")


@app.route("/demo-student/<sample_id>.png")
def demo_student_asset(sample_id):
    sample = DEMO_STUDENTS.get(sample_id)
    if not sample:
        return "Not found", 404
    return send_from_directory(app.root_path, sample["file"], mimetype="image/png")


@app.route("/admin-preview")
def admin_preview():
    school = (request.args.get("school") or "bhs").lower()
    if school not in {"bhs", "ghs"}:
        school = "bhs"
    if ACCESS_CODE and not session.get("demo_access"):
        session["pending_admin_school"] = school
        if school == "ghs":
            return render_template_string(GHS_LOGIN, csrf_token=csrf_token())
        return render_template("login.html", csrf_token=csrf_token())
    ready, status = admin_preview_gate()
    careers = GHS_CAREERS if school == "ghs" else CAREERS
    return render_template(
        "admin_preview.html",
        school=school,
        school_name="Guilford High School" if school == "ghs" else "Branford High School",
        careers=list(careers.keys()),
        samples=DEMO_STUDENTS,
        preview_ready=ready,
        preview_status=status,
        csrf_token=csrf_token(),
        generations_left=max(0, MAX_ADMIN_PREVIEW_GENERATIONS-int(session.get("admin_preview_count", 0))),
    )


@app.route("/armie")
@app.route("/armie/")
def armie_preview():
    """Army-themed career exploration using only fictional sample students."""
    if ACCESS_CODE and not session.get("demo_access"):
        session["pending_armie"] = True
        return render_template("login.html", csrf_token=csrf_token())
    ready, status = admin_preview_gate()
    return render_template(
        "admin_preview.html",
        school="army",
        school_name="Armie - Army Career Exploration",
        careers=list(ARMY_CAREERS.keys()),
        samples=DEMO_STUDENTS,
        preview_ready=ready,
        preview_status=status,
        csrf_token=csrf_token(),
        generations_left=max(0, MAX_ADMIN_PREVIEW_GENERATIONS-int(session.get("admin_preview_count", 0))),
        army_mode=True,
        army_priorities=sorted(ARMIE_PRIORITIES),
    )


@app.route("/healthz")
def healthz():
    """Minimal health check; never tests or exposes credentials."""
    return jsonify(ok=True, service="step-into-your-future", version="22")


@app.errorhandler(413)
def oversized_photo(error):
    return jsonify(ok=False, error="Photo is too large. Choose a JPEG, PNG or WebP photo smaller than 12 MB."), 413


@app.route("/")
def home():
    portrait_enabled, portrait_status = portrait_gate()
    return render_template("index.html", careers=list(CAREERS.keys()), key_ready=bool(load_key()), hosted=HOSTED,
                           csrf_token=csrf_token(), portrait_enabled=portrait_enabled, portrait_status=portrait_status,
                           admin_preview_enabled=ADMIN_PREVIEW_ENABLED,
                           generations_left=max(0, MAX_GENERATIONS_PER_SESSION-int(session.get("generation_count",0))))

@app.route("/login", methods=["POST"])
def login():
    if rate_limited("bhs-login", 10, 15 * 60):
        return render_template("login.html", csrf_token=csrf_token(), error="Too many sign-in attempts. Wait 15 minutes and try again."), 429
    if not ACCESS_CODE:
        session["demo_access"] = True
        session.permanent = True
        session["generation_count"] = 0
        session["admin_preview_count"] = 0
        if session.pop("pending_armie", False):
            return redirect(url_for("armie_preview"))
        school = session.pop("pending_admin_school", "bhs")
        return redirect(url_for("admin_preview", school=school))
    code=(request.form.get("access_code") or "").strip()
    if secrets.compare_digest(code, ACCESS_CODE):
        session["demo_access"] = True
        session.permanent = True
        session["generation_count"] = 0
        session["admin_preview_count"] = 0
        if session.pop("pending_armie", False):
            return redirect(url_for("armie_preview"))
        school = session.pop("pending_admin_school", "bhs")
        return redirect(url_for("admin_preview", school=school))
    return render_template("login.html", csrf_token=csrf_token(), error="That access code is not correct."), 403

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    response = redirect(url_for("home"))
    response.headers["Clear-Site-Data"] = '"cache", "storage"'
    return response

@app.route("/api/setup", methods=["POST"])
def setup():
    if os.environ.get("OPENAI_API_KEY") or os.environ.get("RENDER"):
        return jsonify({"ok":False,"error":"The hosted demo API key is managed securely on the server."}),403
    data=request.get_json(silent=True) or {}
    key=(data.get("api_key") or "").strip()
    if not key.startswith("sk-"):
        return jsonify({"ok":False,"error":"That does not look like an OpenAI API key."}),400
    save_key(key)
    return jsonify({"ok":True})


@app.route("/api/roadmap", methods=["POST"])
@app.route("/api/ghs/roadmap", methods=["POST"])
def roadmap_only():
    """Local course guidance: no photo, provider call, key or portrait quota needed."""
    if rate_limited("roadmap", 60, 10 * 60):
        return jsonify(ok=False, error="Too many roadmap requests from this browser. Wait a few minutes and try again."), 429
    if not request.is_json:
        return jsonify(ok=False, error="Use the roadmap form without a photo."), 400
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or set(data) - {"career", "grade", "path", "priority"}:
        return jsonify(ok=False, error="Unexpected roadmap fields. No photo is needed."), 400
    is_ghs = request.path == "/api/ghs/roadmap"
    careers = GHS_CAREERS if is_ghs else CAREERS
    career, grade = data.get("career"), data.get("grade")
    path, priority = data.get("path"), data.get("priority")
    if not all(isinstance(v, str) for v in (career, grade, path, priority)):
        return jsonify(ok=False, error="Please complete the roadmap selections."), 400
    if career not in careers or grade not in BHS_GRADE_LABELS:
        return jsonify(ok=False, error="Please select an available career and grade."), 400
    if path not in {"employee", "owner", "explore"} or priority not in {"Doing work I enjoy", "Helping people", "High income potential", "Creativity", "Job stability", "Being my own boss"}:
        return jsonify(ok=False, error="Please select an available path and priority."), 400
    info = careers[career]
    rich_steps, timeline, keys = rich_roadmap(career, info["steps"])
    if is_ghs:
        timeline, keys = GHS_DATA["meta"][career]
    school_detail = ghs_for_grade(career, grade, path, priority) if is_ghs else bhs_for_grade(career, grade, path)
    return jsonify(ok=True, image=None, age=None, career=career, grade=grade,
                   school="GHS" if is_ghs else "BHS", path=path, priority=priority,
                   summary=info["summary"], steps=info["steps"], rich_steps=rich_steps,
                   timeline=timeline, keys=keys,
                   **({"ghs": school_detail} if is_ghs else {"bhs": school_detail}))


def demo_age_direction(age):
    future_age = int(age)
    if future_age == 22:
        return "Show believable progression to approximately age 22: a young adult in the early twenties, not a teenager."
    if future_age <= 25:
        return "Show clear but subtle progression into a believable young adult around age 25, with mature facial proportions, grooming and professional presence."
    if future_age <= 28:
        return "Show noticeable progression into the late twenties, with clearly adult facial proportions, grooming, posture and professional presence."
    if future_age <= 30:
        return "Show unmistakable progression to approximately age 30 as a fully mature adult, not the source student simply placed in professional clothing."
    return "Show clearly visible, believable progression to approximately age 35 while preserving the same fictional identity; do not exaggerate aging."


@app.route("/api/admin-preview/generate", methods=["POST"])
def admin_preview_generate():
    """Live administrator demo using only bundled, synthetic source portraits."""
    if ACCESS_CODE and not session.get("demo_access"):
        return jsonify(ok=False, error="Please enter the teacher/admin access code first."), 401
    preview_ready, preview_status = admin_preview_gate()
    if not preview_ready:
        return jsonify(ok=False, error=preview_status), 403
    if rate_limited("admin-preview", 8, 10 * 60):
        return jsonify(ok=False, error="Too many preview requests from this browser. Wait 10 minutes before trying again."), 429
    count = int(session.get("admin_preview_count", 0))
    if count >= MAX_ADMIN_PREVIEW_GENERATIONS:
        return jsonify(ok=False, error=f"This Administrator Preview session is limited to {MAX_ADMIN_PREVIEW_GENERATIONS} fictional portraits to control costs."), 429

    data = request.get_json(silent=True)
    allowed = {"school", "sample_id", "career", "age", "path", "priority", "mode", "grade"}
    if not isinstance(data, dict) or set(data) - allowed:
        return jsonify(ok=False, error="Unexpected preview fields. Refresh the page and try again."), 400
    school = (data.get("school") or "").lower()
    sample_id = data.get("sample_id")
    career = data.get("career")
    age = data.get("age")
    path = data.get("path")
    priority = data.get("priority")
    mode = data.get("mode") or "standard"
    sample = DEMO_STUDENTS.get(sample_id)
    grade = data.get("grade") or (sample["grade"] if sample else "9")
    if school not in {"bhs", "ghs"} or not sample:
        return jsonify(ok=False, error="Choose one of the available fictional student previews."), 400
    career_data = ARMY_CAREERS if mode == "army" else (GHS_CAREERS if school == "ghs" else CAREERS)
    if career not in career_data:
        return jsonify(ok=False, error="Choose an available career."), 400
    if age not in {"22", "25", "28", "30", "35"}:
        return jsonify(ok=False, error="Choose one of the available future ages."), 400
    if path not in {"employee", "owner", "explore"}:
        return jsonify(ok=False, error="Choose an available career path."), 400
    allowed_priorities = ARMIE_PRIORITIES if mode == "army" else {"Doing work I enjoy", "Helping people", "High income potential", "Creativity", "Job stability", "Being my own boss"}
    if priority not in allowed_priorities:
        return jsonify(ok=False, error="Choose one of the available priorities."), 400
    if grade not in {"9", "10", "11", "12"}:
        return jsonify(ok=False, error="Choose a high-school grade from 9 through 12."), 400

    info = career_data[career]
    if mode == "army":
        business_note = {
            "employee": "Show the person serving in an enlisted career role appropriate to the selected career family.",
            "owner": "Show the person in a professional Army leadership pathway appropriate to the selected career family; do not invent rank or decorations.",
            "explore": "Show a realistic early-career Army professional in the selected career family.",
        }[path]
    else:
        business_note = "Show the person as an established professional and small-business owner." if path == "owner" else ""
    prompt = f"""
Create a realistic, respectful FUTURE-CAREER VISUALIZATION based on the entirely fictional, AI-generated student shown in the supplied reference image.

Preserve the fictional person's recognizable identity and apparent ethnicity while applying believable age progression to approximately age {age}. {demo_age_direction(age)}

IMPORTANT: This is an administrator demonstration using a synthetic person who does not exist. Do not simply copy the youthful face into adult clothing. The selected future age must be visually apparent while the result still looks like the same fictional person. The result is illustrative, not predictive.

Career: {career}
Setting: {info['scene']}
Demonstration priority: {priority}
{business_note}

Composition: polished documentary/editorial photograph, waist-up or three-quarter portrait, realistic professional environment, natural flattering lighting, age-appropriate adult appearance, and a confident but natural expression. Do not add text, captions, logos, readable badges or brand marks. The application will add its own fictional-demonstration watermark. Use realistic generic professional clothing and safety equipment where appropriate.
""".strip()

    bio = None
    try:
        bio = io.BytesIO((APP_DIR / sample["file"]).read_bytes())
        bio.name = "fictional-demo-student.png"
        client = OpenAI(api_key=load_key(), timeout=150.0, max_retries=0)
        result = client.images.edit(
            model="gpt-image-2",
            image=bio,
            prompt=prompt,
            size="1024x1536",
            quality="medium",
        )
        item = result.data[0] if result.data else None
        b64 = getattr(item, "b64_json", None)
        if not b64:
            return jsonify(ok=False, error="The image service returned no image data."), 502
        b64 = burn_portrait_watermark(b64, fictional_demo=True)
        session["admin_preview_count"] = count + 1
        rich_steps, timeline, keys = rich_roadmap(career, info["steps"])
        school_career = info.get("school_match", career)
        if mode == "army":
            timeline, keys = info["timeline"], info["keys"]
        elif school == "ghs":
            timeline, keys = GHS_DATA["meta"][career]
        return jsonify(
            ok=True,
            fictional_demo=True,
            sample_label=sample["label"],
            image="data:image/png;base64," + b64,
            career=career,
            age=age,
            grade=grade,
            school=school.upper(),
            path=path,
            priority=priority,
            mode=mode,
            summary=info["summary"],
            steps=info["steps"],
            rich_steps=rich_steps,
            timeline=timeline,
            keys=keys,
            generations_left=max(0, MAX_ADMIN_PREVIEW_GENERATIONS-count-1),
            **({"ghs": ghs_for_grade(school_career, grade, "explore", "Doing work I enjoy")} if school == "ghs" else {"bhs": bhs_for_grade(school_career, grade, "explore")}),
        )
    except Exception as error:
        category = type(error).__name__
        app.logger.warning("Administrator Preview generation failed (%s)", category)
        if category in {"AuthenticationError", "PermissionDeniedError"}:
            message = "The image service is not authorized. Check the server API key and image-model access."
        elif category == "RateLimitError":
            message = "The image service has reached a usage or billing limit. Check the API account."
        elif category in {"APITimeoutError", "APIConnectionError"}:
            message = "The image service did not finish in time. No automatic retry was sent; the submitted request may still be billed."
        else:
            message = "The fictional demonstration portrait could not be completed. Your selections remain available; please try again later."
        return jsonify(ok=False, error=message), 502
    finally:
        if bio is not None:
            bio.close()

@app.route("/api/ghs/generate", methods=["POST"])
@app.route("/api/generate", methods=["POST"])
def generate():
    if ACCESS_CODE and not session.get("demo_access"):
        return jsonify({"ok":False,"error":"Please enter the teacher demo access code first."}),401
    portrait_enabled, portrait_status = portrait_gate()
    if not portrait_enabled:
        return jsonify(ok=False, error=portrait_status), 403
    if rate_limited("portrait", 5, 10 * 60):
        return jsonify(ok=False, error="Too many portrait requests from this browser. Wait 10 minutes before trying again."), 429
    count=int(session.get("generation_count",0))
    if count >= MAX_GENERATIONS_PER_SESSION:
        return jsonify({"ok":False,"error":f"This demo is limited to {MAX_GENERATIONS_PER_SESSION} AI portraits per browser session to control costs."}),429
    key=load_key()
    if not key:
        return jsonify({"ok":False,"error":"No OpenAI API key is configured yet."}),400
    if OpenAI is None:
        return jsonify({"ok":False,"error":"The OpenAI Python package is not installed. Run START_APP.bat again."}),500

    is_ghs = request.path == "/api/ghs/generate"
    career_data = GHS_CAREERS if is_ghs else CAREERS
    photo=request.files.get("photo")
    career=(request.form.get("career") or "").strip()
    grade=(request.form.get("grade") or "9").strip()
    age=(request.form.get("age") or "25").strip()
    path=(request.form.get("path") or "employee").strip()
    priority=(request.form.get("priority") or "Doing work I enjoy").strip()
    photo_consent=(request.form.get("photo_consent") or "").strip()
    privacy_ack=(request.form.get("privacy_ack") or "").strip()
    if not photo or not career:
        return jsonify({"ok":False,"error":"Please provide a photo and choose a career."}),400
    if photo_consent != "confirmed":
        return jsonify({"ok":False,"error":"Confirm that the person pictured is age 13 or older and that you are authorized to submit the photo."}),400
    if privacy_ack != "acknowledged":
        return jsonify({"ok":False,"error":"Acknowledge the photo-processing and provider-retention notice before creating a portrait."}),400
    if career not in career_data:
        return jsonify({"ok":False,"error":"Unknown career selection."}),400
    if grade not in BHS_GRADE_LABELS:
        return jsonify({"ok":False,"error":"Please choose your current grade."}),400

    if age not in {"22", "25", "28", "30", "35"}:
        return jsonify(ok=False, error="Please select one of the available future ages."), 400
    if path not in {"employee", "owner", "explore"}:
        return jsonify(ok=False, error="Please select a valid career path."), 400
    if priority not in {"Doing work I enjoy", "Helping people", "High income potential", "Creativity", "Job stability", "Being my own boss"}:
        return jsonify(ok=False, error="Please select one of the available priorities."), 400
    raw=photo.read()
    if len(raw)>12*1024*1024:
        return jsonify({"ok":False,"error":"Photo is too large. Please use an image under 12 MB."}),400

    # Decode actual image bytes, correct phone rotation, and strip location/EXIF metadata.
    cleaned = None
    try:
        with Image.open(io.BytesIO(raw)) as source:
            if source.format not in {"JPEG", "PNG", "WEBP"}:
                raise ValueError("unsupported image")
            if source.width * source.height > 24_000_000:
                raise ValueError("too many pixels")
            source.load()
            normalized = ImageOps.exif_transpose(source).convert("RGB")
            normalized.thumbnail((2048, 2048))
            cleaned = io.BytesIO()
            normalized.save(cleaned, format="PNG", optimize=True)
            cleaned.seek(0)
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        if cleaned is not None:
            cleaned.close()
        return jsonify(ok=False, error="Choose a valid JPEG, PNG or WebP photo, up to 24 megapixels."), 400
    finally:
        # Release the original upload as soon as decoding finishes. Python and
        # provider infrastructure cannot honestly guarantee a secure memory wipe.
        raw = b""

    info=career_data[career]
    business_note = "The person should look like an established professional and small-business owner." if path=="owner" else ""

    try:
        future_age = int(age)
    except (TypeError, ValueError):
        future_age = 25

    if future_age == 22:
        age_direction = (
            "Show believable progression to approximately age 22, a young adult in the early twenties. "
            "Preserve recognizable identity, with subtle adult facial development and natural grooming. "
            "Do not age the person to 25, 30 or 35."
        )
    elif future_age <= 25:
        age_direction = (
            "Show clear but subtle progression from a high-school-age face into a believable young adult around age 25. "
            "Mature the facial proportions, jaw/cheek structure, skin texture, grooming, posture, and overall professional presence enough that the person no longer looks like a teenager."
        )
    elif future_age <= 28:
        age_direction = (
            "Show a noticeable progression into the late 20s. Preserve identity, but give the face clearly adult proportions and maturity, with natural changes in facial structure, skin texture, grooming, posture, and professional presence."
        )
    elif future_age <= 30:
        age_direction = (
            "Show unmistakable progression to approximately age 30. The subject should look like the same person as a fully mature adult, not the current student simply placed in professional clothing. "
            "Use natural adult facial structure, subtle skin and grooming changes, and a confident established-young-professional presence."
        )
    else:
        age_direction = (
            "Show clearly visible, believable progression to approximately age 35. The subject should remain unmistakably the same person, but should look meaningfully older and more mature than the original student photo. "
            "Use natural changes in facial structure, skin texture, grooming, posture, and professional presence appropriate to the mid-30s. Do not exaggerate wrinkles, gray hair, or other signs that would make the person look substantially older than 35."
        )

    prompt=f"""
Create a realistic, respectful FUTURE-CAREER VISUALIZATION based on the person in the uploaded photograph.

Preserve the person's recognizable identity, distinctive facial features, and apparent ethnicity/core identity characteristics while applying believable age progression to approximately age {age}. {age_direction}

IMPORTANT: Do not simply copy the current youthful face into adult clothing. The selected future age must be visually apparent, while the result must still clearly look like the SAME PERSON. The result is illustrative, not predictive.

Career: {career}
Setting: {info['scene']}
Student priority: {priority}
{business_note}

Composition: polished documentary/editorial photograph, waist-up or three-quarter portrait, realistic professional environment, natural flattering lighting, age-appropriate adult appearance, confident but natural expression. Preserve recognizable identity without freezing the face at its current age. Do not add text, captions, logos, badges with readable department names, or brand marks. The application will add its own standardized disclaimer after generation. Do not sexualize or glamorize the subject. If work clothing or safety equipment is appropriate, use realistic generic professional attire.
""".strip()

    bio = None
    try:
        client=OpenAI(api_key=key, timeout=150.0, max_retries=0)
        bio=cleaned
        bio.name="portrait-reference.png"

        result=client.images.edit(
            model="gpt-image-2",
            image=bio,
            prompt=prompt,
            size="1024x1536",
            quality="medium",
        )
        item=result.data[0] if result.data else None
        b64=getattr(item,"b64_json",None)
        if not b64:
            return jsonify({"ok":False,"error":"The image service returned no image data."}),502
        b64=burn_portrait_watermark(b64)

        session["generation_count"] = count + 1
        rich_steps, timeline, keys = rich_roadmap(career, info["steps"])
        if is_ghs:
            timeline, keys = GHS_DATA["meta"][career]
        return jsonify({
            "ok":True,
            "image":"data:image/png;base64,"+b64,
            "career":career,
            "age":age,
            "summary":info["summary"],
            "steps":info["steps"],
            "rich_steps":rich_steps,
            "timeline":timeline,
            "keys":keys,
            "path":path,
            "priority":priority,
            "grade":grade,
            "school":"GHS" if is_ghs else "BHS",
            "generations_left":max(0, MAX_GENERATIONS_PER_SESSION-count-1),
            **({} if is_ghs else {"bhs":bhs_for_grade(career, grade, path)})
        })
    except Exception as e:
        # Keep provider diagnostics/credentials out of student-facing responses.
        category = type(e).__name__
        app.logger.warning("Portrait generation failed (%s)", category)
        if category in {"AuthenticationError", "PermissionDeniedError"}:
            msg="The image service is not authorized. Ask the teacher to check the server's API key and model access."
        elif category == "RateLimitError":
            msg="The image service has reached a usage or billing limit. Ask the teacher to check the API account."
        elif category in {"APITimeoutError", "APIConnectionError"}:
            msg="The image service did not finish the connection in time. No automatic retry was sent; a submitted request may still be billed. Please check with the teacher before trying again."
        elif category == "BadRequestError":
            msg="The image service could not use this request. Try a clear individual portrait or ask the teacher to check the image-service settings."
        else:
            msg="The portrait could not be completed. Your selections are still here. Please ask the teacher before trying again."
        return jsonify(ok=False, error=msg), 502
    finally:
        if bio is not None:
            bio.close()

if __name__=="__main__":
    ip=local_ip()
    print("\n" + "="*68)
    print(" STEP INTO YOUR FUTURE — TODAY!  •  LIVE AI DEMO")
    print("="*68)
    print("On THIS laptop:  http://127.0.0.1:5000")
    print(f"On your PHONE (same Wi-Fi):  http://{ip}:5000")
    print("\nKeep this window open while using the app.")
    print("Press Ctrl+C to stop it.\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
