"""Independent, read-only career exploration demo. No student data or AI calls."""
import json
from copy import deepcopy
from pathlib import Path
from flask import Blueprint, render_template, redirect, url_for
from bhs_catalog import COURSES

airforce_demo = Blueprint('airforce_demo', __name__)
BASE = Path(__file__).resolve().parent

def demo_data():
    catalog = deepcopy(COURSES)
    supplement = json.loads((BASE / 'data/army_catalog_supplement.json').read_text())['bhs']
    for key, updates in supplement.items():
        catalog.setdefault(key, {}).update(updates)
    roles = json.loads((BASE / 'data/airforce_careers.json').read_text())
    # Equivalent occupations share a school foundation across branch demos.
    # Branch-specific descriptions, training and eligibility remain on each role.
    profiles = json.loads((BASE / 'data/army_school_profiles.json').read_text())['profiles']
    for role in roles:
        if role.get('school_profile'):
            profile = profiles[role['school_profile']]
            role['courses'] = [{'key': key, 'why': role['course_notes'][key]}
                               for key in profile['bhs']]
    used = {course['key'] for role in roles for course in role['courses']}
    return {'roles': roles, 'courses': {key: dict(catalog[key], name=catalog[key].get('name', key)) for key in sorted(used)}, 'reviewed': 'September 23, 2026'}

@airforce_demo.get('/jetforce')
def explorer():
    return render_template('airforce.html', data=demo_data())


@airforce_demo.get('/airforce')
@airforce_demo.get('/af')
def legacy_explorer():
    return redirect(url_for('airforce_demo.explorer'), code=301)
