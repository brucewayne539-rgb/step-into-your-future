import copy
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import app as application
from chs_catalog import CATALOG, COURSES, SELECTABLE, validate_selections, RoadmapValidationError
from chs_roadmap import generate_chs_roadmap, validate_plan, RoadmapUnavailable, PLAN_SCHEMA, REVIEW_SCHEMA
from chs_fixtures import plan

PRIORITY=['Neurosurgeon','Nurse Practitioner','Cybersecurity Specialist']

def fake_client(document,review=None):
    client=MagicMock()
    client.responses.create.side_effect=[SimpleNamespace(status='completed',output_text=json.dumps(document)),SimpleNamespace(status='completed',output_text=json.dumps(review or dict(approved=True,issues=[])))]
    return client

@pytest.mark.parametrize('career',PRIORITY)
@pytest.mark.parametrize('grade',[8,9,10,11,12])
def test_reviewed_examples_and_catalog_grounding(career,grade):
    p=plan(career,grade);client=fake_client(p)
    result=generate_chs_roadmap(career,grade,client=client)
    assert client.responses.create.call_count==2
    all_cards=sum([result['chs'][k] for k in ['primary_course_details','supporting_course_details','future_course_details']],[])
    assert len(all_cards)==len(p['selections'])
    for c in all_cards:
        source=COURSES[c['course_id']]
        assert c['name']==source['name'] and c['page']==source['page']
        assert c['planned_grade'] in source['grades']
        assert c['prerequisite'] and c['planning_note']
    for call in client.responses.create.call_args_list:
        assert call.kwargs['store'] is False
        payload=json.loads(call.kwargs['input'])
        assert set(payload['student'])=={'school','current_grade','career'}
        assert len(payload['catalog']['courses'])==152
    if grade==12:assert not result['chs']['future_course_details']
    if grade==8:assert 'grade 9' in result['chs']['grade_note']

@pytest.mark.parametrize('field,value',[('course_id','BHS-FAKE'),('planned_grade',8),('planned_grade',13),('planned_grade',True),('evidence','A fictional course description'),('why','good')])
def test_invalid_course_output_rejected(field,value):
    p=plan();p['selections'][0][field]=value
    with pytest.raises(RoadmapUnavailable):generate_chs_roadmap('Neurosurgeon',9,client=fake_client(p))

def test_grade_and_prerequisite_not_rewritten_by_model():
    p=plan();p['selections'][0]['grades']='8-12'
    with pytest.raises(RoadmapValidationError):validate_plan(p,'Neurosurgeon',9)
    p=plan();p['selections'][0]['planned_grade']=10
    # Human Body Systems is also in grade 10: selected foundation has to precede it.
    with pytest.raises(RoadmapValidationError):validate_plan(p,'Neurosurgeon',9)

@pytest.mark.parametrize('change',['duplicate','past','no_current','wrong_career','wrong_grade','empty','future_senior'])
def test_invalid_plan_shapes(change):
    p=plan(grade=12 if change=='future_senior' else 9)
    if change=='duplicate':p['selections'].append(copy.deepcopy(p['selections'][0]))
    elif change=='past':p['selections'][0]['planned_grade']=8
    elif change=='no_current':p['selections']=[x for x in p['selections'] if x['planned_grade']>9]
    elif change=='wrong_career':p['career']='Architect'
    elif change=='wrong_grade':p['grade']=10
    elif change=='empty':p['summary']=''
    elif change=='future_senior':p['selections'][0]['planned_grade']=13
    with pytest.raises(RoadmapValidationError):validate_plan(p,'Neurosurgeon',12 if change=='future_senior' else 9)

@pytest.mark.parametrize('career',['Neurosurgeon','Nurse Practitioner'])
@pytest.mark.parametrize('bad_id',['CHS-102','CHS-139','CHS-140'])
def test_reported_medical_mismatches_blocked(career,bad_id):
    p=plan(career,12);c=COURSES[bad_id]
    p['selections'][0]=dict(course_id=bad_id,planned_grade=12,role='direct',why='An invented explanation tries to present this unrelated course as direct preparation for clinical practice.',evidence=c['description'][:100])
    with pytest.raises(RoadmapValidationError):validate_plan(p,career,12)

