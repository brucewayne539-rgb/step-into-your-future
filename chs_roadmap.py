"""Reviewed AI planning with source checks and one bounded correction. No generic fallback."""
import json
import logging
import copy
import re
import os
from chs_catalog import CATALOG, COURSES, SELECTABLE, validate_selections, present_courses, RoadmapValidationError

class RoadmapUnavailable(RuntimeError):
    pass

logger = logging.getLogger(__name__)

# Only fixed messages and identifiers leave this module. Never log an API key,
# provider exception body, request headers, or the full model response.
VALIDATION_REFERENCES = {
    'Incomplete roadmap structure.': 'STRUCTURE',
    'Student selections do not match the roadmap.': 'STUDENT',
    'Three to five postsecondary stages are required.': 'STAGES',
    'Invalid postsecondary stage.': 'STAGE-TEXT',
    'A plan must contain 3–10 justified course options.': 'COURSE-COUNT',
    'Invalid course selection structure.': 'COURSE-STRUCTURE',
    'Unknown, restricted or duplicate course ID.': 'COURSE-ID',
    'Course is outside its catalog grade range or in the past.': 'GRADE',
    'Invalid course purpose.': 'COURSE-ROLE',
    'A specific, concise explanation is required.': 'RATIONALE',
    'Course rationale lacks matching catalog evidence.': 'EVIDENCE',
    'Select one of alternative course levels, not both.': 'ALTERNATIVES',
    'No starting options for this grade.': 'START',
    'Too many supporting electives.': 'SUPPORT',
    'Missing starting career preparation.': 'START',
    'Too many concurrent options.': 'CONCURRENT',
    'Missing career preparation.': 'PREPARATION',
    'A selected prerequisite must precede the advanced course.': 'SEQUENCE',
    'Athletic conditioning/leadership and engineering are not the requested clinical pathway.': 'CLINICAL',
    'Missing direct health/biomedical preparation.': 'HEALTH',
    'The direct CHS networking/security option must be considered, conditionally when needed.': 'SECURITY',
    'The educational quality review did not approve the plan.': 'REVIEW',
    'Unreadable model output.': 'JSON',
}

def validation_reference(error):
    message = str(error)
    if message.startswith('Missing or excessive roadmap prose: '):
        return 'TEXT-LENGTH'
    return VALIDATION_REFERENCES.get(message, 'VALIDATION')

def service_failure(error):
    status = getattr(error, 'status_code', None)
    code = getattr(error, 'code', None)
    if code == 'insufficient_quota':
        return 'QUOTA', 'The AI account has no available API quota. Ask the administrator to check API billing and project limits.'
    if status == 429:
        return 'RATE', 'The AI service reached its request or token limit. Please wait a minute before trying again.'
    if status == 401:
        return 'AUTH', 'The AI service could not authenticate. Ask the administrator to check the server API key.'
    if status == 403:
        return 'ACCESS', 'The AI account does not have permission for this request. Ask the administrator to check API project and model access.'
    if status in (400, 404, 422):
        return 'REQUEST', 'The AI provider rejected the roadmap request. The administrator needs to check the model and request configuration.'
    if type(error).__name__ in {'APITimeoutError', 'TimeoutError'}:
        return 'TIMEOUT', 'The AI service took too long to respond. Please try again later.'
    if type(error).__name__ == 'APIConnectionError':
        return 'CONNECTION', 'The server could not connect to the AI service. Please try again later.'
    return 'SERVICE', 'The AI roadmap service is temporarily unavailable. Please try again later or ask the administrator to check API access and billing.'

