"""Human-authored test examples, never a runtime substitute for AI generation."""
from chs_catalog import COURSES

REASONS={
1:'Practice close reading and clear explanation, foundations for interpreting evidence and communicating decisions in this profession.',
12:'Practice explaining complex ideas and listening to questions, useful when communicating technical or clinical decisions to other people.',
21:'Build equation-solving and quantitative reasoning before advanced science or computing; discuss placement to avoid repeating completed work.',
22:'If Algebra 1 is complete, strengthen logical argument and quantitative problem solving as preparation for later mathematics.',
23:'If Algebra 1 and Geometry are complete, build functions and algebraic reasoning used in scientific and computing study.',
29:'Learn to interpret samples, data and uncertainty so that later research findings or technical evidence can be assessed critically.',
30:'If Algebra I is complete, explore logic and cryptography as foundations for understanding security algorithms and secure systems.',
34:'Build laboratory measurement and physics reasoning in the grade 9 science sequence before later chemistry and biology.',
35:'Develop laboratory and chemical reasoning that supports later understanding of living systems and medicines.',
36:'Build an understanding of cells, heredity and organisms that supports later study of disease and clinical science.',
40:'Study body systems and how they function, directly supporting later study of patient assessment and human disease.',
43:'If Biology is complete and you are ready for an optional college-level challenge, deepen cellular and physiological reasoning for health study.',
47:'Explore medical terminology, vital signs, infection control and patient communication to test your interest in clinical care.',
48:'Use medical cases and research processes to investigate whether biomedical study and clinical problem solving suit your career goal.',
49:'After the introductory biomedical course, examine interacting body systems and apply scientific reasoning to medical cases.',
50:'After the earlier biomedical courses, investigate disease prevention, diagnostics and interventions as preparation for further clinical study.',
53:'If the new CNA course is running and you meet its entry requirements, explore supervised patient-care experience; CNA is optional, not required for nursing advancement.',
129:'Explore networks, programming and responsible computing to establish a broad foundation before specialized security work.',
131:'If you meet one of the listed computing prerequisites or receive teacher recommendation, use isolated virtual machines to investigate threats and practice defensive security.',
132:'Learn how operating systems, hardware and networks work so you can later understand how to protect and troubleshoot them.',
133:'Build programming and software-testing foundations that help you understand how software behaves and where security problems can arise.',
134:'If ready for an optional AP-level challenge, study data transmission, cryptography and algorithms as foundations for defensive computing.',
135:'If Algebra 2 or AP Computer Science Principles is complete and your prior coding preparation is strong, extend your coding and algorithm-analysis skills for technical security work.',
137:'If you are enrolled in the IT CTE program and prior computing coursework prepares you for a capstone, discuss a supervised defensive-security project that demonstrates your skills.'}

MEDICAL={
8:[(48,9),(34,9),(21,9),(1,9),(35,10),(49,10),(36,11),(40,11),(50,11),(43,12)],
9:[(48,9),(34,9),(21,9),(1,9),(35,10),(49,10),(36,11),(40,11),(50,11),(43,12)],
10:[(35,10),(47,10),(48,10),(22,10),(36,11),(40,11),(49,11),(50,12),(43,12)],
11:[(36,11),(40,11),(48,11),(29,11),(49,12),(43,12)],
12:[(40,12),(47,12),(29,12),(43,12)]}
CYBER={8:[(132,9),(129,9),(21,9),(1,9),(131,10),(133,10),(23,11),(135,12),(30,11),(137,12)],9:[(132,9),(129,9),(21,9),(1,9),(131,10),(133,10),(23,11),(135,12),(30,11),(137,12)],10:[(132,10),(133,10),(23,10),(131,11),(30,11),(135,12),(137,12)],11:[(132,11),(134,11),(30,11),(12,11),(131,12),(137,12)],12:[(131,12),(129,12),(135,12),(30,12)]}

def plan(career='Neurosurgeon',grade=9):
    pairs=list(CYBER[grade] if career=='Cybersecurity Specialist' else MEDICAL[grade])
    if career=='Nurse Practitioner' and grade==12:pairs.append((53,12))
    selections=[]
    for n,y in pairs:
        c=COURSES[f'CHS-{n:03}']
        desc=c['description']
        evidence=desc[len(c['name']):].strip()[:100]
        selections.append(dict(course_id=c['id'],planned_grade=y,role='supporting' if n in [1,12] else ('direct' if n in [40,47,48,49,50,53,131,132] else 'foundation'),why=REASONS[n],evidence=evidence))
    if career=='Nurse Practitioner':
        steps=[('Nursing education','Compare nursing education routes that prepare you for RN licensure; check admission, clinical placement and cost.'),('RN preparation and experience','Complete the education and examination requirements for RN licensure and build appropriate clinical experience.'),('Graduate NP education','Complete an appropriate graduate nurse practitioner program and its supervised clinical preparation.'),('Certification and practice','Meet national certification and state advanced-practice requirements before seeking an NP role.')]
        summary='Nurse practitioners combine advanced nursing knowledge with patient assessment and communication. Start by building science foundations and exploring patient care.'
    elif career=='Cybersecurity Specialist':
        steps=[('Choose your training route','Compare computing degrees, technical training and entry-level IT routes for their practical networking and security work.'),('Build authorized experience','Use supervised labs and practical IT work to develop troubleshooting, programming and defensive-security skills.'),('Enter the field','Build a portfolio of authorized projects and consider role-relevant certifications when useful to the employers you target.')]
        summary='Cybersecurity specialists protect systems and information. Build a strong understanding of computers and networks, then practice defensive security in authorized settings.'
    else:
        steps=[('Undergraduate preparation','Build a strong university science foundation, complete medical-school admission requirements and explore supervised clinical exposure.'),('Medical school','Complete medical school leading to an MD or DO and gain supervised clinical training across medical specialties.'),('Neurosurgery residency','Complete specialized neurosurgical residency and the applicable licensing requirements before independent practice; this extends well beyond age 25 for a typical route.')]
        summary='Neurosurgeons diagnose and surgically treat conditions affecting the nervous system. Begin with careful scientific reasoning and a realistic understanding of the long medical training route.'
    return dict(career=career,grade=grade,summary=summary,selections=selections,experience=('Ask a teacher about an authorized virtual security lab where you can document how to protect a test system.' if career=='Cybersecurity Specialist' else 'Ask your counselor about an age-appropriate healthcare career conversation or supervised observation; patient access depends on the host.'),next_step='Bring these options to your counselor and compare them with courses you have already completed before choosing your next schedule.',reflection='Which part of the work would you most like to investigate through a supervised activity?',caveat='Advanced courses are conditional on your preparation. If you are entering a multi-year pathway late, discuss what can fit before graduation.',postsecondary=[dict(title=t,detail=d) for t,d in steps])


def review_result(approved=True, issues=None):
    from chs_roadmap import REVIEW_CRITERIA
    return dict(checks={key:dict(finding='Simulated review of a human-authored test plan; not live quality evidence.',passed=True) for key in REVIEW_CRITERIA},approved=approved,issues=issues or [])


def model_draft(document):
    from chs_roadmap import source_passages
    import copy
    document=copy.deepcopy(document)
    items=document.pop('selections')
    for role in ('direct','foundation','supporting'):
        document[role+'_selections']=[]
    for item in items:
        role=item.pop('role')
        item['evidence']=item['course_id']+':E1'
        document[role+'_selections'].append(item)
    return document
