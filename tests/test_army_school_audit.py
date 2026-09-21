"""Semantic checks use explicit expectations, not the production mapping algorithm.
All route tests mock ONLY paid image generation, never the school pathway.
"""
import json
from types import SimpleNamespace
from unittest.mock import patch
import pytest
import app
from army_school_pathways import school_pathway, validate_roles, AUDIT_REVISION

JOBS = list(app.ARMY_CAREERS)
SCHOOLS = ('bhs', 'ghs')
GRADES = (8, 9, 10, 11, 12)

def plan(job, school='bhs', grade=9):
    return school_pathway(job, grade, school, app.ARMY_SCHOOL_CATALOGS, app.BHS_PROGRAMS)

def cards(result):
    return sum((result[k] for k in ('primary_course_details','supporting_course_details','future_course_details')), [])

@pytest.mark.parametrize('job', JOBS)
@pytest.mark.parametrize('school', SCHOOLS)
@pytest.mark.parametrize('grade', GRADES)
def test_all_role_school_grade_results(job, school, grade):
    p = plan(job, school, grade)
    allcards = cards(p)
    assert allcards, (job,school,grade)
    assert len({x['id'] for x in allcards}) == len(allcards)
    assert p['audit_revision'] == AUDIT_REVISION
    assert job in p['next']
    for group in ('primary_course_details','supporting_course_details'):
        for c in p[group]:
            source = app.ARMY_SCHOOL_CATALOGS[school][c['id']]
            assert grade in source['grades']
            assert not c['planned']
            assert c['prerequisite'] == source.get('prerequisite','')
            assert 'unassessed' in c['eligibility']
    for c in p['future_course_details']:
        assert grade not in c['eligible_grades']
        assert any(g > grade for g in c['eligible_grades'])
        assert c['planned']
    if grade == 8:
        assert not p['primary_course_details'] and not p['supporting_course_details']
    if grade == 12:
        assert not p['future_course_details']
    assert 'completed prerequisites' in p['good']
    assert all('Engineer' not in p[k] or 'Engineer' in job for k in ('next',))

# These independently chosen expectations catch plausible-but-wrong families.
@pytest.mark.parametrize('job,required,forbidden', [
 ('Air Traffic Control (ATC) Operator', {'Geometry','Public Speaking','Physics I'}, {'Hands-On Engineering Workshop','Robotics Foundations','Automotive Mechanics Technology I'}),
 ('Aviation Operations Specialist', {'Foundations of Business – Research','Public Speaking'}, {'Automotive Mechanics Technology I'}),
 ('Fixed Wing Aviator Warrant Officer', {'Geometry','Physics I'}, {'Residential Construction'}),
 ('Air Traffic Control Equipment Repairer', {'Physics I','Advanced Power Technology'}, {'Automotive Mechanics Technology I'}),
 ('Avionic Mechanic', {'Physics I','Advanced Power Technology'}, {'Automotive Mechanics Technology I'}),
 ('Microbiologist', {'Biology','Chemistry','AP/ECE Biology'}, {'Anatomy & Physiology','Hands-On Engineering Workshop'}),
 ('Petroleum Laboratory Specialist', {'Chemistry','Statistics & Probability'}, {'Anatomy & Physiology','Biology'}),
 ('Biomedical Equipment Specialist', {'Physics I','Advanced Power Technology'}, {'Certified Nursing Assistant (CNA) Program'}),
 ('Water Treatment Specialist', {'Biology','Chemistry'}, {'Automotive Mechanics Technology I'}),
 ('Environmental Science & Engineering Officer', {'Biology','Chemistry','Environmental Science A: Understanding Ecology'}, {'Introductory Woodworking'}),
 ('Musician', {'Concert Band','Music Theory'}, {'Acting Workshop: The Art of Acting'}),
 ('Band Officer', {'Concert Band','Music Theory'}, {'Acting Workshop: The Art of Acting'}),
 ('Foreign Language Specialist', {'Spanish I','Spanish II','French I'}, {'Photography','Digital Journalism'}),
 ('Signals Intelligence Voice Interceptor', {'Spanish I','Spanish II'}, {'Photography'}),
 ('Dietitian', {'Biology','Chemistry','Culinary Arts','ECE Fundamentals of Nutrition'}, {'Automotive Mechanics Technology I'}),
 ('Nutrition Care Specialist', {'Culinary Arts','Anatomy & Physiology'}, {'Hands-On Engineering Workshop'}),
 ('Optical Laboratory Specialist', {'Physics I','Geometry'}, {'Certified Nursing Assistant (CNA) Program'}),
 ('Nuclear Medical Science Officer', {'Physics I','Biology','Chemistry'}, {'Robotics Foundations'}),
 ('Pharmacist', {'Chemistry','Biology','Anatomy & Physiology'}, {'Automotive Mechanics Technology I'}),
 ('Clinical Psychologist', {'Psychology','Statistics & Probability'}, {'Introductory Woodworking'}),
 ('Physical Therapy Specialist', {'Anatomy & Physiology','ECE Kinesiology'}, {'Accounting I'}),
 ('Paralegal Specialist', {'Criminal Justice','Business Law'}, {'Hands-On Engineering Workshop'}),
 ('Military Working Dog Handler', {'Biology','Psychology'}, {'Automotive Mechanics Technology I'}),
 ('Diver', {'Physics I','PE 9'}, {'Accounting I'}),
 ('Utilities Equipment Repairer', {'Physics I','Advanced Power Technology'}, {'Business Law'}),
 ('Geospatial Engineer', {'Geometry','AP Human Geography'}, {'Automotive Mechanics Technology I'}),
 ('Cyber Operations Specialist', {'Exploration of Computer Science','AP Computer Science Principles'}, {'Introductory Woodworking'}),
 ('Mortuary Affairs Specialist', {'Biology','Psychology'}, {'Robotics Foundations'}),
 ('Veterinary Food Inspection Specialist', {'Biology','Chemistry','Culinary Arts'}, {'Anatomy & Physiology'}),
 ('Clinical Laboratory Scientist', {'Biology','Chemistry'}, {'Certified Nursing Assistant (CNA) Program'}),
])
def test_semantic_boundaries(job, required, forbidden):
    ids = {c['id'] for c in cards(plan(job,grade=9))}
    assert required <= ids
    assert not (forbidden & ids)