def test_cyber_cannot_omit_direct_school_course():
    p=plan('Cybersecurity Specialist',9);p['selections']=[s for s in p['selections'] if s['course_id']!='CHS-131']
    with pytest.raises(RoadmapValidationError):validate_plan(p,p['career'],9)

def test_semantic_rejection_never_falls_back():
    client=fake_client(plan(),dict(approved=False,issues=['This is not educationally appropriate.']))
    with pytest.raises(RoadmapUnavailable):generate_chs_roadmap('Neurosurgeon',9,client=client)
    assert client.responses.create.call_count==2

@pytest.mark.parametrize('review',[{'approved':True,'issues':['Unsupported claim']},{'approved':'true','issues':[]},{'approved':True},{'approved':False,'issues':[]}])
def test_malformed_or_negative_review_fails_closed(review):
    with pytest.raises(RoadmapUnavailable):generate_chs_roadmap('Neurosurgeon',9,client=fake_client(plan(),review))

def test_provider_failure_and_missing_key():
    with pytest.raises(RoadmapUnavailable):generate_chs_roadmap('Neurosurgeon',9,api_key='')
    c=MagicMock();c.responses.create.side_effect=RuntimeError('secret provider message')
    with pytest.raises(RoadmapUnavailable) as e:generate_chs_roadmap('Neurosurgeon',9,client=c)
    assert 'secret' not in str(e.value) and c.responses.create.call_count==1

@pytest.mark.parametrize('status,text',[('incomplete','{}'),('completed',''),('completed','not JSON')])
def test_truncated_refused_or_malformed_response(status,text):
    c=MagicMock();c.responses.create.return_value=SimpleNamespace(status=status,output_text=text)
    with pytest.raises(RoadmapUnavailable):generate_chs_roadmap('Neurosurgeon',9,client=c)

def test_every_generate_calls_ai_again():
    c=fake_client(plan());c.responses.create.side_effect=list(c.responses.create.side_effect)*2
    generate_chs_roadmap('Neurosurgeon',9,client=c);generate_chs_roadmap('Neurosurgeon',9,client=c)
    assert c.responses.create.call_count==4

@pytest.mark.parametrize('cid,grades,page',[('CHS-034',[9],45),('CHS-035',[10],45),('CHS-036',[11],45),('CHS-040',[11,12],45),('CHS-043',[12],46),('CHS-047',[9,10,11,12],47),('CHS-048',[9,10,11,12],47),('CHS-049',[10,11,12],47),('CHS-050',[11,12],47),('CHS-051',[12],47),('CHS-131',[10,11,12],69),('CHS-132',[9,10,11,12],69),('CHS-134',[10,11,12],69),('CHS-135',[11,12],70),('CHS-102',[12],60)])
def test_facts_from_detailed_entries(cid,grades,page):
    assert COURSES[cid]['grades']==grades and COURSES[cid]['page']==page

def test_catalog_integrity_and_no_placement_assumptions():
    assert len(COURSES)==157 and len(SELECTABLE)==152
    for c in COURSES.values():
        assert c['name'] in c['description']
        assert c['pdf_page']==c['page']+1
        assert c['description'] and c['source']
        for group in c['prerequisite_groups']:assert all(cid in COURSES for cid in group)
    assert 'CHS-018' not in SELECTABLE and 'CHS-033' not in SELECTABLE

@pytest.fixture
def browser():
    application.app.config['TESTING']=True
    c=application.app.test_client()
    with c.session_transaction() as session:session['csrf_token']='chs-test';session['demo_access']=True
    return c

@pytest.mark.parametrize('career',list(application.CAREERS))
@pytest.mark.parametrize('grade',['8','9','10','11','12'])
def test_all_210_chs_route_selections_reach_ai(browser,career,grade):
    # Wiring test only. This does NOT claim 210 live AI or semantic evaluations.
    expected={'summary':'sentinel','chs':{'engine':'stub'}}
    with patch.object(application,'rate_limited',return_value=False),patch.object(application,'generate_chs_roadmap',return_value=expected) as generate:
        r=browser.post('/api/chs/roadmap',json={'career':career,'grade':grade},headers={'X-CSRF-Token':'chs-test'})
    assert r.status_code==200
    assert r.json['school']=='CHS' and r.json['grade']==grade
    assert generate.call_args.args==(career,grade)

