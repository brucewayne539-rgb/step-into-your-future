"""Independent, read-only career exploration demo. No student data or AI calls."""
import json
from copy import deepcopy
from pathlib import Path
from flask import Blueprint, render_template
from bhs_catalog import COURSES

airforce_demo = Blueprint('airforce_demo', __name__)
BASE = Path(__file__).resolve().parent

def demo_data():
    catalog = deepcopy(COURSES)
    supplement = json.loads((BASE / 'data/army_catalog_supplement.json').read_text())['bhs']
    for key, updates in supplement.items():
        catalog.setdefault(key, {}).update(updates)
    roles = json.loads((BASE / 'data/airforce_careers.json').read_text())
    used = {course['key'] for role in roles for course in role['courses']}
    return {'roles': roles, 'courses': {key: dict(catalog[key], name=catalog[key].get('name', key)) for key in sorted(used)}, 'reviewed': 'September 23, 2026'}

@airforce_demo.get('/airforce')
@airforce_demo.get('/af')
def explorer():
    return render_template('airforce.html', data=demo_data())
