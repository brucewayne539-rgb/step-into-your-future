"""Equivalent BHS ATC roles must keep the same preparation choices."""
import unittest
import app
from airforce_demo import demo_data
from army_school_pathways import school_pathway


def check_atc_school_connections_agree(grade):
    data = demo_data()
    role = next(role for role in data['roles'] if role['id'] == 'atc')
    assert {'Statistics & Probability', 'Algebra I', 'Exploration of Computer Science'} <= {
        course['key'] for course in role['courses']}
    army = school_pathway('Air Traffic Control (ATC) Operator', grade, 'bhs',
                          app.ARMY_SCHOOL_CATALOGS, app.BHS_PROGRAMS)
    current, future = [], []
    for course in role['courses']:
        key = course['key']
        record = data['courses'][key]
        assert course['why']
        source = app.ARMY_SCHOOL_CATALOGS['bhs'][key]
        assert record['grades'] == source['grades']
        assert record.get('prerequisite', '') == source.get('prerequisite', '')
        if grade in record['grades']:
            current.append(key)
        elif any(g > grade for g in record['grades']):
            future.append(key)
    assert current == [c['id'] for c in army['primary_course_details'] + army['supporting_course_details']]
    assert future == [c['id'] for c in army['future_course_details']]


class CrossBranchAtcTests(unittest.TestCase):
    def test_all_grades(self):
        for grade in range(8, 13):
            with self.subTest(grade=grade):
                check_atc_school_connections_agree(grade)