@pytest.mark.parametrize('payload',[[],None,{'career':['Neurosurgeon'],'grade':'9'},{'career':'Neurosurgeon','grade':{}},{'career':'Neurosurgeon','grade':9},{'career':'Neurosurgeon','grade':'7'},{'career':'Neurosurgeon','grade':'9','student_name':'Test'},{'career':'Neurosurgeon','grade':'9','path':[]}])
def test_invalid_student_input(browser,payload):
    with patch.object(application,'rate_limited',return_value=False),patch.object(application,'generate_chs_roadmap') as generate:
        r=browser.post('/api/chs/roadmap',json=payload,headers={'X-CSRF-Token':'chs-test'})
    assert r.status_code==400
    generate.assert_not_called()

def test_csrf_and_provider_failure(browser):
    payload=dict(career='Neurosurgeon',grade='9')
    assert browser.post('/api/chs/roadmap',json=payload).status_code==400
    with patch.object(application,'generate_chs_roadmap',side_effect=RoadmapUnavailable('Unavailable')),patch.object(application,'rate_limited',return_value=False):
        r=browser.post('/api/chs/roadmap',json=payload,headers={'X-CSRF-Token':'chs-test'})
    assert r.status_code==503 and not r.json['ok'] and 'chs' not in r.json

@pytest.mark.parametrize('school',['bhs','ghs'])
@pytest.mark.parametrize('career',list(application.CAREERS))
@pytest.mark.parametrize('grade',['8','9','10','11','12'])
def test_existing_420_school_roadmaps_stay_local(browser,school,career,grade):
    with patch.object(application,'rate_limited',return_value=False),patch.object(application,'generate_chs_roadmap') as ai:
        r=browser.post('/api/ghs/roadmap' if school=='ghs' else '/api/roadmap',json=dict(career=career,grade=grade,path='explore',priority='Doing work I enjoy'),headers={'X-CSRF-Token':'chs-test'})
    assert r.status_code==200 and r.json['ok']
    assert school in r.json
    ai.assert_not_called()

def test_chs_template_shows_all_required_metadata(browser):
    r=browser.get('/chs');assert r.status_code==200
    for token in [b'/chs-approved-hero.png',b'Entry requirements:',b'planning_note',b'planned_grade',b'supporting_course_details',b'futureCourses',b'Administrator Demo',b'Shakespeare']:
        assert token in r.data
    assert b'<select id="path"' not in r.data

@pytest.mark.parametrize('cid,expected',[('CHS-024','Geometry and Algebra 2'),('CHS-029','Algebra 1'),('CHS-031','Precalculus'),('CHS-037','Principles of Physics and Algebra 2'),('CHS-049','PLTW Principles of Biomedical Science'),('CHS-050','PLTW Human Body Systems'),('CHS-100','Fitness I'),('CHS-112','Art I'),('CHS-113','Graphic Design I'),('CHS-135','Algebra 2 OR AP Computer Science Principles'),('CHS-137','CTE Program Enrollment'),('CHS-141','Robotics I'),('CHS-145','Pathway Enrollment'),('CHS-151','CTE Program Enrollment')])
def test_prerequisites_embedded_as_pdf_graphics(cid,expected):
    assert COURSES[cid]['prerequisite']==expected
    assert COURSES[cid]['requirements_verified_visually']

@pytest.mark.parametrize('sample_id',['grade9','grade11'])
@pytest.mark.parametrize('grade',['8','9','10','11','12'])
def test_admin_demo_uses_same_chs_engine_and_preserves_fictional_people(browser,sample_id,grade):
    from test_admin_preview import FakeOpenAIClient
    expected=generate_chs_roadmap('Neurosurgeon',grade,client=fake_client(plan('Neurosurgeon',int(grade))))
    with patch.object(application,'admin_preview_gate',return_value=(True,'')),patch.object(application,'rate_limited',return_value=False),patch.object(application,'OpenAI',FakeOpenAIClient),patch.object(application,'load_key',return_value='sk-test'),patch.object(application,'generate_chs_roadmap',return_value=expected) as generate:
        r=browser.post('/api/admin-preview/generate',json=dict(school='chs',sample_id=sample_id,career='Neurosurgeon',grade=grade,age='25',path='explore',priority='Doing work I enjoy'),headers={'X-CSRF-Token':'chs-test'})
    assert r.status_code==200
    assert r.json['chs']==expected['chs'] and r.json['steps']==expected['steps']
    assert r.json['fictional_demo'] is True and r.json['image'].startswith('data:image/png;base64,')
    generate.assert_called_once_with('Neurosurgeon',grade,api_key='sk-test')


