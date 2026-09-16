import unittest
from unittest.mock import patch

import app
from bhs_catalog import CAREER_COURSES, COURSES


class BHSCatalogTests(unittest.TestCase):
    def test_every_career_has_ranked_catalog_mapping(self):
        self.assertEqual(set(app.CAREERS), set(CAREER_COURSES))
        for career, mapping in CAREER_COURSES.items():
            self.assertGreaterEqual(len(mapping["direct"]), 3, career)
            self.assertGreaterEqual(len(mapping["support"]), 3, career)
            self.assertEqual(len(mapping["direct"]), len(set(mapping["direct"])), career)
            self.assertFalse(set(mapping["direct"]) & set(mapping["support"]), career)
            for name in mapping["direct"] + mapping["support"]:
                self.assertIn(name, COURSES, (career, name))

    def test_all_grade_and_path_results_are_complete_and_grade_safe(self):
        for career in app.CAREERS:
            for grade in range(8, 13):
                for path in ("employee", "owner", "explore"):
                    result = app.bhs_for_grade(career, str(grade), path)
                    names = result["courses"] + result["supporting_courses"] + result["future_courses"]
                    self.assertEqual(len(names), len(set(names)), (career, grade, path))
                    self.assertTrue(result["future_courses"] if grade == 8 else result["courses"], (career, grade, path))
                    for item in result["course_details"] + result["supporting_course_details"]:
                        self.assertIn(grade, COURSES[item["name"]]["grades"], (career, grade, item["name"]))
                    for item in result["future_course_details"]:
                        self.assertTrue(any(g > grade for g in COURSES[item["name"]]["grades"]), (career, grade, item["name"]))
                    self.assertTrue(result["programs"], (career, grade))
                    self.assertIn("counselor", result["next"].lower(), (career, grade))

    def test_roadmap_api_all_combinations(self):
        client = app.app.test_client()
        with client.session_transaction() as state:
            state["csrf_token"] = "test-csrf-token"
        priorities = "Doing work I enjoy"
        with patch.object(app, "rate_limited", return_value=False):
            for career in app.CAREERS:
                for grade in map(str, range(8, 13)):
                    for path in ("employee", "owner", "explore"):
                        response = client.post("/api/roadmap", headers={"X-CSRF-Token": "test-csrf-token"}, json={
                            "career": career,
                            "grade": grade,
                            "path": path,
                            "priority": priorities,
                        })
                        self.assertEqual(response.status_code, 200, (career, grade, path, response.get_data(as_text=True)))
                        data = response.get_json()
                        self.assertTrue(data["ok"])
                        self.assertEqual(data["school"], "BHS")
                        self.assertIn("course_details", data["bhs"])

    def test_mutating_api_rejects_missing_csrf(self):
        client = app.app.test_client()
        response = client.post("/api/roadmap", json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("expired", response.get_json()["error"])

    def test_roadmap_is_photo_free_and_security_headers_are_present(self):
        client = app.app.test_client()
        with client.session_transaction() as state:
            state["csrf_token"] = "test-csrf-token"
        response = client.post("/api/roadmap", headers={"X-CSRF-Token": "test-csrf-token"}, json={
            "career": "Architect", "grade": "8", "path": "explore", "priority": "Creativity"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.get_json()["image"])
        self.assertEqual(response.headers["Cache-Control"], "no-store, max-age=0")
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        self.assertIn("camera=()", response.headers["Permissions-Policy"])

    def test_hosted_portraits_fail_closed_without_evidence_flags(self):
        with patch.multiple(app, HOSTED=True, PORTRAITS_ENABLED=True, SECRET_KEY_CONFIGURED=True,
                            ACCESS_CODE="teacher", OPENAI_ZDR_CONFIRMED=False,
                            SCHOOL_PORTRAIT_APPROVED=True, PRIVACY_CONTACT_EMAIL="privacy@example.org"):
            enabled, reason = app.portrait_gate()
        self.assertFalse(enabled)
        self.assertIn("Zero Data Retention", reason)

    def test_status_exposes_no_credentials(self):
        client = app.app.test_client()
        response = client.get("/api/ghs/status")
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True).lower()
        self.assertNotIn("api_key", body)
        self.assertNotIn("secret_key", body)


if __name__ == "__main__":
    unittest.main()