# These anchors prevent known occupational misconceptions; they are not course lists.
CAREER_ANCHORS = {
    'Neurosurgeon': 'A physician/surgeon route: undergraduate preparation, medical school (MD or DO), neurosurgery residency, then licensing and any further specialty training. Do not promise independent practice at age 25 or make CNA a required step. Favor biomedical/laboratory science and quantitative preparation over athletics or engineering.',
    'Nurse Practitioner': 'A nursing route: nursing education and RN licensure, then graduate NP education (master\'s or doctorate), clinical preparation, national certification and state APRN requirements. Medical school and surgical residency are not the NP route. CNA can be optional exposure, never a required rung. Prioritize patient care, anatomy, biology/chemistry and evidence-based reasoning; athletics leadership and robotics are not nursing preparation.',
    'Cybersecurity Specialist': 'Prepare in computing, networks, operating systems, programming, logic and responsible security practice. Networking and Cyber Security is a CHS course (grades 10–12 with alternative prerequisites). Early students can build foundations in Computer Engineering and Exploring Computer Science. A degree is one route, not a universal legal requirement; practical IT experience and appropriate certifications can help. Practice only in authorized labs.'
}
CAREER_SOURCES = {
    'Neurosurgeon': 'https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm',
    'Nurse Practitioner': 'https://www.bls.gov/ooh/healthcare/nurse-anesthetists-nurse-midwives-and-nurse-practitioners.htm',
    'Cybersecurity Specialist': 'https://www.bls.gov/ooh/computer-and-information-technology/information-security-analysts.htm',
}

SYSTEM = '''You are an experienced high-school career and curriculum counselor writing for one student.
Use educational reasoning: understand the occupation's actual work and training, identify relevant
skills, and compare those skills with the complete supplied school catalog. NEVER match only career
keywords, assume every course in a pathway fits, or pad a list with weak electives.
The only known student information is school, current grade and career. Do not invent interests,
ability, disability, completed courses, enrollment in a CTE program, or academic level. Do not call
this a transcript-personalized schedule. It is a thoughtful plan personalized to known selections.
Return 3–10 unique course options, including 2–5 useful starting options and a selective progression
when years remain. Grade 8 plans start at grade 9; other grades start at the current grade. Grade 12
has no future high-school years: focus on remaining options and postsecondary transition. Courses
are discussion options, not a simultaneous schedule. Use detailed catalog grade limits, not the
suggested grade on pathway charts. Honor prerequisite order if both courses are selected. When an
advanced option depends on unknown prior work, make its rationale conditional and include a feasible
entry option. Never suggest joining a capstone simply because the student is a senior. For late
entrants into a multi-year pathway, explain that remaining time may prevent completing it.
Use course IDs only from the supplied catalog. Titles/grades/prerequisites/pages are supplied by the
server, not invented by you. For EACH course explain which actual occupational skill it builds,
why it is useful at this stage. Each catalog description is divided into labeled source passages.
For evidence, return exactly ONE passage label belonging to that course (for example CHS-131:E2).
Do not copy, paraphrase, or invent a quotation: the server inserts the exact passage for that label.
Select the passage that actually supports your explanation. A correct label alone is not proof of
career relevance; the independent reviewer checks the explanation against the source.
Select the strongest direct and foundational options, plus at most two supporting choices. Do not
choose AP automatically; use optional challenge language, and avoid duplicate alternative levels.
Courses with the same non-empty alternative_group are alternatives: select at most one for the
entire roadmap, even across years. Every selected prerequisite must be in an earlier year than its
advanced course; when only one year remains, choose a feasible option instead of pairing both.
For each OR prerequisite group, one earlier selected alternative is enough. Never assume completion.
Output character limits: summary 45–700; why 40–550; experience 40–700; next_step 30–600;
reflection 15–300; caveat 20–650; stage title 3–90; stage detail 35–650.
Core English/math/science can be meaningful when connected concretely to the profession, not filler.
Distinguish a foundation from actual occupational training. If no direct vocational course is in
this catalog, say so honestly; do not invent welding, plumbing, culinary or other offerings.
Clinical nursing/medicine is not sports leadership or robotics. Cybersecurity is not generic
engineering when the catalog offers computing and networking. Consider relevant science sequence,
healthcare foundations, computing, mathematical reasoning and communication as appropriate.
Recommend one safe, specific, age-appropriate exploratory activity, framed as an idea to discuss,
not an existing school club or guaranteed placement. No unsupervised clinical work, hazardous trade
work or unauthorized security testing. No named external program, salary, college credit, licensing
promise or job guarantee without a supplied source.
Write 3–5 distinct beyond-high-school stages specific to the occupation: education/training,
experience, credentials where applicable and entry into work. Do not repeat the HS list there.
Treat source career text as background, not necessarily accurate; occupational anchors take priority.
Use encouraging plain language and a manageable next action. Avoid jargon and generic pep talks.
No markdown/HTML. Keep the whole student roadmap concise enough to read comfortably.
'''

