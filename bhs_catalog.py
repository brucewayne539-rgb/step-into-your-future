"""Normalized Branford High School 2026-27 catalog index.

Only courses and programs documented in the supplied BHS Program of Studies
are included. Career lists are ranked recommendations for counselor discussion,
not requirements or guarantees of enrollment.
"""


def course(grades, department, focus, prerequisite=""):
    return {
        "grades": list(grades),
        "department": department,
        "focus": focus,
        "prerequisite": prerequisite,
    }


COURSES = {
    # Art / visual communication
    "Graphic Design": course(range(9, 13), "Visual Arts", "Digital visual communication using design software."),
    "Advanced Graphic Design": course(range(9, 13), "Visual Arts", "Branding, advanced design work and portfolio development.", "Graphic Design"),
    "Photography": course(range(9, 13), "Visual Arts", "Composition, visual storytelling and image production."),
    "Advanced Photography & Photoshop": course(range(9, 13), "Visual Arts", "Advanced photography, editing and portfolio work.", "Photography"),
    "Drawing & Painting": course(range(9, 13), "Visual Arts", "Observation, composition, drawing and painting skills."),
    "Studio Art": course(range(9, 13), "Visual Arts", "Studio practice and portfolio-building across media."),
    "AP Art & Design": course((11, 12), "Visual Arts", "College-level sustained investigation and portfolio preparation.", "Prior art coursework and department guidance"),

    # Business / finance
    "Foundations of Business – Research": course(range(9, 13), "Business & Finance", "Business models, research, technology and communication."),
    "Accounting I": course((10, 11, 12), "Business & Finance", "Core accounting records, statements, payroll and financial procedures."),
    "Accounting II": course((11, 12), "Business & Finance", "Advanced accounting applications and financial analysis.", "Accounting I recommended"),
    "Business Law": course((10, 11, 12), "Business & Finance", "Law, contracts, consumer issues and legal reasoning."),
    "Financial Literacy": course((10, 11, 12), "Business & Finance", "Budgeting, credit, insurance, saving and financial decision-making."),
    "Entrepreneurship": course((11, 12), "Business & Finance", "Develop an entrepreneurial business using applied business and communication skills.", "Foundations of Business"),
    "AP Business with Personal Finance": course((11, 12), "Business & Finance", "College-level business, markets, entrepreneurship and personal finance.", "Strong prior Social Studies performance recommended"),

    # English / communication / performance
    "Public Speaking": course((10, 11, 12), "English", "Speaking, persuasion, argumentation and presentation confidence."),
    "21st Century Communication": course((10, 11, 12), "English", "Modern written, spoken and digital communication."),
    "Digital Journalism": course((10, 11, 12), "English", "Reporting, interviewing, writing, editing and digital publishing."),
    "Creative Writing": course((10, 11, 12), "English", "Original writing, revision, voice and storytelling."),
    "Acting Workshop: The Art of Acting": course((10, 11, 12), "English / Theater", "Acting craft, performance, interpretation and collaboration."),
    "Boundless Theater": course(range(9, 13), "English / Theater", "Research, direct, perform, design and write toward a production."),
    "Film as Literature": course((10, 11, 12), "English", "Visual storytelling, analysis and film language."),
    "Publications / Yearbook": course(range(9, 13), "English / Media", "Writing, photography, layout, deadlines and publication production."),

    # Family and consumer sciences
    "Culinary Arts": course(range(9, 13), "Family & Consumer Sciences", "Food preparation, kitchen practice, sanitation and teamwork."),
    "Advanced Culinary Arts": course(range(9, 13), "Family & Consumer Sciences", "Advanced food preparation and culinary practice.", "Culinary Arts"),
    "Introduction to Baking & Pastry": course(range(9, 13), "Family & Consumer Sciences", "Baking, pastry foundations, accuracy and food safety."),
    "Advanced Baking & Pastry": course((11, 12), "Family & Consumer Sciences", "Advanced baking and pastry production.", "Introduction to Baking & Pastry"),
    "Principles of Food Preparation I": course((10, 11, 12), "Family & Consumer Sciences", "Applied culinary and food-service preparation."),
    "Principles of Food Preparation II": course((11, 12), "Family & Consumer Sciences", "Advanced food-service preparation with possible college-credit opportunity.", "Principles of Food Preparation I"),
    "Principles of Food Preparation III": course((12,), "Family & Consumer Sciences", "Senior-level culinary and food-service preparation.", "Principles of Food Preparation II"),
    "Child Development": course(range(9, 13), "Family & Consumer Sciences", "Child growth, development, care and learning."),
    "Advanced Child Development": course(range(9, 13), "Family & Consumer Sciences", "Deeper child-development study and applied learning.", "Child Development recommended"),

    # Mathematics / computing
    "Algebra I": course(range(9, 13), "Mathematics", "Equations, functions and quantitative problem-solving."),
    "Geometry": course(range(9, 13), "Mathematics", "Measurement, spatial reasoning, proof and geometric problem-solving."),
    "Algebra II": course((10, 11, 12), "Mathematics", "Advanced algebra, functions and modeling."),
    "Precalculus": course((11, 12), "Mathematics", "Advanced functions and preparation for calculus.", "Algebra II or placement guidance"),
    "Statistics & Probability": course((10, 11, 12), "Mathematics", "Collect, analyze, interpret and communicate data."),
    "AP Statistics": course((11, 12), "Mathematics", "College-level statistical reasoning and data analysis.", "Department placement/recommendation"),
    "Exploration of Computer Science": course(range(9, 13), "Mathematics / Computer Science", "Programming, websites, apps, data, design and physical computing."),
    "AP Computer Science Principles": course((10, 11, 12), "Mathematics / Computer Science", "College-level computing, algorithms, data and societal impacts."),

    # Science / health science
    "Biology": course((9,), "Science", "Living systems, scientific investigation and foundational life science."),
    "Chemistry": course((10, 11, 12), "Science", "Matter, reactions, measurement and laboratory reasoning."),
    "Physics I": course((10, 11, 12), "Science", "Motion, forces, energy, electricity, power grids and applied physics.", "Algebra I credit; C+ in prior math recommended"),
    "Honors Physics I": course((10, 11, 12), "Science", "Rigorous algebra-based mechanics, energy and electricity.", "Algebra I credit; concurrent/completed Geometry or Algebra II recommended"),
    "AP/ECE Biology": course((11, 12), "Science", "College-level biology and laboratory study.", "AP science recommendations/placement"),
    "AP Chemistry II": course((11, 12), "Science", "College-level chemistry and laboratory study.", "Prior Chemistry and AP science recommendations"),
    "Anatomy & Physiology": course((10, 11, 12), "Science / Health Science", "Human body systems and health-science foundation."),
    "Medical Terminology / UConn ECE": course((11, 12), "Science / Health Science", "Medical language organized around human body systems.", "Successful completion of Anatomy & Physiology"),
    "Certified Nursing Assistant (CNA) Program": course((11, 12), "Science / Health Science", "Hands-on patient-care knowledge and CNA preparation through the BHS partnership program.", "Program eligibility, approvals and current requirements"),
    "Dealing with Natural Disasters": course((10, 11, 12), "Science", "Hazards, emergency events, scientific causes and community impacts."),
    "Forensic Science": course((10, 11, 12), "Science", "Scientific methods applied to evidence and investigation."),
    "Environmental Science": course((10, 11, 12), "Science", "Environmental systems, human impacts and applied investigation."),
    "Marine Biology": course((10, 11, 12), "Science", "Marine organisms, ecosystems and scientific study."),
    "ECE Careers in Allied Health": course((11, 12), "Science / Health Science", "Allied-health careers, systems and college-level exploration.", "Current program prerequisites/approval"),

    # Social studies / human behavior
    "Current Issues / Current Issues Honors": course((11,), "Social Studies", "Government, civics, world affairs and current events."),
    "Psychology": course(range(9, 13), "Social Studies", "Behavior, thought, development and mental processes."),
    "Sociology": course(range(9, 13), "Social Studies", "Groups, institutions, culture and social systems."),
    "Criminal Justice": course(range(9, 13), "Social Studies", "Law enforcement, courts, constitutional issues and justice systems."),
    "AP Psychology": course((11, 12), "Social Studies", "College-level study of behavior and mental processes.", "Strong prior Social Studies performance recommended"),
    "AP Human Geography": course((10, 11, 12), "Social Studies", "Population, culture, cities, development and geographic analysis.", "AP course recommendation/placement"),

    # Technology education
    "Introductory Woodworking": course(range(9, 13), "Technology Education", "Tool safety, measurement, materials and woodworking foundations."),
    "Advanced Woodworking": course(range(9, 13), "Technology Education", "Advanced tools, joinery, planning and project construction.", "Introductory Woodworking"),
    "Residential Construction": course(range(9, 13), "Technology Education", "Blueprints, framing, roofing, finishing, codes and construction careers.", "C or better in Introductory Woodworking"),
    "Introductory Power Technology": course(range(9, 13), "Technology Education", "Engines, power systems, hand tools, safety and mechanical foundations."),
    "Advanced Power Technology": course(range(9, 13), "Technology Education", "Power systems, electric circuits, motors, diagnostics and alternative-energy vehicles.", "Introductory Power Technology"),
    "Automotive Mechanics Technology I": course((10, 11, 12), "Technology Education", "Automotive systems, service, diagnostics and shop practice.", "Introductory Power Technology"),
    "Automotive Mechanics Technology II": course((11, 12), "Technology Education", "Advanced automotive diagnosis, systems and repair.", "Automotive Mechanics Technology I"),
    "Hands-On Engineering Workshop": course(range(9, 13), "Technology Education", "Engineering design, fabrication, measurement and iterative problem-solving."),
    "Advanced Hands-On Engineering Workshop": course(range(9, 13), "Technology Education", "Advanced engineering design and fabrication projects.", "Hands-On Engineering Workshop"),
    "Introductory Drafting & Design": course(range(9, 13), "Technology Education", "Technical drawing, CAD, measurement and design communication."),
    "Advanced Drafting & Design": course(range(9, 13), "Technology Education", "Advanced CAD/design for architecture, engineering and drafting.", "Introductory Drafting & Design"),
    "Robotics Foundations": course(range(9, 13), "Technology Education", "Robotics, systems thinking, design, building and programming."),
    "Web Design and Computer Applications": course(range(9, 13), "Technology / Visual Communication", "Web graphics, websites, blogs and digital publishing; offered in alternate years."),
    "Advanced Web Design and Computer Applications": course(range(9, 13), "Technology / Visual Communication", "Interactive websites, graphics, animation and site management; offered in alternate years.", "Web Design and Computer Applications"),
    "Digital Media Communication": course(range(9, 13), "Technology / Media", "Digital storytelling, camera, sound, editing and media production."),
    "Advanced Digital Media Communication": course(range(9, 13), "Technology / Media", "Advanced camera, lighting, sound, editing and portfolio production.", "Digital Media Communication"),
    "Capstone STEM": course((11, 12), "Technology / STEM", "Substantial self-directed STEM design, research or engineering project.", "Program approval/current requirements"),

    # Wellness / applied experiences listed as course/program options
    "Physical Education / Wellness": course(range(9, 13), "Physical Education & Health", "Fitness, health, teamwork and wellness foundations."),
    "Lifetime Fitness & Wellness": course((11, 12), "Physical Education & Health", "Lifelong fitness planning, health and personal wellness."),
    "Unified PE and Health": course((10, 11, 12), "Physical Education & Health", "Inclusive teamwork, leadership, health and physical activity.", "Teacher recommendation/current placement requirements"),
    "ECE Kinesiology": course((11, 12), "Physical Education & Health", "College-level study of movement, exercise and human performance.", "Current ECE/department requirements"),
    "Classroom Aide": course((11, 12), "Career Pathways", "Daily supervised classroom support, tutoring and educator observation.", "Schedule fit and Department Chair acceptance"),
}