def test_admin_does_not_buy_image_when_roadmap_fails(browser):
    image_client=MagicMock()
    with patch.object(application,'admin_preview_gate',return_value=(True,'')),patch.object(application,'rate_limited',return_value=False),patch.object(application,'OpenAI',image_client),patch.object(application,'generate_chs_roadmap',side_effect=RoadmapUnavailable('Try later')):
        r=browser.post('/api/admin-preview/generate',json=dict(school='chs',sample_id='grade9',career='Neurosurgeon',grade='9',age='25',path='explore',priority='Doing work I enjoy'),headers={'X-CSRF-Token':'chs-test'})
    assert r.status_code==503
    image_client.assert_not_called()
    with browser.session_transaction() as s:assert s.get('admin_preview_count',0)==0

@pytest.mark.parametrize('success',[False,True])
def test_optional_photo_uses_same_plan_and_never_calls_images_on_failed_plan(browser,success):
    import io,base64
    from test_admin_preview import generated_png_b64
    image_client=MagicMock()
    image_client.return_value.images.edit.return_value=SimpleNamespace(data=[SimpleNamespace(b64_json=generated_png_b64())])
    expected=generate_chs_roadmap('Nurse Practitioner',12,client=fake_client(plan('Nurse Practitioner',12)))
    with patch.object(application,'portrait_gate',return_value=(True,'')),patch.object(application,'rate_limited',return_value=False),patch.object(application,'OpenAI',image_client),patch.object(application,'load_key',return_value='sk-test'),patch.object(application,'generate_chs_roadmap',return_value=expected,side_effect=None if success else RoadmapUnavailable('Unavailable')):
        r=browser.post('/api/chs/generate',data=dict(career='Nurse Practitioner',grade='12',age='25',path='explore',priority='Doing work I enjoy',photo_consent='confirmed',privacy_ack='acknowledged',_csrf_token='chs-test',photo=(io.BytesIO(base64.b64decode(generated_png_b64())),'test.png')))
    if success:
        assert r.status_code==200 and r.json['chs']==expected['chs'] and r.json['steps']==expected['steps']
        image_client.return_value.images.edit.assert_called_once()
    else:
        assert r.status_code==503
        image_client.assert_not_called()
        with browser.session_transaction() as s:assert s.get('generation_count',0)==0


def test_sdk_http_serialization_and_response_parsing():
    # Real installed SDK + real serialized HTTP, with a transport stub rather than paid calls.
    from openai import OpenAI,DefaultHttpxClient
    try:
        import httpx2
    except ImportError:
        import httpx as httpx2
    captured=[]
    outputs=[plan(),{'approved':True,'issues':[]}]
    def handle(request):
        body=json.loads(request.content);captured.append(body)
        result=outputs[len(captured)-1]
        return httpx2.Response(200,json={'id':'resp_test','object':'response','created_at':0,'model':'gpt-4.1','status':'completed','output':[{'id':'msg_test','type':'message','role':'assistant','status':'completed','content':[{'type':'output_text','text':json.dumps(result),'annotations':[]}]}]})
    client=OpenAI(api_key='sk-test',http_client=DefaultHttpxClient(transport=httpx2.MockTransport(handle)))
    result=generate_chs_roadmap('Neurosurgeon',9,client=client)
    assert result['chs']['engine']=='catalog-grounded-ai-v1'
    assert len(captured)==2 and all(b['store'] is False for b in captured)
    assert captured[0]['text']['format']['schema']==PLAN_SCHEMA
    assert captured[1]['text']['format']['schema']==REVIEW_SCHEMA
    client.close()
