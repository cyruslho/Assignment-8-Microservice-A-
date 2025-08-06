import requests
import unittest

class TestNutritionMicroservice(unittest.TestCase):
    BASE_URL = "http://localhost:5000"
    
    def test_basic_input(self):
        response = requests.post(
            f"{self.BASE_URL}/analyze-nutrition",
            json={"ingredients": ["1 cup rice", "2 eggs"]}
        )
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(data["calories"], 455.0, delta=0.1)  # 312 + 143
        self.assertAlmostEqual(data["macronutrients"]["protein"], 19.48, delta=0.1)
        self.assertEqual(len(data["ingredients_parsed"]), 2)
    
    def test_mixed_units(self):
        response = requests.post(
            f"{self.BASE_URL}/analyze-nutrition",
            json={"ingredients": ["100g chicken breast", "1 tbsp almond"]}
        )
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(data["macronutrients"]["protein"], 34.15, delta=0.1)
        self.assertAlmostEqual(data["calories"], 251.85, delta=0.1)
    
    def test_invalid_input(self):
        response = requests.post(
            f"{self.BASE_URL}/analyze-nutrition",
            json={"ingredients": ["invalid", 123, ""]}
        )
        data = response.json()
        self.assertEqual(len(data["skipped_ingredients"]), 3)

if __name__ == '__main__':
    unittest.main()
