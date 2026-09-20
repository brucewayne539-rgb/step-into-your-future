"""Regressions from actual test-service failures; model behavior still needs live review."""
import copy
import json
from pathlib import Path

import jsonschema
import pytest

from chs_catalog import SELECTABLE, RoadmapValidationError
from chs_roadmap import (plan_schema, resolve_evidence, validate_plan,
                        review_issues, REVIEW_CRITERIA, generate_chs_roadmap)
from chs_fixtures import plan, model_draft, review_result


@pytest.mark.parametrize('grade', range(8,13))
def test_generation_contract_restricts_every_course_to_actual_remaining_grades(grade):
    schema=plan_schema('Nurse Practitioner',grade)
    jsonschema.Draft202012Validator.check_schema(schema)
    choice_schema={'$defs':schema['$defs'],'$ref':'#/$defs/course_option'}
    validator=jsonschema.Draft202012Validator(choice_schema)
    for cid,course in SELECTABLE.items():
        for year in range(8,14):
            choice=dict(course_id=cid,planned_grade=year,
                        why='A complete explanation of the occupational skill and its relevance.',
                        evidence=cid+':E1')
            expected=year>=max(9,grade) and year in course['grades']
            assert validator.is_valid(choice)==expected, (cid,grade,year)


@pytest.mark.parametrize('career',['Neurosurgeon','Nurse Practitioner','Cybersecurity Specialist'])
@pytest.mark.parametrize('grade',range(8,13))
def test_known_feasible_grade_plans_fit_generation_contract(career,grade):
    draft=model_draft(plan(career,grade))
    jsonschema.validate(draft,plan_schema(career,grade))
    resolved=resolve_evidence(draft)
    validate_plan(resolved,career,grade)


def test_third_supporting_elective_is_not_in_generation_contract():
    draft=model_draft(plan())
    option=copy.deepcopy(draft['foundation_selections'][0])
    draft['supporting_selections']=[option,copy.deepcopy(option),copy.deepcopy(option)]
    errors=list(jsonschema.Draft202012Validator(plan_schema('Neurosurgeon',9)).iter_errors(draft))
    assert any(e.validator=='maxItems' and list(e.path)==['supporting_selections'] for e in errors)


def test_actual_live_midword_summary_cannot_be_returned_again():
    actual=json.loads((Path(__file__).parent/'fixtures/cyber_grade9_live_rejected.json').read_text())
    assert actual['summary'].endswith('entry-l')
    candidate=plan('Cybersecurity Specialist',9)
    candidate['summary']=actual['summary']
    with pytest.raises(RoadmapValidationError,match='unfinished sentence'):
        validate_plan(candidate,'Cybersecurity Specialist',9)


@pytest.mark.parametrize('criterion',REVIEW_CRITERIA)
def test_overall_approval_cannot_override_a_failed_review_criterion(criterion):
    review=review_result()
    review['checks'][criterion]={'finding':'AP course lacks optional readiness and placement conditions.', 'passed':False}
    issues=review_issues(review)
    assert len(issues)==1 and issues[0].startswith(criterion+':')


def test_missing_criterion_does_not_count_as_educational_review():
    review=review_result()
    del review['checks']['source_support']
    with pytest.raises(RoadmapValidationError):
        review_issues(review)


def test_new_model_contract_reaches_review_and_existing_student_result():
    from types import SimpleNamespace
    from unittest.mock import MagicMock
    client=MagicMock()
    draft=model_draft(plan('Nurse Practitioner',11))
    client.responses.create.side_effect=[
        SimpleNamespace(status='completed',output_text=json.dumps(draft)),
        SimpleNamespace(status='completed',output_text=json.dumps(review_result()))]
    result=generate_chs_roadmap('Nurse Practitioner',11,client=client)
    review_payload=json.loads(client.responses.create.call_args_list[1].kwargs['input'])
    assert 'selections' in review_payload['proposed_plan']
    assert 'direct_selections' not in review_payload['proposed_plan']
    cards=sum([result['chs'][k] for k in ('primary_course_details','supporting_course_details','future_course_details')],[])
    assert len(cards)==len(plan('Nurse Practitioner',11)['selections'])
    assert all(card['planned_grade']>=11 for card in cards)
