"""Reviewed AI planning with source checks and one bounded correction. No generic fallback."""
import json
import logging
import copy
import re
import os
import time
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
    'Roadmap contains an unfinished sentence.': 'UNFINISHED',
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
        numbers = rate_numbers(error)
        if numbers.get('requested', 0) > numbers.get('limit', float('inf')):
            return 'RATE-SIZE', 'The roadmap request exceeds the AI account’s token allowance. The administrator needs to adjust request size or the API limit.'
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
Return direct_selections, foundation_selections, and supporting_selections arrays. Together they
must contain 3–10 unique course options, including 2–5 useful starting options and a selective progression
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
Select the strongest direct and foundational options, plus at most two supporting choices in total.
Direct courses teach career-specific content. Foundations build essential science, mathematics,
computing, communication or other skills needed for this career. Supporting options are secondary
helpful electives; do not mislabel essential laboratory science or quantitative preparation as filler. Do not
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
Write to the student as "you". Use short COMPLETE sentences, never fragments or clipped words.
Aim well below the hard character limits: summary 2 sentences (180–350 characters); each course
rationale 1–2 sentences (100–300 characters); each training stage 1–2 sentences (80–250 characters).
Experience should be ONE specific activity (120–300 characters), not a list of vague suggestions.
Every AP recommendation must explicitly say it is optional and depends on demonstrated readiness
and counselor/teacher placement. A generic note elsewhere is not enough for an AP rationale.
OR prerequisites are alternatives: do not tell a student they must finish all the alternatives.
Do not repeat a course they may already have completed as though their transcript were known.
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
Examine six separate criteria and state a concrete finding for each BEFORE deciding approval:
source_support: does each cited passage support the actual skill claimed? A title or broad welcome
sentence is not evidence for technical skills found only in another passage. Also check full descriptions.
career_fit: are these the strongest useful options for this career, without padding or missed direct choices?
grade_readiness: are grades correct, entry conditions honest, and EVERY AP course explicitly optional
and conditional on readiness/placement within its own rationale? Do not accept only a general caveat.
sequence: do planned years respect selected prerequisites, OR alternatives and limited remaining time?
Do not imply additional mandatory prerequisites after one valid alternative has already been planned.
training_route: does the postsecondary route match the occupation and distinguish optional credentials?
readability: does every prose field end as a coherent complete sentence, without clipped words, overload,
or vague activity lists? Examine the END of summary and each rationale in particular.
A finding must identify actual courses or text in this proposed plan, not simply assert "looks correct".
Set each criterion passed=false when it fails; include actionable correction instructions in issues.
Return approved=true ONLY when all six criteria pass and issues is empty. Do not output a corrected plan.''' 

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
    'evidence':{'type':'string','pattern':r'^CHS-[0-9]{3}:E[1-9][0-9]*$'},
    'why':prose(40,550)
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
REVIEW_CRITERIA = ('source_support','career_fit','grade_readiness','sequence','training_route','readability')
REVIEW_SCHEMA=obj({
    'checks':obj({key:obj({'finding':STR,'passed':{'type':'boolean'}}) for key in REVIEW_CRITERIA}),
    'issues':{'type':'array','items':STR}, 'approved':{'type':'boolean'}
})


def plan_schema(career, grade):
    """The generation contract itself permits only eligible course/year pairs."""
    schema = copy.deepcopy(PLAN_SCHEMA)
    schema['properties']['career'] = {'type':'string','enum':[career]}
    schema['properties']['grade']['enum'] = [int(grade)]
    variants = []
    for year in range(max(9, int(grade)), 13):
        selection = copy.deepcopy(SELECTION)
        selection['properties']['course_id']['enum'] = [cid for cid,c in SELECTABLE.items() if year in c['grades']]
        selection['properties']['planned_grade']['enum'] = [year]
        del selection['properties']['role']
        selection['required'].remove('role')
        variants.append(selection)
    del schema['properties']['selections']
    schema['required'].remove('selections')
    schema['$defs'] = {'course_option':{'anyOf':variants}}
    for role,limit in [('direct',10),('foundation',10),('supporting',2)]:
        key = role+'_selections'
        schema['properties'][key] = {'type':'array','items':{'$ref':'#/$defs/course_option'},'maxItems':limit}
        schema['required'].append(key)
    # Generate source-backed choices first, then summarize that actual plan.
    order=['career','grade','direct_selections','foundation_selections','supporting_selections']
    order += [key for key in schema['properties'] if key not in order]
    schema['properties']={key:schema['properties'][key] for key in order}
    schema['required']=order
    return schema


def review_issues(review):
    if not isinstance(review,dict) or set(review)!={'checks','approved','issues'} or type(review['approved']) is not bool or not isinstance(review['issues'],list) or not all(isinstance(x,str) and x.strip() for x in review['issues']):
        raise RoadmapValidationError('The educational quality review did not approve the plan.')
    checks=review['checks']
    if not isinstance(checks,dict) or set(checks)!=set(REVIEW_CRITERIA):
        raise RoadmapValidationError('The educational quality review did not approve the plan.')
    issues=list(review['issues'])
    for key,check in checks.items():
        if not isinstance(check,dict) or set(check)!={'finding','passed'} or type(check['passed']) is not bool or not isinstance(check['finding'],str) or not check['finding'].strip():
            raise RoadmapValidationError('The educational quality review did not approve the plan.')
        if not check['passed']:
            issues.append(key+': '+check['finding'])
    if review['approved'] is not True and not issues:
        raise RoadmapValidationError('The educational quality review did not approve the plan.')
    return issues


def complete_sentence(text):
    return isinstance(text,str) and text.rstrip().rstrip('"\'”’)]').endswith(('.', '!', '?'))


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
    # Table rows remove repeated JSON field names. The numbered passage lists
    # retain every description word; only the common planning note is deduplicated.
    columns = ['id','name','grades','prerequisite','prerequisite_groups',
               'alternative_group','planning_note','description_passages']
    common_note = 'Course completion and placement are unknown. Confirm level, eligibility and schedule with your counselor.'
    courses = []
    for c in SELECTABLE.values():
        item = {**c, 'alternative_group':c.get('alternative_group',''),
                'planning_note':'' if c['planning_note']==common_note else c['planning_note'],
                'description_passages':list(source_passages(c).values())}
        courses.append([item[k] for k in columns])
    return {'school':CATALOG['school'],'catalog_year':CATALOG['catalog_year'],
            'current_year_verified':False, 'columns':columns,
            'common_planning_note':common_note,
            'passage_reference':'Each description_passages list is numbered E1, E2, etc. Evidence is the course ID, colon, and passage number: CHS-131:E2.',
            'courses':courses}


def resolve_evidence(plan):
    """Expand only a valid reference to this course's own catalog passage.

    Unknown/cross-course labels remain invalid and are rejected by the ordinary
    exact-source validator. Literal quotations remain supported for saved plans.
    """
    plan = copy.deepcopy(plan)
    groups = ('direct_selections','foundation_selections','supporting_selections')
    if isinstance(plan,dict) and any(key in plan for key in groups):
        expected = (set(PLAN_SCHEMA['required']) - {'selections'}) | set(groups)
        if set(plan) != expected or not all(isinstance(plan[key],list) for key in groups):
            raise RoadmapValidationError('Incomplete roadmap structure.')
        selections=[]
        for key in groups:
            role=key.removesuffix('_selections')
            for item in plan.pop(key):
                if not isinstance(item,dict) or 'role' in item:
                    raise RoadmapValidationError('Invalid course selection structure.')
                selections.append({**item,'role':role})
        plan['selections']=selections
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
    prose_fields=[plan[k] for k in ('summary','experience','next_step','reflection','caveat')]
    prose_fields += [step['detail'] for step in steps] + [item['why'] for item in plan['selections']]
    if not all(complete_sentence(value) for value in prose_fields):
        raise RoadmapValidationError('Roadmap contains an unfinished sentence.')
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

def rate_numbers(error):
    """Read only numeric allowance information, never expose the provider body."""
    message = str(error)
    result = {}
    for field in ('Limit', 'Requested'):
        match = re.search(r'\b' + field + r'\s*:?\s*([0-9]+)', message)
        if match:
            result[field.lower()] = int(match.group(1))
    return result


def rate_wait(error):
    if getattr(error, 'status_code', None) != 429 or getattr(error, 'code', None) == 'insufficient_quota':
        return None
    numbers = rate_numbers(error)
    if numbers.get('requested', 0) > numbers.get('limit', float('inf')):
        return None  # A request larger than the allowance cannot be fixed by waiting.
    headers = getattr(getattr(error, 'response', None), 'headers', {})
    for key, scale in [('retry-after-ms', 0.001), ('retry-after', 1)]:
        value = headers.get(key, '')
        if value == '':
            continue
        try:
            seconds = float(value) * scale
        except (TypeError, ValueError):
            return None  # An unfamiliar reset format must not trigger an early retry.
        if 0 <= seconds <= 60:
            return max(1, seconds)
        return None  # Honor a longer reset by stopping, not retrying prematurely.
    match = re.search(r'try again in ([0-9.]+)s', str(error), re.IGNORECASE)
    if match:
        seconds = float(match.group(1))
        return min(60, max(1, seconds + 0.5)) if seconds <= 59.5 else None
    return 60  # One bounded wait when the provider supplies no reset header.


def _response(client, model, instructions, payload, schema, name, *, deadline=None):
    for attempt in range(2):
        remaining = 40 if deadline is None else deadline - time.monotonic()
        if remaining <= 0:
            raise RoadmapUnavailable('The roadmap service reached its time limit. Please try again later. Support reference: CHS-TIMEOUT.')
        try:
            response=client.responses.create(model=model,instructions=instructions,
                input=json.dumps(payload,ensure_ascii=False,separators=(',',':')),
                store=False,max_output_tokens=3500 if name=='chs_career_plan' else 2200,
                timeout=min(40.0, remaining),
                text={'format':{'type':'json_schema','name':name,'strict':True,'schema':schema}})
            break
        except Exception as error:
            wait = rate_wait(error)
            if attempt or wait is None or (deadline is not None and time.monotonic()+wait+40 > deadline):
                raise
            logger.warning('CHS roadmap waiting for provider rate reset (%d seconds)', wait)
            time.sleep(wait)
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
        generation_schema = plan_schema(career,grade)
        deadline = time.monotonic() + 220
        # At most one correction, always followed by the same deterministic and
        # independent review gates. Only temporary rate limits get a bounded wait;
        # authentication, quota and oversized requests are never retried.
        for attempt in range(2):
            draft = _response(client,model,SYSTEM,request_context,generation_schema,'chs_career_plan',deadline=deadline)
            plan = resolve_evidence(draft)
            try:
                validate_plan(plan,career,grade)
            except RoadmapValidationError as error:
                if attempt:
                    raise
                request_context = {**context, 'previous_plan':draft,
                    'correction_required':[str(error)],
                    'instruction':'Return a complete corrected plan. Preserve all source and educational requirements. Use evidence passage labels.'}
                continue
            review=_response(client,os.getenv('ROADMAP_REVIEW_MODEL',model),REVIEW_SYSTEM,
                             {**context,'proposed_plan':plan},REVIEW_SCHEMA,'chs_career_review',deadline=deadline)
            issues = review_issues(review)
            if not issues:
                break
            if attempt:
                raise RoadmapValidationError('The educational quality review did not approve the plan.')
            request_context = {**context, 'previous_plan':draft,
                'correction_required':issues,
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