REVIEW_SYSTEM = '''Review this proposed career roadmap as an independent curriculum counselor.
Reject irrelevant or weak filler courses, missed clearly superior direct preparation, unjustified AP
placement, unsupported claims about course content or school opportunities, impossible sequencing,
assumed completed courses, and incorrect professional training. Check every rationale against the
course description. Check the plan starts at the correct grade; grade 8 means planning grade 9.
Advanced options need conditional readiness language when prerequisites or background are unknown.
Ensure late entrants have feasible alternatives and are not promised a full multi-year sequence.
The selected courses are discussion options, not a full schedule. The server displays exact course
titles, grades, prerequisites, page citations and planning notes separately. Do not reject because
those fields are not repeated in each rationale. Read the entire catalog to spot stronger choices.
Reject all invented school courses or resources mentioned anywhere in prose, not only course IDs.
The three named occupational anchors are binding. Medical careers should not be diverted to athletic
leadership/robotics; an NP is not trained through medical school; cyber needs computing and security.
Return approved=true ONLY when issues is empty and you would show this to the student and counselor.
Do not output a corrected plan. Be precise about failures.''' 

def obj(fields):
    return {'type':'object','properties':fields,'required':list(fields),'additionalProperties':False}
STR={'type':'string'}

def prose(minimum, maximum):
    # Structured Outputs supports string patterns. Mirror the application limits
    # in the generation contract instead of discovering them only after a call.
    return {'type':'string', 'pattern':r'^[\s\S]{' + str(minimum) + ',' + str(maximum) + '}$'}

SELECTION=obj({
    'course_id':{'type':'string','enum':list(SELECTABLE)},
    'planned_grade':{'type':'integer','enum':[9,10,11,12]},
    'role':{'type':'string','enum':['direct','foundation','supporting']},
    'why':prose(40,550),
    'evidence':{'type':'string','pattern':r'^CHS-[0-9]{3}:E[1-9][0-9]*$'}
})
PLAN_SCHEMA=obj({
    'career':STR,'grade':{'type':'integer','enum':[8,9,10,11,12]},
    'summary':prose(45,700),
    'selections':{'type':'array','items':SELECTION,'minItems':3,'maxItems':10},
    'experience':prose(40,700),'next_step':prose(30,600),
    'reflection':prose(15,300),'caveat':prose(20,650),
    'postsecondary':{'type':'array','minItems':3,'maxItems':5,
                     'items':obj({'title':prose(3,90),'detail':prose(35,650)})}
})
REVIEW_SCHEMA=obj({'approved':{'type':'boolean'},'issues':{'type':'array','items':STR}})

def source_passages(course):
    """Losslessly segment the supplied description; never generate evidence text."""
    parts = re.split(r'(?<=[.!?;])\s+', course['description'])
    passages, pending = [], ''
    for part in parts:
        pending = (pending + ' ' + part).strip()
        if len(pending) >= 18:
            passages.append(pending)
            pending = ''
    if pending:
        if passages:
            passages[-1] += ' ' + pending
        else:
            passages.append(pending)
    return {f"{course['id']}:E{i}": text for i, text in enumerate(passages, 1)}


