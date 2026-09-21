"""Catalog-grounded Armie pathways; no fallback to an unrelated civilian career.

The explicit role/profile manifest is reviewed independently of route selection.
Unknown jobs/schools fail validation instead of receiving a generic course list.
School placement cannot be certified without a student's completed coursework.
"""
from copy import deepcopy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / 'data/army_school_profiles.json').read_text())
SUPPLEMENT = json.loads((ROOT / 'data/army_catalog_supplement.json').read_text())
AUDIT_REVISION = 'armie-school-review-2026-09-21-v1'


def catalogs(bhs_catalog, ghs_catalog):
    result = {'bhs': deepcopy(bhs_catalog), 'ghs': deepcopy(ghs_catalog)}
    for school, changes in SUPPLEMENT.items():
        for key, update in changes.items():
            result[school].setdefault(key, {}).update(update)
    return result


def validate_roles(jobs, school_catalogs):
    if set(jobs) != set(DATA['roles']):
        raise ValueError('Army choices need an explicit reviewed school profile')
    for job, key in DATA['roles'].items():
        profile = DATA['profiles'][key]
        for school in ('bhs', 'ghs'):
            ids = profile[school]
            if len(ids) != len(set(ids)) or not ids:
                raise ValueError(f'Duplicate or empty profile: {job}/{school}')
            for course_id in ids:
                record = school_catalogs[school][course_id]
                if not record['grades'] or any(g not in range(9, 13) for g in record['grades']):
                    raise ValueError(f'Invalid grade data: {school}/{course_id}')


def school_pathway(job, grade, school, school_catalogs, bhs_programs):
    grade = int(grade)
    if grade not in range(8, 13) or school not in ('bhs', 'ghs'):
        raise ValueError('Unsupported Army school or grade')
    profile_id = DATA['roles'][job]
    profile = DATA['profiles'][profile_id]
    catalog = school_catalogs[school]
    candidates = profile[school]
    current = [key for key in candidates if grade in catalog[key]['grades']]
    future = [key for key in candidates if grade not in catalog[key]['grades'] and any(g > grade for g in catalog[key]['grades'])]

    def detail(key, planned=False):
        item = catalog[key]
        name = item.get('name', key)
        focus = item.get('focus', item.get('why', ''))
        prereq = item.get('prerequisite', '')
        # Do not infer completed prerequisites from grade alone.
        reason = f'Preparation to discuss for {job}: ' + focus
        if prereq:
            reason += ' Discuss placement and entry requirements before enrolling.'
        return {'id': key, 'name': name, 'grades': ', '.join(map(str,item['grades'])),
                'eligible_grades': list(item['grades']),
                'department': item.get('department', ''), 'focus': reason, 'why': reason,
                'prerequisite': prereq, 'page': item.get('page'), 'planned': planned,
                'eligibility': 'future grade; prerequisites unassessed' if planned else 'grade permitted; prerequisites unassessed'}

    primary = [detail(k) for k in current[:3]]
    supporting = [detail(k) for k in current[3:]]
    later = [detail(k, True) for k in future]
    programs = []
    if school == 'bhs':
        for name in ('Job Shadowing', 'Senior Internship'):
            item = bhs_programs[name]
            if grade in item['grades'] or any(g > grade for g in item['grades']):
                programs.append({'name': name, 'grades': ', '.join(map(str,item['grades'])),
                                 'state': 'discuss eligibility now' if grade in item['grades'] else 'plan ahead',
                                 'detail': item['detail'] + f' Ask whether an approved opportunity can explore {job}; a placement is not guaranteed.'})
    else:
        for name, grades, detail_text in [
            ('Community Service for Credit', [9,10,11,12], 'An approved proposal is required before starting. Catalog p. 13.'),
            ('Capstone Project / Internship', [11,12], 'Discuss advisor/mentor approval, scheduling and eligibility. Catalog p. 13.'),
            ('Mastery Based Diploma Program', [11,12], 'Discuss a career-related research project and planning activities. Catalog p. 11.')]:
            state = 'discuss eligibility now' if grade in grades else 'plan ahead'
            programs.append({'name':name+' — '+state, 'grades':', '.join(map(str,grades)), 'state':state,
                             'detail':detail_text+f' Connect the project to {job}.'})
    actions = {
        8:'Plan a ninth-grade foundation and the preparation for later electives with your counselor.',
        9:'Review your current preparation with your counselor, choose a realistic foundation, and identify one later option.',
        10:'Check completed courses and plan the prerequisites for relevant junior/senior options.',
        11:'Review remaining graduation requirements and choose a useful senior-year course or approved project.',
        12:'Prioritize useful remaining courses and an approved experience; confirm post-graduation applications and training requirements.'}
    good = ('These are career-related options to discuss, not a required checklist or a verified enrollment decision. '
            f'This pathway emphasizes {profile["skills"]}. Grade eligibility does not prove completed prerequisites. Choose the next math, science or language level based on your record; do not repeat completed courses. '
            + profile['note'])
    response = {'profile_id': profile_id, 'audit_revision':AUDIT_REVISION,
                'primary_course_details': primary, 'course_details':primary,
                'supporting_course_details':supporting,'future_course_details':later,
                'courses':[c['name'] for c in primary], 'supporting_courses':[c['name'] for c in supporting],
                'future_courses':[c['name'] for c in later], 'programs':programs,
                'experience':profile['project'], 'good':good,
                'next':f'For {job}: '+actions[grade],
                'grade_note':f'For a current Grade {grade} student — '+('plan high-school options' if grade==8 else 'confirm placement and prerequisites'),
                'reflection':f'Which part of {profile["skills"]} would you like to practice?'}
    return response
