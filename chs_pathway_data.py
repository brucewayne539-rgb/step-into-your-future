"""Explicit career-to-course decisions from the CHS 2025–26 catalog.

These are recommended options, not complete schedules or transcript evaluations.
No keyword search or generated course list is used at request time.
Year lists describe a student starting in grade 9; entry lists adapt later starts.
"""

# Each explanation separates a catalog-taught skill from its career application.
REASONS = {
1: 'Practice reading evidence and writing clear explanations; these support accurate documentation and communication in {work}.',
6: 'Study interpersonal communication, group leadership and problem solving; apply these to communicating with people and coordinating work in {work}.',
11: 'Practice narrative structure, purposeful language and revision using feedback; apply these to storytelling and engaging audiences in {work}.',
12: 'Practice public speaking, listening and structured debate; apply these to explaining decisions and responding clearly to questions in {work}.',
13: 'Develop informational writing, source reading and media literacy through college-level writing projects; apply these to research and accurate explanations in {work}.',
10: 'Analyze film style, history and meaning through written responses and discussion; use that analysis to understand storytelling choices in {work}.',
21: 'Develop equations, functions and statistical reasoning; these are mathematical foundations for quantitative decisions in {work}.',
22: 'Study measurement, area, volume, geometric reasoning and trigonometry; apply these to spatial problems and later technical study in {work}.',
23: 'Extend your understanding of functions, algebraic expressions and statistics; use that foundation for quantitative study connected to {work}.',
24: 'Develop functions and trigonometry in preparation for calculus; these support later mathematical models used in {work}.',
29: 'Study sampling, data analysis, confidence intervals and hypothesis testing; apply these to judging evidence and uncertainty in {work}.',
30: 'Explore logic, cryptography, circuit theory and matrices; connect these foundations to algorithms and system reasoning in {work}.',
34: 'Investigate measurement, force, energy, electricity and matter through experiments; build the physical-science foundation for later study related to {work}.',
35: 'Study properties of matter and chemical reactions through laboratory work; connect chemical reasoning and careful measurement to later study in {work}.',
36: 'Study organisms, heredity, evolution and ecosystems; build the biological foundation for later scientific study related to {work}.',
37: 'Investigate forces, energy, electricity and other physical phenomena in laboratory work; use these principles to understand technical problems in {work}.',
40: 'Study organ systems, homeostasis, disorders and medical diagnosis; connect body structure and function to later professional study in {work}.',
41: 'Investigate fingerprints, DNA and trace evidence in staged crime scenes; connect laboratory observations to evidence handling and investigation in {work}.',
42: 'Design chemistry experiments, analyze data and evaluate conclusions; optional advanced laboratory preparation can support further study in {work}.',
43: 'Investigate cellular biology, genetics and physiology through advanced experiments; this is optional preparation for further life-science study in {work}.',
45: 'Study ecosystems, habitats, conservation and pollution, including watershed testing; connect environmental conditions to animal and population health in {work}.',
47: 'Explore medical terminology, vital signs, infection control and patient-care simulations; use this introduction to understand clinical work connected to {work}. It is not professional licensure or a required CNA step.',
48: 'Investigate a fictional medical case using medical history, physiology and experiments; practice weighing scientific evidence relevant to later study in {work}.',
49: 'Investigate interacting body systems and measure functions such as muscle movement and respiration; connect these observations to further study in {work}.',
50: 'Investigate disease prevention, diagnosis and treatment through fictional cases; explore infection, genetics and medical interventions relevant to later study in {work}.',
52: 'Study emergency assessment, stabilization and patient transport; explore the emergency-care side of {work}. Course participation alone does not establish permission to practice; confirm exam, age and licensing eligibility.',
53: 'Explore hygiene assistance, vital signs, mobility support and infection control through CNA training. This is optional patient-care exposure for {work}, not a required step toward RN or graduate study. The catalog announces a fall 2026 start; confirm that it is running.',
54: 'Examine modern U.S. history, civil rights and interactions between social groups; use historical context to understand public institutions in {work}.',
55: 'Examine globalization, government systems and social issues; connect this background to evaluating policies and community needs in {work}.',
56: 'Study constitutional government, civil rights and how laws are made; connect these foundations to public responsibilities in {work}.',
60: 'Study learning, development, behavior, emotion and mental processes; use this background to understand people in {work}. This introductory course does not qualify you to provide psychological treatment.',
61: 'Study social interaction, culture, groups and demographic change; connect this knowledge to understanding communities and social circumstances in {work}.',
64: 'Study the relationships among military technology, warfare and society; use this perspective to examine the responsibilities and consequences of {work}.',
66: 'Follow cases through responding agencies, investigation and court proceedings; learn how public-safety roles coordinate in work connected to {work}.',
67: 'Compare policing, courts, corrections and adult and juvenile law; use that foundation to understand legal procedures in {work}.',
68: 'Study legal ethics, civil rights and family, business and employment law; connect legal reasoning to rights and responsibilities in {work}.',
75: 'Study economic performance, the financial sector and economic policy; optional advanced economics can help you interpret the wider conditions affecting {work}.',
99: 'Develop strength, endurance and conditioning habits; the catalog explicitly connects these techniques with public-safety and military work. This is physical preparation supporting {work}, not occupational certification.',
101: 'Explore recognition, prevention and management of sports-related injuries; connect this introduction to movement and rehabilitation interests in {work}. It does not qualify you to treat patients.',
103: 'Build drawing, painting and visual-design foundations; apply visual composition to later design and communication work in {work}. This also prepares you for CHS art courses with Art I as a prerequisite.',
106: 'Develop a sustained body of artwork and explain a personal design investigation; use the resulting portfolio to demonstrate visual decisions relevant to {work}.',
107: 'Make art while supporting peers with disabilities academically and socially; explore inclusive participation and communication related to {work}. Placement depends on program needs and capacity.',
111: 'Learn camera operation and basic Photoshop through photographic assignments; apply these skills to creating usable images for {work}.',
112: 'Use typography and digital images to create visual messages such as logos, menus and advertising; apply these design skills to {work}.',
113: 'Extend graphic-design skills through posters, brochures, logos and other projects; build practical portfolio examples connected to {work}.',
114: 'Practice camera operation, composition, sound, lighting and editing; apply these production skills to visual storytelling in {work}.',
116: 'Develop vocal technique, music reading and ensemble performance through rehearsals and concerts; explore the vocal-performance side of {work}.',
117: 'Develop advanced ensemble singing, sight reading and performance technique; explore the musical-performance side of {work}. Membership is by audition and the description expects prior Concert Chorus experience.',
128: 'Help plan dance activities and choreograph pieces while supporting beginning dancers; connect supervised teaching and movement direction to {work}. Prior Dance credit and an interview are required.',
125: 'Practice improvisation, collaboration and group confidence through theatre exercises; apply these skills to responding to people and performing in {work}.',
126: 'Extend acting skills and study directing and theatre technology; connect rehearsal and production decisions directly to {work}.',
127: 'Explore dance performance and composition across several styles; develop movement and stage-expression skills connected to {work}.',
129: 'Explore programming, data, networks, web development and responsible computing; use this broad computing foundation for the digital work involved in {work}.',
130: 'Combine storytelling, artwork, programming and game analysis to build games; use the project process to explore interactive design and software behavior in {work}.',
131: 'Use isolated virtual machines to investigate threats and protect system settings, networks and files; practice defensive skills directly relevant to {work}. Work only on systems you are authorized to use.',
132: 'Install and troubleshoot computer hardware, operating systems and network components; connect these skills to diagnosing and protecting the technology used in {work}.',
133: 'Develop programming, algorithms, data analysis and software testing; apply the software-development process to practical projects related to {work}.',
134: 'Explore data transmission, cryptography and JavaScript app design; this optional AP course develops computing foundations relevant to {work}.',
135: 'Develop Java programs, object-oriented design and algorithm analysis; this optional advanced course supports more demanding software tasks in {work}.',
136: 'Evaluate and create digital information and promotional materials; connect this pathway course to audience communication and campaign work in {work}.',
137: 'Develop an independent computing project with industry input after earlier computing study; an approved capstone can demonstrate practical skills related to {work}.',
139: 'Use the engineering-design process, 3D models and an engineering notebook to develop solutions; connect design decisions and documentation to {work}.',
140: 'Program robots to move and respond to sensors; explore how control systems operate in technical work related to {work}.',
141: 'Investigate industrial robots, motors, sensors and automated material handling; connect these systems to industrial production related to {work}. This is automation preparation, not welding instruction.',
142: 'Create digital 3D models and printed prototypes; use physical models to communicate shapes and design ideas in {work}.',
143: 'Read and create perspective, assembly and detail drawings using CAD; connect technical drawings to planning and communicating work in {work}.',
144: 'Use Arduino components, digital signals, sensors and variable resistors in practical projects; build low-voltage control-system foundations related to {work}. This does not teach or authorize regulated electrical installation.',
146: 'Use digital tools for business communication, financial analysis and promotional work; connect those skills to organizing the business side of {work}.',
147: 'Study target audiences, branding, promotion and marketing ethics through sports and entertainment examples; apply those concepts to reaching audiences or customers in {work}.',
148: 'Study budgeting, credit, income and financial decisions; use this personal-finance foundation when evaluating training costs and earnings connected to {work}.',
149: 'Learn the accounting equation, debits, credits and financial statements; apply these skills to understanding costs and financial records in {work}.',
150: 'Develop a business concept and plan using case studies, sales and business strategy; explore the ownership and operating decisions associated with {work}.',
151: 'Work on real business planning and execution with CHS partners; connect practical operations and customer needs to {work}. This option requires CTE enrollment and appropriate prior preparation.',
152: 'Study educational practices, observe classrooms and design a model school; investigate how teaching environments support learning in {work}.',
153: 'Study child development, motivation, instruction and assessment, then deliver supervised mini-lessons; connect those experiences to {work}.',
154: 'Build on earlier education-pathway learning through supervised lesson planning, teaching and assessment; use mentor feedback to explore {work}. This requires prior pathway preparation.',
155: 'Support peers with disabilities academically and socially; develop respectful communication and inclusive participation skills related to {work}. Application, program capacity and supervision apply.',
156: 'Plan and deliver lessons as a supervised instructional assistant while maintaining subject knowledge; test your interest in the daily work of {work}. Application and interview are required.',
157: 'Combine photography, page design and publication teamwork to produce the yearbook; build deadline-driven communication experience related to {work}.',
}