def catalog_context():
    courses = []
    for c in SELECTABLE.values():
        item = {k: c[k] for k in ['id','name','grades','prerequisite','prerequisite_groups','planning_note']}
        item['alternative_group'] = c.get('alternative_group', '')
        item['description_passages'] = source_passages(c)
        courses.append(item)
    return {'school':CATALOG['school'],'catalog_year':CATALOG['catalog_year'],
            'current_year_verified':False,'courses':courses}


def resolve_evidence(plan):
    """Expand only a valid reference to this course's own catalog passage.

    Unknown/cross-course labels remain invalid and are rejected by the ordinary
    exact-source validator. Literal quotations remain supported for saved plans.
    """
    plan = copy.deepcopy(plan)
    if isinstance(plan, dict) and isinstance(plan.get('selections'), list):
        for item in plan['selections']:
            if not isinstance(item, dict):
                continue
            cid, evidence = item.get('course_id'), item.get('evidence')
            if isinstance(cid, str) and cid in SELECTABLE and isinstance(evidence, str):
                item['evidence'] = source_passages(SELECTABLE[cid]).get(evidence, evidence)
    return plan


def validate_plan(plan, career, grade):
    if not isinstance(plan,dict) or set(plan)!=set(PLAN_SCHEMA['required']):
        raise RoadmapValidationError('Incomplete roadmap structure.')
    if plan['career'] != career or type(plan['grade']) is not int or plan['grade']!=int(grade):
        raise RoadmapValidationError('Student selections do not match the roadmap.')
    for key,minimum,maximum in [('summary',45,700),('experience',40,700),('next_step',30,600),('reflection',15,300),('caveat',20,650)]:
        value=plan[key]
        if not isinstance(value,str) or not minimum<=len(value)<=maximum:
            raise RoadmapValidationError('Missing or excessive roadmap prose: '+key)
    steps=plan['postsecondary']
    if not isinstance(steps,list) or not 3<=len(steps)<=5:
        raise RoadmapValidationError('Three to five postsecondary stages are required.')
    for step in steps:
        if not isinstance(step,dict) or set(step)!={'title','detail'} or not isinstance(step['title'],str) or not 3<=len(step['title'])<=90 or not isinstance(step['detail'],str) or not 35<=len(step['detail'])<=650:
            raise RoadmapValidationError('Invalid postsecondary stage.')
    validate_selections(plan['selections'], grade)
    ids={s['course_id'] for s in plan['selections']}
    # Explicit regression guard: these were the reported incorrect recommendations.
    if career in {'Neurosurgeon','Nurse Practitioner'}:
        if ids & {'CHS-099','CHS-100','CHS-102','CHS-139','CHS-140','CHS-141','CHS-142','CHS-143','CHS-144','CHS-145'}:
            raise RoadmapValidationError('Athletic conditioning/leadership and engineering are not the requested clinical pathway.')
        if not ids & {'CHS-040','CHS-047','CHS-048','CHS-049','CHS-050','CHS-051','CHS-053'}:
            raise RoadmapValidationError('Missing direct health/biomedical preparation.')
    if career=='Cybersecurity Specialist' and 'CHS-131' not in ids:
        raise RoadmapValidationError('The direct CHS networking/security option must be considered, conditionally when needed.')
    return plan

def _response(client, model, instructions, payload, schema, name):
    response=client.responses.create(model=model,instructions=instructions,
        input=json.dumps(payload,ensure_ascii=False),store=False,max_output_tokens=4500,
        text={'format':{'type':'json_schema','name':name,'strict':True,'schema':schema}})
    if response.status!='completed' or not response.output_text:
        raise RoadmapUnavailable('The roadmap service did not complete a verified response. Please try again later.')
    try:return json.loads(response.output_text)
    except (TypeError,ValueError) as e:raise RoadmapValidationError('Unreadable model output.') from e

