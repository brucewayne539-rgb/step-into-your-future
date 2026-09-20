"""Render actual templates plus clearly labeled mocked test responses for DOM tests."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(root),str(root/'tests')]
import app
from chs_fixtures import plan
from test_chs_intelligence import fake_client
from chs_roadmap import generate_chs_roadmap
out=Path(sys.argv[1] if len(sys.argv)>1 else '.qa-chs');out.mkdir(exist_ok=True)
c=app.app.test_client();(out/'chs-rendered.html').write_bytes(c.get('/chs').data)
results=[]
for career in ['Neurosurgeon','Nurse Practitioner','Cybersecurity Specialist']:
    for grade in range(8,13):
        results.append(dict(ok=True,career=career,grade=str(grade),school='CHS',**generate_chs_roadmap(career,grade,client=fake_client(plan(career,grade)))))
(out/'ui-fixtures.json').write_text(json.dumps(results))
with c.session_transaction() as session:session['demo_access']=True
(out/'admin-rendered.html').write_bytes(c.get('/admin-preview?school=chs').data)
print('Mocked DOM test inputs written; no live AI requests.')
