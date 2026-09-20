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

    def test_school_explorers_are_public_but_admin_preview_is_protected(self):
        with patch.object(application, "ACCESS_CODE", "test-demo-code"):
            bhs = self.client.get("/")
            self.assertEqual(bhs.status_code, 200)
            self.assertIn(b"How would you like to explore?", bhs.data)
            self.assertNotIn(b"Administrator Preview Access", bhs.data)

            ghs = self.client.get("/ghs")
            self.assertEqual(ghs.status_code, 200)
            self.assertIn(b"How would you like to explore?", ghs.data)
            self.assertNotIn(b"Administrator Preview Access", ghs.data)

            protected = self.client.get("/admin-preview?school=bhs")
            self.assertEqual(protected.status_code, 200)
            self.assertIn(b'name="access_code"', protected.data)
            self.assertIn(b'action="/login"', protected.data)
            self.assertNotIn(b"Fictional Sample Student", protected.data)

    def test_access_code_returns_to_requested_admin_preview(self):
        with patch.object(application, "ACCESS_CODE", "test-demo-code"):
            self.client.get("/admin-preview?school=bhs")
            with self.client.session_transaction() as session:
                token = session["csrf_token"]
            response = self.client.post(
                "/login",
                data={"_csrf_token": token, "access_code": "test-demo-code"},
            )
            self.assertEqual(response.status_code, 302)
            self.assertIn("/admin-preview?school=bhs", response.headers["Location"])

    def test_pilot_simulation_routes_are_protected_and_return_to_requested_school(self):
        with patch.object(application, "ACCESS_CODE", "test-demo-code"):
            protected = self.client.get("/chs/pilot-demo")
            self.assertEqual(protected.status_code, 200)
            self.assertIn(b'name="access_code"', protected.data)
            with self.client.session_transaction() as session:
                token = session["csrf_token"]
            response = self.client.post(
                "/login",
                data={"_csrf_token": token, "access_code": "test-demo-code"},
            )
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.headers["Location"].endswith("/chs/pilot-demo"))

    @patch.object(application, "load_key", return_value="sk-test")
    @patch.object(application, "OpenAI", FakeOpenAIClient)
    def test_each_pilot_simulation_uses_normal_student_flow_and_fake_photo_substitution(self, _key):
        self.authorize()
        for path, school_name in (
            ("/pilot-demo", b"Branford High School"),
            ("/ghs/pilot-demo", b"Guilford High School"),
            ("/chs/pilot-demo", b"Cumberland High School"),
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIn(school_name, response.data)
                self.assertIn(b"Student Career Explorer", response.data)
                self.assertIn(b'type="file"', response.data)
                self.assertIn(b"your selected file never leaves this browser", response.data)
                self.assertIn(b"FICTIONAL AI DEMONSTRATION", response.data)
                self.assertNotIn(b"Choose a fictional student.", response.data)
                response.close()

    def test_armie_pilot_simulation_returns_after_access_code(self):
        with patch.object(application, "ACCESS_CODE", "test-demo-code"):
            protected = self.client.get("/armie/pilot-demo")
            self.assertEqual(protected.status_code, 200)
            self.assertIn(b'name="access_code"', protected.data)
            with self.client.session_transaction() as session:
                token = session["csrf_token"]
            response = self.client.post(
                "/login",
                data={"_csrf_token": token, "access_code": "test-demo-code"},
            )
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.headers["Location"].endswith("/armie/pilot-demo"))

    @patch.object(application, "load_key", return_value="sk-test")
    @patch.object(application, "OpenAI", FakeOpenAIClient)
    def test_armie_pilot_simulation_has_photo_step_and_army_career_choices(self, _key):
        self.authorize()
        response = self.client.get("/armie/pilot-demo")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Student Career Explorer", response.data)
        self.assertIn(b'type="file"', response.data)
        self.assertIn(b"Cyber Operations Specialist", response.data)
        self.assertIn(b"Branford High School", response.data)
        self.assertIn(b"Guilford High School", response.data)
        self.assertIn(b"your selected file never leaves this browser", response.data)
        self.assertNotIn(b"Choose a fictional student and school", response.data)
        response.close()

    def test_no_photo_roadmap_does_not_require_access_code(self):
        with patch.object(application, "ACCESS_CODE", "test-demo-code"), \
             patch.object(application, "rate_limited", return_value=False):
            with self.client.session_transaction() as session:
                session["csrf_token"] = "test-csrf"
                session.pop("demo_access", None)
            response = self.client.post(
                "/api/roadmap",
                headers={"X-CSRF-Token": "test-csrf"},
                json={
                    "career": "Architect",
                    "grade": "9",
                    "path": "explore",
                    "priority": "Creativity",
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.get_json()["ok"])

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

    @patch.object(application, "load_key", return_value="sk-test")
    @patch.object(application, "OpenAI", FakeOpenAIClient)
    def test_ghs_preview_returns_school_courses_and_programs(self, _key):
        self.authorize()
        response = self.client.post(
            "/api/admin-preview/generate",
            headers={"X-CSRF-Token": "test-csrf"},
            json={
                "school": "ghs",
                "sample_id": "grade11",
                "career": "Architect",
                "age": "30",
                "path": "employee",
                "priority": "Creativity",
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["school"], "GHS")
        self.assertTrue(data["ghs"]["primary_course_details"])
        self.assertTrue(data["ghs"]["supporting_course_details"])
        self.assertTrue(data["ghs"]["programs"])
        self.assertIn("counselor", data["ghs"]["next"].lower())

    def test_all_ghs_preview_pathways_have_school_specific_results(self):
        for career in application.GHS_CAREERS:
            for grade in application.BHS_GRADE_LABELS:
                for path in ("employee", "owner", "explore"):
                    result = application.ghs_for_grade(career, grade, path)
                    self.assertTrue(result["primary_course_details"] or result["future_course_details"])
                    self.assertTrue(result["programs"])
                    self.assertTrue(result["experience"])
                    self.assertTrue(result["next"])

    @patch.object(application, "load_key", return_value="sk-test")
    @patch.object(application, "OpenAI", FakeOpenAIClient)
    def test_armie_page_has_army_branding_and_no_upload(self, _key):
        self.authorize()
        response = self.client.get("/armie")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"MEET <span>ARMIE</span>", response.data)
        self.assertIn(b"Cyber Operations Specialist", response.data)
        self.assertIn(b"Branford High School", response.data)
        self.assertIn(b"Guilford High School", response.data)
        self.assertNotIn(b'type="file"', response.data)

    def test_every_armie_career_maps_to_both_school_catalogs(self):
        for career, info in application.ARMY_CAREERS.items():
            with self.subTest(career=career):
                school_match = info["school_match"]
                self.assertIn(school_match, application.CAREERS)
                self.assertIn(school_match, application.GHS_CAREERS)

    @patch.object(application, "load_key", return_value="sk-test")
    @patch.object(application, "OpenAI", FakeOpenAIClient)
    def test_armie_live_preview_returns_grade_specific_bhs_path(self, _key):
        self.authorize()
        response = self.client.post(
            "/api/admin-preview/generate",
            headers={"X-CSRF-Token": "test-csrf"},
            json={
                "mode": "army",
                "school": "bhs",
                "sample_id": "grade9",
                "grade": "12",
                "career": "Cyber Operations Specialist",
                "age": "25",
                "path": "employee",
                "priority": "Technology and cyber",
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["mode"], "army")
        self.assertEqual(data["grade"], "12")
        self.assertEqual(data["career"], "Cyber Operations Specialist")
        self.assertIn("current 12th", data["bhs"]["grade_note"])
        self.assertIn("Cyber", data["keys"])


if __name__ == "__main__":
    unittest.main()
