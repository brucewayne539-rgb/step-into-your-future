"""Contract and adversarial recovery tests; these are not live AI evaluations."""
import copy
import json
import re
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from chs_catalog import SELECTABLE, normalized
from chs_roadmap import (source_passages, resolve_evidence, validate_plan,
                        generate_chs_roadmap, RoadmapUnavailable, PLAN_SCHEMA)
from chs_fixtures import plan


def client_for(*outputs):
    client = MagicMock()
    client.responses.create.side_effect = [
        SimpleNamespace(status='completed', output_text=json.dumps(x))
        for x in outputs
    ]
    return client


def cited_plan():
    result = plan()
    for item in result['selections']:
        item['evidence'] = item['course_id'] + ':E1'
    return result


def test_passages_preserve_every_catalog_description_and_exact_source():
    for course in SELECTABLE.values():
        passages = source_passages(course)
        assert normalized(' '.join(passages.values())) == normalized(course['description'])
        for quote in passages.values():
            assert len(quote.strip()) >= 18
            assert normalized(quote) in normalized(course['description'])


def test_citations_expand_without_mutating_model_plan_and_reviewer_sees_source():
    candidate = cited_plan()
    original = copy.deepcopy(candidate)
    client = client_for(candidate, dict(approved=True, issues=[]))
    result = generate_chs_roadmap('Neurosurgeon', 9, client=client)
    assert candidate == original
    review_input = json.loads(client.responses.create.call_args_list[1].kwargs['input'])
    reviewed = review_input['proposed_plan']
    validate_plan(reviewed, 'Neurosurgeon', 9)
    for selected in reviewed['selections']:
        assert selected['evidence'] == source_passages(SELECTABLE[selected['course_id']])[selected['course_id']+':E1']
    for cards in ('primary_course_details', 'supporting_course_details', 'future_course_details'):
        for card in result['chs'][cards]:
            assert card['evidence'] in SELECTABLE[card['course_id']]['description']


@pytest.mark.parametrize('evidence', ['CHS-131:E1', 'CHS-048:E999999', 'Invented catalog evidence'])
def test_false_citations_remain_blocked_after_one_correction(evidence):
    bad = cited_plan()
    bad['selections'][0]['evidence'] = evidence
    client = client_for(bad, bad)
    with pytest.raises(RoadmapUnavailable, match='CHS-EVIDENCE'):
        generate_chs_roadmap('Neurosurgeon', 9, client=client)
    assert client.responses.create.call_count == 2


def test_invalid_first_draft_can_be_corrected_but_must_receive_review():
    bad = cited_plan()
    bad['summary'] = 'Too short'
    good = cited_plan()
    client = client_for(bad, good, dict(approved=True, issues=[]))
    result = generate_chs_roadmap('Neurosurgeon', 9, client=client)
    assert result['summary'] == good['summary']
    assert client.responses.create.call_count == 3
    correction = json.loads(client.responses.create.call_args_list[1].kwargs['input'])
    assert correction['correction_required'] == ['Missing or excessive roadmap prose: summary']


def test_semantic_correction_requires_new_review_not_first_approval():
    good = cited_plan()
    client = client_for(good, dict(approved=False, issues=['Clarify readiness.']),
                        good, dict(approved=True, issues=[]))
    generate_chs_roadmap('Neurosurgeon', 9, client=client)
    assert client.responses.create.call_count == 4
    correction = json.loads(client.responses.create.call_args_list[2].kwargs['input'])
    assert correction['correction_required'] == ['Clarify readiness.']
    assert client.responses.create.call_args_list[3].kwargs['text']['format']['name'] == 'chs_career_review'


def test_repair_cannot_bypass_grade_rules():
    first = cited_plan()
    repaired = copy.deepcopy(first)
    repaired['selections'][0]['planned_grade'] = 8
    client = client_for(first, dict(approved=False, issues=['Clarify readiness.']), repaired)
    with pytest.raises(RoadmapUnavailable, match='CHS-GRADE'):
        generate_chs_roadmap('Neurosurgeon', 9, client=client)
    assert client.responses.create.call_count == 3


def test_provider_errors_are_not_retried_or_exposed(caplog):
    client = MagicMock()
    error = RuntimeError('private-token-SENTINEL')
    error.status_code = 429
    client.responses.create.side_effect = error
    with pytest.raises(RoadmapUnavailable, match='CHS-RATE') as caught:
        generate_chs_roadmap('Neurosurgeon', 9, client=client)
    assert client.responses.create.call_count == 1
    assert 'SENTINEL' not in str(caught.value) + caplog.text


@pytest.mark.parametrize('field,minimum,maximum', [
    ('summary',45,700),('experience',40,700),('next_step',30,600),
    ('reflection',15,300),('caveat',20,650)])
def test_generation_contract_enforces_prose_boundaries(field,minimum,maximum):
    pattern = PLAN_SCHEMA['properties'][field]['pattern']
    assert not re.fullmatch(pattern, 'x'*(minimum-1))
    assert re.fullmatch(pattern, 'x'*minimum)
    assert re.fullmatch(pattern, 'x'*maximum)
    assert not re.fullmatch(pattern, 'x'*(maximum+1))