# Four-year options plus explicit starting choices for grades 10, 11 and 12.
# Entry options avoid assuming completion of an earlier multi-year pathway.
FAMILIES = {}
def family(name, years, entries, direct, limitation=''):
    FAMILIES[name] = dict(years=dict(zip((9,10,11,12),years)), entries=dict(zip((10,11,12),entries)), direct=set(direct), limitation=limitation)

family('medicine', [[48,34,21],[35,49],[36,50],[40,43]], [[48,35,22],[36,40,47,29],[40,47,29,43]], [48,49,50,40], 'High-school health courses introduce the field; they do not provide professional medical training or replace medical-school admission requirements.')
family('nursing', [[47,34,21],[35,48],[36,49],[40,60]], [[47,35,48],[36,40,47,29],[40,47,29,53]], [47,48,49,40,53], 'CNA is optional experience, not a prerequisite for becoming an RN or nurse practitioner. Nursing education and professional licensing come after high school.')
family('dental', [[47,34,21],[35,48],[36,40],[29,43]], [[47,35,48],[36,40,47],[40,47,29]], [47,40], 'These are health-science foundations; the supplied catalog does not list a dental-hygiene clinical program.')
family('veterinary', [[48,34,21],[35,22],[36,45],[43,29]], [[35,48,22],[36,45,29],[43,45,29,42]], [36,43,45], 'CHS biomedical cases concern humans. They offer transferable science practice, not veterinary or animal-handling training; arrange animal-care exploration separately.')
family('physical', [[101,34,21],[35,47],[36,40],[29,60]], [[101,35,47],[36,40,101],[40,101,29,60]], [101,40,47], 'Sports Medicine is exploratory preparation; a physical therapist needs further professional education and licensure.')
family('occupational', [[47,107,34],[155,35],[40,60],[29,61]], [[47,155,35],[40,60,155],[40,60,155,29]], [40,47,155,107], 'Peer-support activities are supervised exploration of participation and inclusion, not occupational-therapy treatment.')
family('caregiving', [[47,107,1],[155,12],[40,60],[53,6]], [[47,155,12],[47,40,60],[53,47,40,6]], [47,107,155,40,53], 'CNA is one possible training option. Confirm the announced fall 2026 offering and the actual requirements of the care role you want; personal care and licensed nursing are different roles.')
family('cyber', [[132,129,21],[131,133],[30,23],[135,137]], [[132,133,22],[132,134,30],[131,129,30,135]], [132,131,137], 'Networking and Cyber Security has alternative entry routes, including teacher recommendation. Practice only in authorized environments; an AP course or particular certification is not required for every security job.')
family('software', [[129,130,21],[133,134],[135,30],[137,29]], [[133,130,134],[133,134,30],[133,135,29,137]], [129,130,133,134,135,137], 'Compare introductory and advanced computing choices with your actual coding experience. AP and CTE capstones are conditional options, not universal requirements.')
family('data', [[129,21,34],[133,22],[23,29],[24,135]], [[133,22,129],[133,23,29],[133,29,24,135]], [129,133,29,135], 'CHS computing and statistics provide foundations. These courses are not being represented as dedicated machine-learning or professional AI training.')
family('web', [[103,129,130],[112,133],[113,134],[137,150]], [[103,133,129],[112,133,134],[112,133,150,137]], [129,130,112,113,133,137], 'Design and coding complement one another. Advanced art and computing options require the preparation or pathway enrollment shown on their cards.')
family('graphics', [[103,129,147],[112,111],[113,157],[106,150]], [[103,129,147],[112,111,147],[112,111,147,106]], [103,112,111,113,157,106], 'Build a portfolio through the art sequence. Advanced Art Studio may accept an approved portfolio; it is not an automatic placement for a new art student.')
family('news', [[103,1,56],[114,111],[12,13],[157,68]], [[103,12,11],[114,13,12],[114,13,12,68]], [114,111,12,13,157], 'Art foundations support later video and photography. Treat reporting, verification and interviewing as skills to practice through supervised projects; a school newsroom placement is not promised.')
family('theatre', [[125,116,127],[126,11],[12,10],[117,128]], [[125,116,11],[125,116,12],[125,116,12,10]], [125,116,127,126,10,117,128], 'Theatre, voice and movement offer different ways to explore performance. Professional casting and employment remain competitive; these are not promises of Broadway work.')
family('education', [[107,1,21],[152,155],[153,60],[154,156]], [[152,155,12],[152,153,155,60],[152,153,155,156]], [107,152,153,154,155,156], 'Educational Psychology permits Next Generation Learning before or concurrently. A senior beginning the pathway should discuss these entry options rather than assume eligibility for the final Student Teaching Practicum.')
family('counseling', [[107,1,56],[152,155],[60,61],[29,6]], [[152,155,12],[60,61,155],[60,61,29,155]], [60,61,155,152], 'School counseling and clinical mental-health counseling have distinct training and credential routes. Peer support is supervised participation, not independent counseling.')
family('psychology', [[1,21,34],[35,12],[36,60],[29,61]], [[35,12,22],[36,60,29],[60,29,61,13]], [60,29,36,61], 'Introductory psychology and statistics help you explore behavior and research. They do not authorize diagnosis or treatment, and different psychology careers require different qualifications.')
family('electrical', [[34,21,139],[144,22],[23,143],[37,150]], [[144,22,139],[144,23,143],[144,143,37,150]], [144,143], 'The supplied CHS catalog does not list an electrician apprenticeship or electrical-installation course. Physics, controls and drafting are preparation; supervised trade training is a separate next step.')
family('hvac', [[34,21,139],[144,35],[23,143],[37,150]], [[144,35,139],[144,23,143],[144,143,37,150]], [144,143], 'The supplied catalog does not list dedicated HVAC installation or refrigerant training. These science, controls and drafting courses provide related foundations for later trade training.')
family('automotive', [[34,21,132],[144,22],[23,143],[37,150]], [[144,22,132],[144,23,143],[144,132,37,150]], [144,132], 'The supplied catalog does not list an automotive repair program. Computer troubleshooting and control systems offer related foundations; vehicle diagnosis and repair need separate hands-on training.')
family('plumbing', [[34,21,139],[22,143],[23,150],[37,149]], [[22,143,139],[23,143,150],[143,37,149,150]], [143,139], 'The supplied catalog does not list a plumbing installation course. Measurement, drafting and science prepare you to explore a supervised plumbing apprenticeship or other approved trade route.')
family('carpentry', [[139,21,34],[22,143],[23,150],[149,29]], [[22,143,139],[23,143,150],[143,139,149,150]], [139,143], 'The supplied catalog does not list carpentry-shop training. Design and drafting build relevant foundations, while tool use and construction skills require appropriate supervised training.')
family('welding', [[139,21,34],[143,35],[22,140],[141,150]], [[143,35,139],[143,22,140],[143,139,141,150]], [143,139,141], 'The supplied catalog does not list welding instruction. Drafting, materials science and industrial automation are related preparation; welding processes and safety require dedicated supervised training.')
family('engineering', [[139,21,34],[22,140],[23,144],[37,24]], [[139,22,140],[139,23,144],[139,144,37,24]], [139,140,144,37], 'Engineering spans several specialties. Use these design, controls and mathematics options to identify your interests; verify college mathematics preparation separately.')
family('architecture', [[139,103,21],[143,22],[23,112],[142,24]], [[143,22,103],[143,23,112],[143,142,103,24]], [139,143,142,103,112], 'CAD, visual design and mathematics are related preparation. CHS does not provide architectural licensure; college and professional requirements depend on the route you pursue.')
family('construction', [[139,21,146],[143,22],[149,23],[150,29]], [[143,22,149],[143,149,23],[143,149,150,29]], [139,143,149,150], 'This route combines technical drawings with costs and operations. It does not imply that CHS offers construction-site training or a guaranteed site placement.')
family('business', [[146,147,21],[149,150],[29,12],[151,6]], [[149,150,12],[149,150,29],[149,150,151,6]], [146,149,150,151,147], 'Management develops through experience as well as coursework. School-Based Enterprise is conditional on CTE enrollment and program placement.')
family('finance', [[146,21,129],[149,148],[29,23],[75,6]], [[149,148,22],[149,29,23],[149,29,75,6]], [149,29,146,75], 'Personal Finance concerns individual financial decisions; Accounting addresses business records. Financial-manager roles usually follow experience rather than high-school graduation.')
family('enterprise', [[146,147,129],[150,149],[12,29],[151,6]], [[150,149,147],[150,149,29],[150,149,151,12]], [146,147,150,149,151], 'Explore a small, supervised business concept before taking financial risks. A class project does not establish that a business will succeed.')
family('marketing', [[147,146,103],[112,150],[29,12],[136,151]], [[147,103,150],[147,112,29],[147,112,29,136]], [147,146,112,136,151], 'Marketing combines audience research, visual communication and business decisions. Digital Media Literacy requires the named pathway and completed program coursework.')
family('healthmanagement', [[47,146,21],[149,150],[29,60],[151,6]], [[47,149,150],[47,149,29],[47,149,29,6]], [47,146,149,151], 'Healthcare management concerns operations and services. It does not require becoming a physician, and these options do not qualify a student to manage a clinical facility immediately.')
family('service', [[146,129,125],[12,147],[60,148],[151,6]], [[12,147,148],[12,60,148],[6,12,148,151]], [146,12,6,151], 'Customer service can be explored through communication and supervised work experience. College is not a universal entry requirement.')
family('law', [[56,54,1],[66,12],[67,13],[68,61]], [[66,12,55],[66,67,13],[66,67,68,13]], [56,66,67,68,13], 'These courses develop legal understanding and argument; they are not professional legal qualifications. Compare professional routes and jurisdiction requirements after high school.')
family('policing', [[56,54,47],[66,12],[67,41],[68,60]], [[66,12,47],[66,67,41],[66,67,41,68]], [56,66,67,41,68], 'Academic law and forensic study support exploration. Police employment also has agency-specific eligibility, selection and academy requirements.')
family('fire', [[47,34,21],[66,35],[40,99],[52,60]], [[47,66,35],[47,40,99],[52,47,40,99]], [47,52,66], 'Fire departments differ in hiring and EMT requirements. CHS EMT Basic is a senior course; confirm its availability and any age, exam and licensing conditions.')
family('publicoffice', [[56,54,1],[12,55],[68,61],[29,6]], [[56,12,55],[56,68,61],[56,68,29,6]], [56,68,12,61], 'Public office involves public service and office-specific eligibility. There is no promise of election, and this is not a business-ownership pathway.')
family('military', [[64,56,132],[133,12],[99,30],[131,6]], [[64,133,12],[64,132,99],[64,131,99,6]], [64,132,133,131], 'Military specialties differ substantially. This is one technical/public-service exploration route; compare specialties, commitments and eligibility with a counselor, family and official sources before deciding.')
family('culinary', [[146,21,147],[35,149],[150,12],[151,148]], [[35,149,147],[150,149,12],[150,149,151,148]], [146,149,150,151], 'The supplied catalog does not list a culinary cooking course. CHS offers useful restaurant-business preparation; cooking, kitchen safety and food-service training need separate supervised opportunities.')

