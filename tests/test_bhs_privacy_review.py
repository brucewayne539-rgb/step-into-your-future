"""Exercise the privacy boundary with hostile requests and a mocked AI provider."""
import io
import unittest
from pathlib import Path
from unittest.mock import patch

import app as application


class BHSPrivacyReviewTests(unittest.TestCase):
    def setUp(self):
        application.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
        application.RATE_BUCKETS.clear()
        self.client = application.app.test_client()
        with self.client.session_transaction() as state:
            state['csrf_token'] = 'privacy-test'
            state['demo_access'] = True
        self.headers = {'X-CSRF-Token': 'privacy-test'}
        self.selection = dict(career='Architect', grade='9', path='explore', priority='Creativity')

    def test_real_photo_requests_cannot_reach_decoder_or_provider_even_with_old_flags(self):
        with patch.multiple(application, PORTRAITS_ENABLED=True, OPENAI_ZDR_CONFIRMED=True,
                            SCHOOL_PORTRAIT_APPROVED=True), \
             patch.object(application, 'OpenAI') as provider, \
             patch.object(application.Image, 'open') as decoder:
            for endpoint in ('/api/generate', '/api/bhs/generate', '/api/ghs/generate', '/api/chs/generate'):
                with self.subTest(endpoint=endpoint):
                    response = self.client.post(endpoint, data={'photo': (io.BytesIO(b'not-an-image'), 'student.png')})
                    self.assertEqual(response.status_code, 403)
            provider.assert_not_called()
            decoder.assert_not_called()

    def test_roadmaps_reject_extra_student_data_and_file_uploads(self):
        for field in ('name', 'student_id', 'prompt', 'photo', 'image', 'transcript', 'age'):
            response = self.client.post('/api/bhs/roadmap', headers=self.headers,
                                        json={**self.selection, field: 'must-not-be-accepted'})
            self.assertEqual(response.status_code, 400, field)
        response = self.client.post('/api/bhs/roadmap', headers=self.headers,
                                    data={'photo': (io.BytesIO(b'photo'), 'student.png')})
        self.assertEqual(response.status_code, 400)

    def test_roadmaps_never_call_ai_or_persist_choices_in_session(self):
        with patch.object(application, 'OpenAI') as provider:
            response = self.client.post('/api/bhs/roadmap', headers=self.headers, json=self.selection)
            self.assertEqual(response.status_code, 200)
            self.assertIsNone(response.json['image'])
            provider.assert_not_called()
        with self.client.session_transaction() as state:
            for field in self.selection:
                self.assertNotIn(field, state)

    def test_bhs_pages_and_legacy_preview_have_no_photo_input_or_analytics(self):
        for endpoint in ('/', '/bhs', '/bhs/', '/admin-preview?school=bhs', '/pilot-demo', '/bhs/privacy', '/bhs/school-review'):
            response = self.client.get(endpoint, follow_redirects=True)
            self.assertEqual(response.status_code, 200, endpoint)
            html = response.get_data(as_text=True)
            self.assertNotIn('type="file"', html, endpoint)
            self.assertNotIn('googletagmanager.com', html)
            self.assertNotIn('google-analytics.com', html)
            csp = response.headers['Content-Security-Policy']
            self.assertIn("connect-src 'self';", csp)
            self.assertNotIn('https:', csp)

    def test_all_shipped_templates_exclude_google_tags(self):
        for path in Path(application.APP_DIR).rglob('*.html'):
            text = path.read_text()
            self.assertNotIn('googletagmanager.com', text, str(path))
            self.assertNotIn("gtag('config'", text, str(path))

    def test_preview_rejects_arbitrary_images_and_prompts(self):
        payload = dict(school='bhs', sample_id='grade9', career='Architect', age='25',
                       path='explore', priority='Creativity')
        with patch.object(application, 'admin_preview_gate', return_value=(True, 'Ready')), \
             patch.object(application, 'OpenAI') as provider:
            for extra in ({'photo': 'data:image/png;base64,AAAA'}, {'prompt': 'student record'},
                          {'image_url': 'https://example.org/student.png'}, {'sample_id': '../../student'},
                          {'sample_id': {'bad': 'type'}}):
                response = self.client.post('/api/admin-preview/generate', headers=self.headers,
                                            json={**payload, **extra})
                self.assertEqual(response.status_code, 400, extra)
            provider.assert_not_called()

    def test_hosted_cookie_flags_and_idle_security_record_expiry(self):
        before = application.app.config['SESSION_COOKIE_SECURE']
        application.app.config['SESSION_COOKIE_SECURE'] = True
        try:
            response = application.app.test_client().get('/bhs', base_url='https://school.example')
            cookie = response.headers['Set-Cookie']
            for flag in ('Secure', 'HttpOnly', 'SameSite=Lax'):
                self.assertIn(flag, cookie)
        finally:
            application.app.config['SESSION_COOKIE_SECURE'] = before
        with application.app.test_request_context('/bhs'):
            from collections import deque
            application.RATE_BUCKETS[('old', 'pseudonym')] = deque([1.0])
            with patch.object(application.time, 'monotonic', return_value=1000.0):
                application.rate_limited('new', 60, 600)
            self.assertNotIn(('old', 'pseudonym'), application.RATE_BUCKETS)


if __name__ == '__main__':
    unittest.main()
