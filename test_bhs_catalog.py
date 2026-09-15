import unittest

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
        priorities = "Doing work I enjoy"
        for career in app.CAREERS:
            for grade in map(str, range(8, 13)):
                for path in ("employee", "owner", "explore"):
                    response = client.post("/api/roadmap", json={
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


if __name__ == "__main__":
    unittest.main()
