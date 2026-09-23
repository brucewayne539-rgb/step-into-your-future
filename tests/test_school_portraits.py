"""Exercise both image paths for all three schools without provider calls."""
import io
import unittest
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from PIL import Image

import app
from school_portraits import AVIATION, WORKPLACE


class SchoolPortraitTests(unittest.TestCase):
    def test_all_school_image_paths_receive_workplace_and_cockpit_guidance(self):
        for school in ('bhs', 'ghs', 'chs'):
            for demo in (True, False):
                with self.subTest(school=school, demo=demo):
                    client = app.app.test_client()
                    with client.session_transaction() as session:
                        session['demo_access'] = True
                        session['csrf_token'] = 'local-test'
                    fake = MagicMock()
                    fake.images.edit.return_value = SimpleNamespace(data=[SimpleNamespace(b64_json='mock')])
                    with ExitStack() as stack:
                        for name, value in [('admin_preview_gate', (True, 'Ready')),
                                            ('portrait_gate', (True, 'Ready')),
                                            ('rate_limited', False), ('load_key', 'local-test'),
                                            ('burn_portrait_watermark', 'mock'), ('OpenAI', fake)]:
                            stack.enter_context(patch.object(app, name, return_value=value))
                        fields = {'career': 'Automotive Technician', 'grade': '9', 'age': '35',
                                  'path': 'explore', 'priority': 'Doing work I enjoy'}
                        headers = {'X-CSRF-Token': 'local-test'}
                        if demo:
                            response = client.post('/api/admin-preview/generate', headers=headers,
                                json=dict(fields, mode='standard', school=school, sample_id='grade9'))
                        else:
                            image = io.BytesIO()
                            Image.new('RGB', (32, 32), 'gray').save(image, format='PNG')
                            image.seek(0)
                            response = client.post('/api/generate' if school == 'bhs' else f'/api/{school}/generate',
                                headers=headers, data=dict(fields, photo=(image, 'test.png'),
                                photo_consent='confirmed', privacy_ack='acknowledged'))
                    self.assertEqual(response.status_code, 200, response.get_json())
                    prompt = fake.images.edit.call_args.kwargs['prompt']
                    self.assertIn(WORKPLACE, prompt)
                    self.assertIn(AVIATION, prompt)
                    self.assertIn('approximately age 35', prompt)
                    self.assertNotIn('Military career display:', prompt)
                    self.assertNotIn('flattering lighting', prompt)
                    self.assertEqual(fake.images.edit.call_count, 1)


if __name__ == '__main__':
    unittest.main()