PROFILES = {}
def career(name, family_name, work, activity):
    PROFILES[name] = dict(family=family_name, work=work, activity=activity)

career('Architect','architecture','building design and architectural communication','Create a small room-layout model and explain how it serves the people who use the space; ask a design teacher for feedback.')
career('Electrician','electrical','electrical-system troubleshooting and planning','Ask a technology teacher about a supervised low-voltage circuit activity and interview an electrician about apprenticeship work; do not work on building wiring.')
career('Registered Nurse','nursing','nursing assessment, patient care and health education','Prepare questions for a nurse about assessment, patient communication and a typical shift; ask your counselor to help arrange an informational conversation.')
career('Veterinarian','veterinary','animal health and veterinary science','Ask a counselor about an age-appropriate animal-care volunteer opportunity or veterinary interview; compare animal-care work with the science behind it.')
career('Software Developer','software','software design, implementation and testing','Build a small program that solves a real classroom problem, test several inputs and explain one bug you found and fixed.')
career('Teacher','education','classroom instruction and student learning','With teacher approval, plan a short lesson, deliver it in a supervised setting and reflect on how you checked whether learners understood.')
career('Firefighter','fire','fire response, rescue and emergency patient care','Ask about a fire-station career visit or firefighter interview; compare fire suppression, prevention and emergency medical duties without participating in hazardous operations.')
career('Police Officer','policing','community policing and evidence-based investigation','Use a fictional incident to practice writing an objective account, then ask a public-safety teacher how facts, assumptions and individual rights should be handled.')
career('TV News Reporter / Local Anchor','news','news reporting, interviewing and broadcast production','Produce a short school-interest report with permission, verify each factual claim and practice a clear on-camera explanation.')
career('Broadway Director / Actor','theatre','acting, directing and stage production','Rehearse a short scene with teacher feedback, trying one version as a performer and one as a director; record what changed the audience’s understanding.')
career('Chef / Restaurant Owner','culinary','restaurant planning and food-business operations','With an adult supervising food preparation, cost a simple menu and compare ingredient costs, portion sizes and a realistic selling price.')
career('Automotive Technician','automotive','vehicle diagnostics and repair planning','Interview a technician about how a diagnostic fault is traced; ask about a supervised shop visit rather than attempting vehicle repairs without training.')
career('Physical Therapist','physical','movement assessment and rehabilitation','Ask a physical therapist about how treatment goals and progress are measured; use a supervised interview rather than diagnosing an injury or designing treatment.')
career('Plumber','plumbing','pipe-system layout and plumbing service','Sketch a fictional room’s pipe route and discuss the drawing with a technology teacher or plumber; ask how apprentices learn codes, measurements and safe installation.')
career('Business Administration / Manager','business','business operations, budgets and team coordination','Plan a small school project with a budget, assigned responsibilities and a deadline; compare the plan with the actual outcome.')
career('Carpenter','carpentry','construction layout and carpentry planning','Create a measured drawing and materials estimate for a small project; use tools only with qualified supervision and permission.')
career('Graphic Designer','graphics','visual communication and graphic design','Create two versions of a poster for the same audience and ask viewers which communicates the message more clearly and why.')
career('Neurosurgeon','medicine','the scientific study behind brain, spine and nervous-system care','Prepare a question list about neurological diagnosis, surgical teamwork and the training route, then ask your counselor about a physician interview or public medical-career event.')
career('Cybersecurity Specialist','cyber','defensive cybersecurity and secure-system administration','In a teacher-approved isolated lab, document one system-hardening change and how you checked it; never test school or public systems without explicit authorization.')
career('Data Scientist / AI Specialist','data','data analysis, statistical modeling and responsible AI','Analyze a small public dataset, explain one pattern and one limitation, and check whether your conclusion changes when unusual observations are removed.')
career('Dental Hygienist','dental','oral-health prevention and patient education','Ask a hygienist about preventive care, patient education and daily clinical work; prepare a short factual career summary from the interview.')
career('Doctor / Physician','medicine','medical diagnosis, treatment and clinical reasoning','Ask about an age-appropriate physician interview or healthcare career event; compare daily patient care with the education needed for different specialties.')
career('HVAC Technician','hvac','heating, cooling and system-control troubleshooting','Ask an HVAC technician how airflow, temperature measurements and controls help diagnose a system; explore a safe classroom model with a technology teacher.')
career('Lawyer / Attorney','law','legal research, advocacy and client communication','Use a classroom case to write arguments for two sides, identify supporting evidence and discuss the difference between persuasive claims and verified facts.')
career('Marketing / Advertising Professional','marketing','audience research and advertising campaigns','Design a small campaign for a school event, identify the intended audience and choose a measurable way to judge whether the message worked.')
career('Medical & Health Services Manager','healthmanagement','healthcare operations, service quality and budgeting','Interview a healthcare office manager about scheduling, service quality and budgets; use a fictional example rather than accessing patient records.')
career('Nurse Practitioner','nursing','advanced nursing assessment and patient care','Prepare questions for an RN or nurse practitioner about patient assessment, education and the RN-to-NP training route; ask your counselor to help arrange the conversation.')
career('Occupational Therapist','occupational','participation in everyday activities and occupational therapy','With a teacher, examine how a classroom activity could offer more ways for students to participate; discuss the idea with an OT or educator without providing therapy.')
career('Physician Assistant','medicine','medical assessment and team-based patient care','Ask a PA about clinical duties, supervised training and program admission expectations; compare this route with nursing and medical school.')
career('School Counselor / Mental Health Counselor','counseling','student support and professional counseling','Interview a school counselor about their work and how it differs from clinical mental-health counseling; do not collect classmates’ private mental-health information.')
career('Web / Digital Designer','web','website design and usable digital interfaces','Build a small website prototype, test whether someone can complete one task and improve the layout using their feedback, including keyboard access.')
career('Welder / Fabricator','welding','metal fabrication and manufacturing','Read a simple technical drawing and discuss the fabrication sequence with a teacher or tradesperson; welding equipment requires trained supervision.')
career('Engineer','engineering','engineering design and technical problem solving','Build a safe classroom prototype, measure whether it meets a design goal and record how testing led you to revise it.')
career('Accountant / Financial Manager','finance','accounting, budgets and financial analysis','Use fictional transactions to prepare a simple income statement and explain the difference between revenue, expenses and cash available.')
career('Entrepreneur / Business Owner','enterprise','business creation and day-to-day operations','Interview potential users about a small problem, draft a low-cost business concept and test interest with an adult adviser before spending money.')
career('Special Education Teacher','education','inclusive instruction and support for students with disabilities','With an educator’s supervision, adapt a short learning activity to offer different ways to participate and demonstrate understanding; respect students’ privacy.')
career('Military / Armed Forces','military','military technical service and public responsibility','Compare two specialties using official information and questions for a counselor or recruiter, including daily duties, eligibility, service commitments and civilian-transferable skills.')
career('Customer Service Representative','service','customer communication and problem resolution','Practice a fictional customer conversation: listen, restate the problem, explain available options and check whether the resolution is understood.')
career('Elected Official / Politician','publicoffice','public policy and constituent representation','Attend or watch a public local-government meeting and summarize one issue, the competing viewpoints and the evidence used in the discussion.')
career('Caregiver / Personal Care Aide','caregiving','daily-living support and respectful personal care','Ask a care professional about supporting independence, communication and personal boundaries; explore only approved, supervised activities.')
career('Construction Manager','construction','construction scheduling, estimating and coordination','Build a fictional project schedule and materials budget from a simple drawing; identify where delays or cost changes would affect other tasks.')
career('Psychologist','psychology','behavioral research and psychological science','Use published or anonymous public data to practice explaining a behavioral research finding and its limitations; do not diagnose or experiment on classmates.')

# Grade-specific course sequences that differ from the family defaults.
# These are explicit educational decisions, not inferred from career keywords.
ENTRY_FUTURES = {
 'medicine': {10:{11:[36,49,40],12:[50,43]},11:{12:[43,60]}},
 'nursing': {10:{11:[36,49],12:[40,60]},11:{12:[43,60]}},
 'dental': {10:{11:[36,40],12:[29,43]},11:{12:[29,43]}},
 'veterinary': {11:{12:[43,42]}},
 'cyber': {10:{11:[131,30],12:[135,137]},11:{12:[131,137]}},
 'software': {11:{12:[135,137]}},
 'web': {10:{11:[112,134],12:[113,137]},11:{12:[113,137]}},
 'graphics': {10:{11:[112,111],12:[113,157]},11:{12:[113,157]}},
 'news': {10:{11:[114,111],12:[157,13]},11:{12:[68,6]}},
 'theatre': {10:{11:[126,12],12:[117,10]},11:{12:[126,10]}},
}