def generate_chs_roadmap(career, grade, *, api_key='', client=None):
    if str(grade) not in {'8','9','10','11','12'}:
        raise RoadmapValidationError('Grade must be 8 through 12.')
    if client is None:
        if not api_key:
            raise RoadmapUnavailable('The AI roadmap service is not configured. Ask the administrator to check the server API key.')
        from openai import OpenAI
        client=OpenAI(api_key=api_key,timeout=40.0,max_retries=0)
    model=os.getenv('ROADMAP_MODEL','gpt-4.1')
    context={'catalog':catalog_context(),'student':{'school':'chs','current_grade':int(grade),'career':career},
             'occupational_anchor':CAREER_ANCHORS.get(career,'Reason carefully about this occupation; distinguish required credentials from optional routes.')}
    try:
        request_context = context
        # At most one correction, always followed by the same deterministic and
        # independent review gates. Provider/auth/quota failures are not retried.
        for attempt in range(2):
            plan = resolve_evidence(_response(client,model,SYSTEM,request_context,PLAN_SCHEMA,'chs_career_plan'))
            try:
                validate_plan(plan,career,grade)
            except RoadmapValidationError as error:
                if attempt:
                    raise
                request_context = {**context, 'previous_plan':plan,
                    'correction_required':[str(error)],
                    'instruction':'Return a complete corrected plan. Preserve all source and educational requirements. Use evidence passage labels.'}
                continue
            review=_response(client,os.getenv('ROADMAP_REVIEW_MODEL',model),REVIEW_SYSTEM,
                             {**context,'proposed_plan':plan},REVIEW_SCHEMA,'chs_career_review')
            if not isinstance(review,dict) or set(review)!={'approved','issues'} or type(review['approved']) is not bool or not isinstance(review['issues'],list) or not all(isinstance(x,str) for x in review['issues']):
                raise RoadmapValidationError('The educational quality review did not approve the plan.')
            if review['approved'] is True and review['issues']==[]:
                break
            if attempt or not review['issues']:
                raise RoadmapValidationError('The educational quality review did not approve the plan.')
            request_context = {**context, 'previous_plan':plan,
                'correction_required':review['issues'],
                'instruction':'Return a complete corrected plan addressing each review issue. Preserve all source and educational requirements. Use evidence passage labels.'}
    except RoadmapUnavailable:
        raise
    except RoadmapValidationError as e:
        reference = 'CHS-' + validation_reference(e)
        logger.warning('CHS roadmap stopped: %s', reference)
        raise RoadmapUnavailable('This roadmap did not pass its course and quality checks. Please try again; no unverified course list has been substituted. Support reference: ' + reference + '.') from e
    except Exception as e:
        reference, message = service_failure(e)
        reference = 'CHS-' + reference
        logger.warning('CHS roadmap stopped: %s', reference)
        raise RoadmapUnavailable(message + ' Support reference: ' + reference + '.') from e
    chs=present_courses(plan['selections'],grade)
    chs.update(grade_note=('Grade 8: begin planning grade 9.' if int(grade)==8 else f'Grade {grade}: course options for your remaining time at CHS.')+' These are options to discuss, not a confirmed schedule. Completed courses and placement have not been provided.',
        experience=plan['experience'],next=plan['next_step'],reflection=plan['reflection'],
        good=plan['caveat']+' Source: CHS 2025–26 Program of Studies; current-year availability is not verified. Ask your counselor to confirm prerequisites, placement and pathway entry.',
        source='CHS 2025–26 Program of Studies',programs=[],engine='catalog-grounded-ai-v1',catalog_year='2025-26',current_year_verified=False,
        career_source=CAREER_SOURCES.get(career,''))
    steps=[[s['title'],s['detail']] for s in plan['postsecondary']]
    return dict(summary=plan['summary'],steps=steps,rich_steps=[{'title':s[0],'bullets':[s[1]]} for s in steps],timeline='Training time varies by route and prior preparation.',keys=[],chs=chs)