PROGRAMS = {
    "Job Shadowing": {"grades": [9, 10, 11, 12], "detail": "One-day approved observation at a local business or community organization; the student secures the placement and transportation."},
    "Internal Internship": {"grades": [11, 12], "detail": "Supervised BHS experience in Technology Support, Athletics Management, Hospitality or Education; approval and portfolio requirements apply."},
    "Senior Internship": {"grades": [12], "detail": "A culminating approved workplace experience beginning in May with a minimum 140 hours and required seminar."},
    "Health Science Program Pathway": {"grades": [9, 10, 11, 12], "detail": "A planned sequence connecting core science, health-science coursework, college credit and clinical/career exploration."},
    "Classroom Aide": {"grades": [11, 12], "detail": "Supervised daily classroom experience; schedule and Department Chair approval are required."},
}


# Ranked lists. Direct courses are the clearest school-to-career matches;
# supporting courses build useful adjacent skills. Ownership courses are added
# only when the student selects the future business-owner path.
CAREER_COURSES = {
    "Architect": {"direct": ["Introductory Drafting & Design", "Advanced Drafting & Design", "Hands-On Engineering Workshop", "Geometry", "Physics I"], "support": ["Advanced Hands-On Engineering Workshop", "Drawing & Painting", "Studio Art", "AP Art & Design", "Residential Construction", "Capstone STEM"]},
    "Electrician": {"direct": ["Introductory Power Technology", "Advanced Power Technology", "Physics I"], "support": ["Hands-On Engineering Workshop", "Introductory Drafting & Design", "Introductory Woodworking", "Residential Construction", "Advanced Drafting & Design", "Algebra I", "Geometry"]},
    "Registered Nurse": {"direct": ["Biology", "Anatomy & Physiology", "Medical Terminology / UConn ECE", "Certified Nursing Assistant (CNA) Program"], "support": ["Chemistry", "Psychology", "Public Speaking", "Statistics & Probability", "ECE Careers in Allied Health"]},
    "Veterinarian": {"direct": ["Biology", "Chemistry", "Anatomy & Physiology", "AP/ECE Biology"], "support": ["Statistics & Probability", "Psychology", "Public Speaking", "Marine Biology"]},
    "Software Developer": {"direct": ["Exploration of Computer Science", "AP Computer Science Principles", "Robotics Foundations"], "support": ["Web Design and Computer Applications", "Advanced Web Design and Computer Applications", "Algebra II", "Statistics & Probability", "Capstone STEM", "21st Century Communication"]},
    "Teacher": {"direct": ["Child Development", "Advanced Child Development", "Public Speaking", "Classroom Aide"], "support": ["Psychology", "Sociology", "21st Century Communication", "Digital Media Communication"]},
    "Firefighter": {"direct": ["Biology", "Physical Education / Wellness", "Introductory Power Technology", "Chemistry", "Anatomy & Physiology"], "support": ["Public Speaking", "Dealing with Natural Disasters", "Residential Construction", "Physics I", "Psychology", "Lifetime Fitness & Wellness", "Unified PE and Health"]},
    "Police Officer": {"direct": ["Criminal Justice", "Current Issues / Current Issues Honors", "Psychology"], "support": ["Public Speaking", "Sociology", "Forensic Science", "Financial Literacy", "Lifetime Fitness & Wellness"]},
    "TV News Reporter / Local Anchor": {"direct": ["Digital Journalism", "Digital Media Communication", "Advanced Digital Media Communication", "Public Speaking"], "support": ["Publications / Yearbook", "21st Century Communication", "Photography", "Current Issues / Current Issues Honors", "Film as Literature"]},
    "Broadway Director / Actor": {"direct": ["Acting Workshop: The Art of Acting", "Boundless Theater", "Public Speaking"], "support": ["Film as Literature", "Creative Writing", "Digital Media Communication", "21st Century Communication", "Graphic Design", "Photography"]},
    "Chef / Restaurant Owner": {"direct": ["Culinary Arts", "Advanced Culinary Arts", "Principles of Food Preparation I", "Principles of Food Preparation II", "Principles of Food Preparation III"], "support": ["Introduction to Baking & Pastry", "Advanced Baking & Pastry", "Foundations of Business – Research", "Accounting I", "Financial Literacy"]},
    "Automotive Technician": {"direct": ["Introductory Power Technology", "Advanced Power Technology", "Automotive Mechanics Technology I", "Automotive Mechanics Technology II"], "support": ["Physics I", "Hands-On Engineering Workshop", "Introductory Drafting & Design", "Algebra I", "Financial Literacy"]},
    "Physical Therapist": {"direct": ["Biology", "Anatomy & Physiology", "Medical Terminology / UConn ECE", "ECE Kinesiology"], "support": ["Chemistry", "Psychology", "Statistics & Probability", "Public Speaking", "ECE Careers in Allied Health"]},
    "Plumber": {"direct": ["Residential Construction", "Introductory Woodworking", "Introductory Drafting & Design"], "support": ["Advanced Woodworking", "Advanced Drafting & Design", "Introductory Power Technology", "Physics I", "Algebra I", "Geometry"]},
    "Business Administration / Manager": {"direct": ["Foundations of Business – Research", "Accounting I", "AP Business with Personal Finance"], "support": ["Accounting II", "Business Law", "Financial Literacy", "Entrepreneurship", "Public Speaking", "Statistics & Probability", "21st Century Communication"]},
    "Carpenter": {"direct": ["Introductory Woodworking", "Advanced Woodworking", "Residential Construction"], "support": ["Introductory Drafting & Design", "Advanced Drafting & Design", "Geometry", "Hands-On Engineering Workshop", "Financial Literacy"]},
    "Graphic Designer": {"direct": ["Graphic Design", "Advanced Graphic Design", "Photography"], "support": ["Advanced Photography & Photoshop", "Drawing & Painting", "Studio Art", "AP Art & Design", "Digital Media Communication", "Web Design and Computer Applications", "Publications / Yearbook"]},
    "Neurosurgeon": {"direct": ["Biology", "Chemistry", "Anatomy & Physiology", "AP/ECE Biology", "AP Chemistry II"], "support": ["Physics I", "Psychology", "Statistics & Probability", "Medical Terminology / UConn ECE", "Public Speaking"]},
    "Cybersecurity Specialist": {"direct": ["Exploration of Computer Science", "AP Computer Science Principles", "Robotics Foundations"], "support": ["Web Design and Computer Applications", "Advanced Web Design and Computer Applications", "Algebra II", "Statistics & Probability", "Capstone STEM", "21st Century Communication"]},
    "Data Scientist / AI Specialist": {"direct": ["Statistics & Probability", "AP Statistics", "Exploration of Computer Science", "AP Computer Science Principles"], "support": ["Algebra II", "Precalculus", "Robotics Foundations", "Capstone STEM", "Public Speaking", "21st Century Communication"]},
    "Dental Hygienist": {"direct": ["Biology", "Anatomy & Physiology", "Medical Terminology / UConn ECE", "Certified Nursing Assistant (CNA) Program"], "support": ["Chemistry", "Public Speaking", "Psychology", "ECE Careers in Allied Health"]},
    "Doctor / Physician": {"direct": ["Biology", "Chemistry", "Anatomy & Physiology", "AP/ECE Biology", "AP Chemistry II"], "support": ["Physics I", "Statistics & Probability", "Medical Terminology / UConn ECE", "Psychology", "Public Speaking"]},
    "HVAC Technician": {"direct": ["Introductory Power Technology", "Advanced Power Technology", "Physics I", "Residential Construction"], "support": ["Hands-On Engineering Workshop", "Introductory Drafting & Design", "Algebra I", "Geometry", "Environmental Science", "Financial Literacy"]},
    "Lawyer / Attorney": {"direct": ["Business Law", "Public Speaking", "Current Issues / Current Issues Honors"], "support": ["Digital Journalism", "Psychology", "Sociology", "Financial Literacy", "21st Century Communication", "AP Human Geography"]},
    "Marketing / Advertising Professional": {"direct": ["Foundations of Business – Research", "Graphic Design", "Digital Media Communication"], "support": ["Advanced Graphic Design", "Advanced Digital Media Communication", "Public Speaking", "21st Century Communication", "Photography", "Publications / Yearbook", "Statistics & Probability", "AP Business with Personal Finance"]},
    "Medical & Health Services Manager": {"direct": ["Foundations of Business – Research", "Anatomy & Physiology", "AP Business with Personal Finance"], "support": ["Accounting I", "Statistics & Probability", "Medical Terminology / UConn ECE", "Public Speaking", "Business Law", "ECE Careers in Allied Health"]},
    "Nurse Practitioner": {"direct": ["Biology", "Chemistry", "Anatomy & Physiology", "Medical Terminology / UConn ECE", "Certified Nursing Assistant (CNA) Program"], "support": ["AP/ECE Biology", "Statistics & Probability", "Psychology", "Public Speaking", "ECE Careers in Allied Health"]},
    "Occupational Therapist": {"direct": ["Biology", "Anatomy & Physiology", "Psychology", "Medical Terminology / UConn ECE"], "support": ["Child Development", "Sociology", "ECE Kinesiology", "Public Speaking", "Unified PE and Health", "ECE Careers in Allied Health"]},
    "Physician Assistant": {"direct": ["Biology", "Chemistry", "Anatomy & Physiology", "Medical Terminology / UConn ECE"], "support": ["AP/ECE Biology", "Statistics & Probability", "Psychology", "Certified Nursing Assistant (CNA) Program", "ECE Careers in Allied Health"]},
    "School Counselor / Mental Health Counselor": {"direct": ["Psychology", "Sociology", "Child Development"], "support": ["Advanced Child Development", "AP Psychology", "Public Speaking", "21st Century Communication", "Statistics & Probability", "Classroom Aide"]},
    "Web / Digital Designer": {"direct": ["Web Design and Computer Applications", "Advanced Web Design and Computer Applications", "Graphic Design"], "support": ["Advanced Graphic Design", "Digital Media Communication", "Advanced Digital Media Communication", "Photography", "Exploration of Computer Science", "Publications / Yearbook", "Capstone STEM"]},
    "Welder / Fabricator": {"direct": ["Hands-On Engineering Workshop", "Advanced Hands-On Engineering Workshop", "Introductory Drafting & Design"], "support": ["Advanced Drafting & Design", "Introductory Power Technology", "Physics I", "Algebra I", "Geometry", "Introductory Woodworking"]},
    "Engineer": {"direct": ["Hands-On Engineering Workshop", "Advanced Hands-On Engineering Workshop", "Robotics Foundations", "Introductory Drafting & Design", "Advanced Drafting & Design"], "support": ["Physics I", "Honors Physics I", "Algebra II", "Precalculus", "Exploration of Computer Science", "AP Computer Science Principles", "Capstone STEM"]},
    "Accountant / Financial Manager": {"direct": ["Accounting I", "Accounting II", "AP Business with Personal Finance"], "support": ["Foundations of Business – Research", "Financial Literacy", "Statistics & Probability", "Business Law", "Public Speaking", "Entrepreneurship"]},
    "Entrepreneur / Business Owner": {"direct": ["Foundations of Business – Research", "Entrepreneurship", "AP Business with Personal Finance"], "support": ["Accounting I", "Accounting II", "Financial Literacy", "Business Law", "Public Speaking", "21st Century Communication", "Statistics & Probability"]},
    "Special Education Teacher": {"direct": ["Child Development", "Advanced Child Development", "Psychology", "Classroom Aide"], "support": ["Sociology", "Public Speaking", "21st Century Communication", "Unified PE and Health", "AP Psychology"]},
    "Military / Armed Forces": {"direct": ["Physical Education / Wellness", "Current Issues / Current Issues Honors", "Public Speaking"], "support": ["Hands-On Engineering Workshop", "Exploration of Computer Science", "Financial Literacy", "Lifetime Fitness & Wellness", "Robotics Foundations", "Anatomy & Physiology", "21st Century Communication"]},
    "Customer Service Representative": {"direct": ["21st Century Communication", "Public Speaking", "Foundations of Business – Research"], "support": ["Digital Media Communication", "Financial Literacy", "Psychology", "Business Law", "Accounting I"]},
    "Elected Official / Politician": {"direct": ["Current Issues / Current Issues Honors", "Public Speaking", "Business Law"], "support": ["Digital Journalism", "Financial Literacy", "Psychology", "Sociology", "AP Human Geography", "21st Century Communication"]},
    "Caregiver / Personal Care Aide": {"direct": ["Anatomy & Physiology", "Certified Nursing Assistant (CNA) Program", "Psychology"], "support": ["Child Development", "Advanced Child Development", "Unified PE and Health", "Medical Terminology / UConn ECE", "Public Speaking", "Sociology"]},
    "Construction Manager": {"direct": ["Residential Construction", "Introductory Drafting & Design", "Advanced Drafting & Design"], "support": ["Introductory Woodworking", "Advanced Woodworking", "Hands-On Engineering Workshop", "Foundations of Business – Research", "Accounting I", "Geometry", "Public Speaking", "Capstone STEM"]},
    "Psychologist": {"direct": ["Psychology", "AP Psychology", "Statistics & Probability"], "support": ["Sociology", "Child Development", "Advanced Child Development", "Biology", "Anatomy & Physiology", "Public Speaking", "21st Century Communication"]},
}


OWNERSHIP_COURSES = [
    "Foundations of Business – Research",
    "Accounting I",
    "Financial Literacy",
    "Entrepreneurship",
    "AP Business with Personal Finance",
    "Business Law",
]


def validate():
    missing = {
        name
        for mapping in CAREER_COURSES.values()
        for group in ("direct", "support")
        for name in mapping.get(group, [])
        if name not in COURSES
    }
    if missing:
        raise ValueError(f"Unknown BHS course(s): {sorted(missing)}")


validate()
