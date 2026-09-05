import os, io, base64, socket, json, traceback, secrets
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename

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

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
if os.environ.get("RENDER") or os.environ.get("HTTPS_ONLY") == "1":
    app.config["SESSION_COOKIE_SECURE"] = True

ACCESS_CODE = (os.environ.get("DEMO_ACCESS_CODE") or "").strip()
MAX_GENERATIONS_PER_SESSION = int(os.environ.get("MAX_GENERATIONS_PER_SESSION", "2"))

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

@app.route("/")
def home():
    if ACCESS_CODE and not session.get("demo_access"):
        return render_template("login.html")
    return render_template("index.html", careers=list(CAREERS.keys()), key_ready=bool(load_key()), hosted=bool(os.environ.get("OPENAI_API_KEY")), generations_left=max(0, MAX_GENERATIONS_PER_SESSION-int(session.get("generation_count",0))))

@app.route("/login", methods=["POST"])
def login():
    if not ACCESS_CODE:
        session["demo_access"] = True
        return redirect(url_for("home"))
    code=(request.form.get("access_code") or "").strip()
    if secrets.compare_digest(code, ACCESS_CODE):
        session["demo_access"] = True
        session["generation_count"] = 0
        return redirect(url_for("home"))
    return render_template("login.html", error="That access code is not correct."), 403

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/api/setup", methods=["POST"])
def setup():
    if os.environ.get("OPENAI_API_KEY"):
        return jsonify({"ok":False,"error":"The hosted demo API key is managed securely on the server."}),403
    data=request.get_json(silent=True) or {}
    key=(data.get("api_key") or "").strip()
    if not key.startswith("sk-"):
        return jsonify({"ok":False,"error":"That does not look like an OpenAI API key."}),400
    save_key(key)
    return jsonify({"ok":True})

@app.route("/api/generate", methods=["POST"])
def generate():
    if ACCESS_CODE and not session.get("demo_access"):
        return jsonify({"ok":False,"error":"Please enter the teacher demo access code first."}),401
    count=int(session.get("generation_count",0))
    if count >= MAX_GENERATIONS_PER_SESSION:
        return jsonify({"ok":False,"error":f"This demo is limited to {MAX_GENERATIONS_PER_SESSION} AI portraits per browser session to control costs."}),429
    key=load_key()
    if not key:
        return jsonify({"ok":False,"error":"No OpenAI API key is configured yet."}),400
    if OpenAI is None:
        return jsonify({"ok":False,"error":"The OpenAI Python package is not installed. Run START_APP.bat again."}),500

    photo=request.files.get("photo")
    career=(request.form.get("career") or "").strip()
    age=(request.form.get("age") or "25").strip()
    path=(request.form.get("path") or "employee").strip()
    priority=(request.form.get("priority") or "Doing work I enjoy").strip()
    if not photo or not career:
        return jsonify({"ok":False,"error":"Please provide a photo and choose a career."}),400
    if career not in CAREERS:
        return jsonify({"ok":False,"error":"Unknown career selection."}),400

    raw=photo.read()
    if len(raw)>12*1024*1024:
        return jsonify({"ok":False,"error":"Photo is too large. Please use an image under 12 MB."}),400

    info=CAREERS[career]
    business_note = "The person should look like an established professional and small-business owner." if path=="owner" else ""
    prompt=f"""
Create a realistic, respectful FUTURE-CAREER VISUALIZATION based on the person in the uploaded photograph.

Preserve the person's recognizable facial identity and core facial features. Show an imaginative approximation of the SAME PERSON at approximately age {age}. The result is illustrative, not predictive.

Career: {career}
Setting: {info['scene']}
Student priority: {priority}
{business_note}

Composition: polished documentary/editorial photograph, waist-up or three-quarter portrait, realistic professional environment, natural flattering lighting, age-appropriate adult appearance, confident but natural expression. Keep the face faithful to the source photo. Do not add text, captions, logos, badges with readable department names, watermarks, or brand marks. Do not sexualize or glamorize the subject. Do not change apparent ethnicity or other core identity characteristics. If work clothing or safety equipment is appropriate, use realistic generic professional attire.
""".strip()

    try:
        client=OpenAI(api_key=key)
        bio=io.BytesIO(raw)
        bio.name=secure_filename(photo.filename or "student.jpg") or "student.jpg"

        result=client.images.edit(
            model="gpt-image-2",
            image=bio,
            prompt=prompt,
            size="1024x1536",
            quality="medium",
        )
        item=result.data[0]
        b64=getattr(item,"b64_json",None)
        if not b64:
            return jsonify({"ok":False,"error":"The image service returned no image data."}),502

        session["generation_count"] = count + 1
        rich_steps, timeline, keys = rich_roadmap(career, info["steps"])
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
            "priority":priority
        })
    except Exception as e:
        msg=str(e)
        if "billing" in msg.lower() or "quota" in msg.lower():
            msg="The API account appears to need billing/credits or has reached a usage limit."
        elif "api key" in msg.lower() or "authentication" in msg.lower() or "401" in msg:
            msg="The API key was rejected. Please check the key in Setup."
        return jsonify({"ok":False,"error":msg[:500]}),500

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
