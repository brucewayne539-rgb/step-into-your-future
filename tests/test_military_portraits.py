"""Check career coverage and the prompt actually sent by the protected route."""
import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import app
from military_portraits import COMMON, REVISION, portrait_guidance


class MilitaryPortraitTests(unittest.TestCase):
    def test_every_military_career_has_workplace_guidance(self):
        roles = json.loads((Path(app.APP_DIR) / 'data/airforce_careers.json').read_text())
        for mode, careers in [('army', app.ARMY_CAREERS), ('jetforce', [r['id'] for r in roles])]:
            for career in careers:
                with self.subTest(mode=mode, career=career):
                    guidance = portrait_guidance(mode, career)
                    self.assertIn(COMMON, guidance)
                    self.assertIn('Workplace detail:', guidance)

    def test_protected_route_sends_task_guidance_and_keeps_age(self):
        cases = [
            ('army', 'Wheeled Vehicle Mechanic', 'vehicle safely supported'),
            ('army', 'Culinary Specialist', 'hair restraint'),
            ('army', 'Air Traffic Control (ATC) Operator', 'control training console'),
            ('army', 'Practical Nursing Specialist', 'clinical training'),
            ('jetforce', 'propulsion', 'powered-down equipment'),
            ('jetforce', 'pilot', 'flight simulator'),
            ('jetforce', 'cyber', 'desk-only scene'),
        ]
        for mode, career, expected in cases:
            for age in ('22', '35'):
                with self.subTest(mode=mode, career=career, age=age):
                    client = app.app.test_client()
                    with client.session_transaction() as session:
                        session['demo_access'] = True
                        session['csrf_token'] = 'local-test'
                    fake = MagicMock()
                    fake.images.edit.return_value = SimpleNamespace(data=[SimpleNamespace(b64_json='mock')])
                    with patch.object(app, 'admin_preview_gate', return_value=(True, 'Ready')), \
                         patch.object(app, 'rate_limited', return_value=False), \
                         patch.object(app, 'OpenAI', return_value=fake), \
                         patch.object(app, 'load_key', return_value='local-test'), \
                         patch.object(app, 'burn_portrait_watermark', return_value='mock'):
                        response = client.post('/api/admin-preview/generate',
                            headers={'X-CSRF-Token': 'local-test'},
                            json={'mode': mode, 'school': 'bhs', 'sample_id': 'grade9',
                                  'career': career, 'age': age, 'grade': '9', 'path': 'explore',
                                  'priority': 'Hands-on mechanical work' if mode == 'army' else 'Doing work I enjoy'})
                    self.assertEqual(response.status_code, 200, response.get_json())
                    prompt = fake.images.edit.call_args.kwargs['prompt']
                    self.assertIn(COMMON, prompt)
                    self.assertIn(expected, prompt)
                    self.assertIn('approximately age ' + age, prompt)
                    self.assertIn('natural workplace lighting', prompt)
                    self.assertNotIn('flattering lighting', prompt)
                    if mode == 'jetforce':
                        self.assertIn('No military uniforms', prompt)
                    self.assertEqual(fake.images.edit.call_count, 1)

    def test_school_portraits_unchanged_and_revision_visible(self):
        self.assertEqual(portrait_guidance('standard', 'Engineer'), '')
        client = app.app.test_client()
        for path in ('/jetforce', '/armie/'):
            self.assertEqual(client.get(path).headers.get('X-Military-Portrait-Revision'), REVISION)


if __name__ == '__main__':
    unittest.main()
