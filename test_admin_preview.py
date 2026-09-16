import base64
import io
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image

import app as application


def generated_png_b64():
    image = Image.new("RGB", (512, 768), (75, 105, 125))
    output = io.BytesIO()
    image.save(output, format="PNG")
    return base64.b64encode(output.getvalue()).decode("ascii")


class FakeOpenAIClient:
    def __init__(self, *args, **kwargs):
        self.images = SimpleNamespace(edit=self.edit)

    @staticmethod
    def edit(**kwargs):
        assert kwargs["model"] == "gpt-image-2"
        assert kwargs["image"].name == "fictional-demo-student.png"
        return SimpleNamespace(data=[SimpleNamespace(b64_json=generated_png_b64())])


class AdministratorPreviewTests(unittest.TestCase):
    def setUp(self):
        application.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
        self.client = application.app.test_client()

    def authorize(self):
        with self.client.session_transaction() as session:
            session["demo_access"] = True
            session["csrf_token"] = "test-csrf"
            session["admin_preview_count"] = 0

    def test_fictional_source_assets_are_available(self):
        for sample in ("grade9", "grade11"):
            response = self.client.get(f"/demo-student/{sample}.png")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.mimetype, "image/png")
            self.assertGreater(len(response.data), 100_000)
            response.close()

    @patch.object(application, "load_key", return_value="sk-test")
    @patch.object(application, "OpenAI", FakeOpenAIClient)
    def test_preview_page_has_no_upload_control(self, _key):
        self.authorize()
        response = self.client.get("/admin-preview?school=bhs")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Fictional Sample Student", response.data)
        self.assertNotIn(b'type="file"', response.data)
        response.close()

    @patch.object(application, "load_key", return_value="sk-test")
    @patch.object(application, "OpenAI", FakeOpenAIClient)
    def test_live_fictional_preview_returns_watermarked_result(self, _key):
        self.authorize()
        response = self.client.post(
            "/api/admin-preview/generate",
            headers={"X-CSRF-Token": "test-csrf"},
            json={
                "school": "bhs",
                "sample_id": "grade9",
                "career": "Firefighter",
                "age": "28",
                "path": "employee",
                "priority": "Helping people",
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["ok"])
        self.assertTrue(data["fictional_demo"])
        self.assertEqual(data["grade"], "9")
        self.assertEqual(data["career"], "Firefighter")
        self.assertEqual(data["generations_left"], application.MAX_ADMIN_PREVIEW_GENERATIONS - 1)
        self.assertTrue(data["image"].startswith("data:image/png;base64,"))
        self.assertIn("course_details", data["bhs"])


if __name__ == "__main__":
    unittest.main()
