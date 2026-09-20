"""Predictable, catalog-backed CHS roadmaps for every supported career.

Selection uses explicit educational mappings and grade-specific entry routes.
All source facts are read from chs_catalog; no provider call is made. The former
AI engine remains available only for its historical regression tests, not as a
runtime fallback. Portrait generation is unchanged.
"""
import copy
import json
from pathlib import Path
from chs_catalog import CATALOG, SELECTABLE, COURSES, present_courses, validate_selections, RoadmapValidationError
from chs_pathway_data import FAMILIES, PROFILES, REASONS, ENTRY_FUTURES
from chs_roadmap import RoadmapUnavailable, PROFILE_SOURCES

ENGINE_REVISION = 'chs-catalog-pathways-2026-09-20'
TRAINING = json.loads((Path(__file__).parent / 'chs_career_training.json').read_text(encoding='utf-8'))
PATHS = {'employee','owner','explore'}
PRIORITIES = {
 'Doing work I enjoy':'Which part of the activity would you want to do again, and which part felt less appealing?',
 'Helping people':'Who benefits from this work, and what would doing it responsibly require of you?',
 'High income potential':'Compare training costs, time to qualify and typical entry-level earnings with a counselor; avoid judging a career by its highest advertised salary.',
 'Creativity':'Identify one part of the activity where you can compare two approaches and explain your design or problem-solving choices.',
 'Job stability':'Ask a professional which skills remain useful when employers, technology or local demand change.',
 'Being my own boss':'Ask which qualifications and experience would be needed before independent work, and which duties would come with running an organization.',
}


def course_id(number):
    return f'CHS-{number:03d}'


def pairs_for(profile, grade, path):
    target=max(9,grade)
    family_name=profile['family']
    family=FAMILIES[family_name]
    years=copy.deepcopy(family['years'])
    if target>9:
        years[target]=list(family['entries'][target])
        for year,items in ENTRY_FUTURES.get(family_name,{}).get(target,{}).items():
            years[year]=list(items)
    pairs=[]
    seen=set()
    for year in range(target,13):
        for number in years[year]:
            if number not in seen:
                pairs.append((number,year,False))
                seen.add(number)
    # A business interest adds an explicitly supporting option, without replacing
    # the occupation's science, craft or technical preparation. No ownership
    # course is imposed on public service or military careers.
    if path=='owner' and family_name not in {'publicoffice','military'}:
        number=146 if target==9 else 150
        if number not in seen:
            pairs.append((number,target,True))
        # Already planned business courses stay at their intentional year.
    return pairs


def entry_note(course):
    parts=[]
    if course['name'].startswith('AP ') or course['id']=='CHS-013':
        parts.append('Optional advanced course: discuss workload and readiness with your teacher.')
    if course['prerequisite'] or course['prerequisite_groups']:
        parts.append('Eligibility is conditional on meeting the entry requirements below; prior completion has not been assumed.')
    if ['CHS-103'] in course['prerequisite_groups']:
        parts.append('If Art I is not complete, ask about Art I: Visual Foundations as your starting option instead.')
    return ' '.join(parts)


