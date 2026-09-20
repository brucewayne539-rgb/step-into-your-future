"""CHS catalog grounding. Course facts come from the supplied detailed course entries.

Career selection belongs to the AI planner, never substring/keyword matching.
This module enforces catalog identity, grade eligibility and sequence constraints.
"""
import json
import re
from pathlib import Path

CATALOG = json.loads((Path(__file__).parent / 'data/chs_catalog_2025_26.json').read_text(encoding='utf-8'))
COURSES = {c['id']: c for c in CATALOG['courses']}
SELECTABLE = {k: c for k, c in COURSES.items() if c['eligible_for_recommendation']}

class RoadmapValidationError(ValueError):
    pass

def normalized(text):
    return re.sub(r'\s+', ' ', text).strip().casefold()

def validate_selections(selections, grade):
    """Reject an invalid plan in full; never silently discard or invent a course."""
    target = max(9, int(grade))
    if not isinstance(selections, list) or not 3 <= len(selections) <= 10:
        raise RoadmapValidationError('A plan must contain 3–10 justified course options.')
    seen, alternatives, planned = set(), set(), {}
    for item in selections:
        if not isinstance(item, dict) or set(item) != {'course_id','planned_grade','role','why','evidence'}:
            raise RoadmapValidationError('Invalid course selection structure.')
        cid = item['course_id']
        if cid not in SELECTABLE or cid in seen:
            raise RoadmapValidationError('Unknown, restricted or duplicate course ID.')
        seen.add(cid)
        c = SELECTABLE[cid]
        year = item['planned_grade']
        if type(year) is not int or year not in c['grades'] or year < target:
            raise RoadmapValidationError('Course is outside its catalog grade range or in the past.')
        if item['role'] not in {'direct','foundation','supporting'}:
            raise RoadmapValidationError('Invalid course purpose.')
        if not isinstance(item['why'],str) or not 40 <= len(item['why']) <= 550:
            raise RoadmapValidationError('A specific, concise explanation is required.')
        quote = item['evidence']
        if not isinstance(quote,str) or len(quote.strip()) < 18 or normalized(quote) not in normalized(c['description']):
            raise RoadmapValidationError('Course rationale lacks matching catalog evidence.')
        alt = c.get('alternative_group')
        if alt and alt in alternatives:
            raise RoadmapValidationError('Select one of alternative course levels, not both.')
        if alt: alternatives.add(alt)
        planned[cid] = year
    if sum(s['planned_grade'] == target for s in selections) < 2:
        raise RoadmapValidationError('No starting options for this grade.')
    if sum(s['role']=='supporting' for s in selections)>2:
        raise RoadmapValidationError('Too many supporting electives.')
    if not any(s['planned_grade']==target and s['role'] in {'direct','foundation'} for s in selections):
        raise RoadmapValidationError('Missing starting career preparation.')
    if sum(s['planned_grade']==target for s in selections)>5:
        raise RoadmapValidationError('Too many concurrent options.')
    if not any(s['role'] in {'direct','foundation'} for s in selections):
        raise RoadmapValidationError('Missing career preparation.')
    for cid, year in planned.items():
        for group in COURSES[cid]['prerequisite_groups']:
            selected_prereqs = [planned[p] for p in group if p in planned]
            if selected_prereqs and not any(p < year for p in selected_prereqs):
                raise RoadmapValidationError('A selected prerequisite must precede the advanced course.')
    return selections

def present_courses(selections, grade):
    validate_selections(selections, grade)
    target = max(9, int(grade))
    result = dict(primary_course_details=[], supporting_course_details=[], future_course_details=[])
    for s in selections:
        c = COURSES[s['course_id']]
        prereq = c['prerequisite'] or 'No separate prerequisite is listed in this course entry; confirm placement and program requirements.'
        if c['prerequisite_groups'] and not c['prerequisite']:
            prereq = 'Sequence preparation: ' + '; '.join(' or '.join(COURSES[p]['name'] for p in g) for g in c['prerequisite_groups']) + '. Confirm with the department.'
        card = dict(course_id=c['id'], name=c['name'], why=s['why'], grades='–'.join(map(str,[min(c['grades']),max(c['grades'])])) if len(c['grades'])>1 else str(c['grades'][0]),
                    department=c['department'],page=c['page'],pdf_page=c['pdf_page'],planned=s['planned_grade']>target,planned_grade=s['planned_grade'],
                    role=s['role'], prerequisite=prereq, planning_note=c['planning_note'], evidence=s['evidence'])
        key = 'future_course_details' if card['planned'] else ('supporting_course_details' if s['role']=='supporting' else 'primary_course_details')
        result[key].append(card)
    result['future_course_details'].sort(key=lambda c:c['planned_grade'])
    return result