@pytest.mark.parametrize('job,required,forbidden', [
 ('Air Traffic Control (ATC) Operator',{'geometry','physics','english9'},{'auto','wood','metal'}),
 ('Avionic Mechanic',{'electronics','physics'},{'auto'}),
 ('Microbiologist',{'bio','chem','lab'},{'auto','engineering'}),
 ('Musician',{'band','theory'},{'theatre'}),
 ('Foreign Language Specialist',{'spanish1','spanish2','french2'},{'photo','film'}),
 ('Water Treatment Specialist',{'chem','bio'},{'auto'}),
 ('Optical Laboratory Specialist',{'physics','geometry'},{'healthcare'}),
 ('Petroleum Laboratory Specialist',{'chem','lab'},{'anatomy','bio'}),
])
def test_ghs_semantic_boundaries(job, required, forbidden):
    ids={c['id'] for c in cards(plan(job,'ghs',9))}
    assert required <= ids and not forbidden & ids

def test_original_catalog_constraints_independent_of_runtime_data():
    # Original supplied BHS catalog pp. 44-46, 51-52, 55-59, 79-81;
    # GHS pp. 38-41, 69-71. Prevent missing prerequisites recurring.
    b=app.ARMY_SCHOOL_CATALOGS['bhs'];g=app.ARMY_SCHOOL_CATALOGS['ghs']
    assert b['Biology']['grades']==[9]
    assert b['PE 9']['grades']==[9]
    assert b['PE 10']['grades']==[10]
    assert b['ECE Fundamentals of Nutrition']['grades']==[11,12]
    assert b['Chemistry']['grades']==[10,11,12]
    assert 'Algebra I credit' in b['Chemistry']['prerequisite']
    assert 'Chemistry I Honors credit' in b['AP Chemistry II']['prerequisite']
    assert b['Public Speaking']['grades']==[10,11,12]
    assert 'C- in Algebra I' in b['Geometry']['prerequisite']
    assert 'director approval' in b['Concert Band']['prerequisite']
    assert b['Spanish III']['grades']==[10,11,12]
    assert b['French III']['grades']==[11,12]
    assert g['spanish1']['grades']==[9,10,11]
    assert g['french2']['grades']==[9,10,11]
    assert g['spanish3']['grades']==[10,11,12]
    assert g['aptheory']['grades']==[10,11,12]
    assert 'Teacher recommendation' in g['aptheory']['prerequisite']
    senior_ids={c['id'] for c in cards(plan('Foreign Language Specialist','ghs',12))}
    assert 'spanish1' not in senior_ids and 'french2' not in senior_ids
    assert 'spanish3' in senior_ids and 'french3' in senior_ids


def test_unknown_roles_cannot_silently_receive_generic_courses():
    with pytest.raises(KeyError): plan('Invented new job')
    with pytest.raises(ValueError): validate_roles(JOBS+['New role without review'],app.ARMY_SCHOOL_CATALOGS)

@pytest.fixture
def route_client():
    app.app.config.update(TESTING=True,SESSION_COOKIE_SECURE=False)
    fake=SimpleNamespace(images=SimpleNamespace(edit=lambda **kw:SimpleNamespace(data=[SimpleNamespace(b64_json='image-test-only')])))
    with patch.object(app,'admin_preview_gate',return_value=(True,'Ready')), patch.object(app,'rate_limited',return_value=False), patch.object(app,'OpenAI',return_value=fake), patch.object(app,'load_key',return_value='test'), patch.object(app,'burn_portrait_watermark',return_value='image-test-only'):
        client=app.app.test_client()
        with client.session_transaction() as s:
            s['demo_access']=True;s['csrf_token']='test';s['admin_preview_count']=0
        yield client

@pytest.mark.parametrize('job',JOBS)
@pytest.mark.parametrize('school',SCHOOLS)
@pytest.mark.parametrize('grade',GRADES)
def test_actual_generation_route_uses_audited_pathway(route_client,job,school,grade):
    response=route_client.post('/api/admin-preview/generate',headers={'X-CSRF-Token':'test'},json={
        'mode':'army','school':school,'sample_id':'grade9','grade':str(grade),
        'career':job,'age':'25','path':'employee','priority':'Technology and cyber'})
    assert response.status_code==200, response.get_json()
    p=response.get_json()[school]
    assert p==plan(job,school,grade)
    assert p['audit_revision']==AUDIT_REVISION