def generate_chs_roadmap(career, grade, *, path='explore', priority='Doing work I enjoy', api_key='', client=None):
    """Return actual catalog options; compatibility args never call an AI service."""
    if not isinstance(career,str) or career not in PROFILES:
        raise RoadmapUnavailable('Choose one of the available CHS careers.')
    if isinstance(grade,bool) or str(grade) not in {'8','9','10','11','12'}:
        raise RoadmapUnavailable('Choose a grade from 8 through 12.')
    if not isinstance(path,str) or path not in PATHS or not isinstance(priority,str) or priority not in PRIORITIES:
        raise RoadmapUnavailable('Choose valid pathway and priority selections.')
    grade=int(grade)
    target=max(9,grade)
    profile=PROFILES[career]
    family=FAMILIES[profile['family']]
    selections=[]
    for number,year,ownership in pairs_for(profile,grade,path):
        cid=course_id(number)
        c=SELECTABLE[cid]
        why=REASONS[number].format(work=profile['work'])
        if ownership:
            why='Because you selected the ownership path, consider this supporting option. '+why
        selections.append(dict(course_id=cid, planned_grade=year,
            role='supporting' if ownership else ('direct' if number in family['direct'] else 'foundation'),
            why=why, evidence=c['description']))
    try:
        validate_selections(selections,grade)
        if not set(range(target,13)).issubset({s['planned_grade'] for s in selections}):
            raise RoadmapValidationError('A remaining school year has no course options.')
        cards=present_courses(selections,grade)
    except RoadmapValidationError as error:
        raise RoadmapUnavailable('This CHS pathway needs a catalog correction. Support reference: CHS-CATALOG-PATHWAY.') from error
    for group in ('primary_course_details','supporting_course_details','future_course_details'):
        for card in cards[group]:
            c=SELECTABLE[card['course_id']]
            card['planning_note']=' '.join(filter(None,[
                'If you already completed this course, discuss the next suitable option instead of repeating it.',
                entry_note(c),c['planning_note']]))
    current=cards['primary_course_details']
    names=' and '.join(c['name'] for c in current[:2])
    start=('As a grade 8 student, use this as a plan for entering grade 9; these are not middle-school enrollments.'
           if grade==8 else f'For your current grade {grade}, begin with the courses below and discuss later options as shown.')
    start+=' These are career-related options, not a complete schedule. Completed courses and placement have not been provided.'
    late=''
    if grade>=11:
        late=' Starting now does not require completing an entire four-year pathway. Focus on the courses that fit your remaining time, and confirm any advanced-course eligibility.'
    next_step=f'Ask your counselor about {names} for grade {target}. Check your completed courses, graduation requirements and available schedule before enrolling.'
    if grade==12:
        next_step+=' Compare your next training or employment options now.'
    elif grade==8:
        next_step+=' Include your middle-school counselor when planning the transition to CHS.'
    path_note={
        'employee':'Ask what training and beginner experience employers expect before hiring for this work.',
        'owner':('Explore leadership and public responsibility within this career; the ownership choice does not turn military service or elected office into a private business.' if profile['family'] in {'publicoffice','military'} else 'Your ownership interest adds a business perspective. Professional qualifications still come first, and business preparation does not authorize independent regulated practice.'),
        'explore':'Use the activity to decide whether the actual daily work fits your interests before committing to a training route.',
    }[path]
    age_note=('For now, explore through an interview, a public event or an age-appropriate activity with adult guidance.' if grade==8 else 'Arrange activities through your teacher or counselor; access, age limits and supervision depend on the host.')
    good=(family['limitation']+late+' Where prerequisites list alternatives, you need the appropriate permitted route, not every alternative. '
          'Course availability, CTE placement and current-year requirements must be confirmed with CHS.')
    training=TRAINING[career]
    cards.update(grade_note=start, experience=profile['activity']+' '+age_note,
        next=next_step, reflection=PRIORITIES[priority]+' '+path_note, good=good,
        source='CHS 2025–26 Program of Studies',programs=[],
        engine='catalog-pathways',engine_revision=ENGINE_REVISION,
        catalog_year=CATALOG['catalog_year'],current_year_verified=False,
        career_source=PROFILE_SOURCES.get(career,[''])[0],
        career_sources=PROFILE_SOURCES.get(career,[]),
        personalization={'career':career,'grade':grade,'path':path,'priority':priority},
        models={'planner':None,'reviewer':None})
    steps=copy.deepcopy(training['steps'])
    high_school={'title':'High School','bullets':[
        f'Explore {career} through the CHS courses below, beginning with {names}.',
        next_step,
        profile['activity']+' '+age_note]}
    rich_steps=[high_school]+copy.deepcopy(training['rich_steps'])
    return dict(summary=training['summary'], steps=steps,
        rich_steps=rich_steps, timeline=training['timeline'],
        keys=list(training['keys']),chs=cards)
