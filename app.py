from flask import Flask, request, jsonify
import re

app = Flask(__name__)

# Nutrition Database (kcal per 100g) - All singular names
NUTRITION_DB = {
    "rice": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3, "iron": "0.4mg"},
    "brown rice": {"calories": 111, "protein": 2.6, "carbs": 23, "fat": 0.9, "magnesium": "43mg"},
    "egg": {"calories": 143, "protein": 13, "carbs": 0.7, "fat": 9.5, "vitaminD": "1.1mcg"},
    "chicken breast": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6, "niacin": "14.8mg"},
    "almond": {"calories": 579, "protein": 21, "carbs": 22, "fat": 50, "vitaminE": "25.6mg"},
    "spinach": {"calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4, "vitaminK": "483mcg"},
    "milk": {"calories": 42, "protein": 3.4, "carbs": 4.8, "fat": 1, "calcium": "125mg"}
}

# Unit conversion factors (to grams)
UNIT_CONVERSION = {
    "cup": 240, "tbsp": 15, "tsp": 5, "piece": 50, "egg": 50
}

def parse_ingredient(ingredient):
    """Convert '2 cups rice' or '100g rice' to {'name': 'rice', 'grams': ...}"""
    try:
        ingredient = ingredient.lower().strip()

        # Handle eggs separately
        if "egg" in ingredient:
            qty = float(re.search(r'(\d+)', ingredient).group(1))
            return {"name": "egg", "grams": qty * UNIT_CONVERSION["egg"]}

        # Match quantity, unit, name
        match = re.match(r"(\d+(?:\.\d+)?)\s*([a-zA-Z]+)\s+(.+)", ingredient)
        if not match:
            return None

        quantity, unit, name = match.groups()
        quantity = float(quantity)
        unit = unit.rstrip('s')
        name = name.rstrip('s')

        if unit in ["g", "gram"]:
            grams = quantity
        else:
            if unit == "tablespoon":
                unit = "tbsp"
            if unit == "teaspoon":
                unit = "tsp"
            grams = quantity * UNIT_CONVERSION.get(unit, 100)

        return {"name": name.strip(), "grams": grams}
    except:
        return None

@app.route('/analyze-nutrition', methods=['POST'])
def analyze_nutrition():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    if "ingredients" not in data or not isinstance(data["ingredients"], list):
        return jsonify({"error": "Ingredients must be an array"}), 400
    
    ingredients = data["ingredients"]
    total = {
        "calories": 0,
        "macronutrients": {"protein": 0, "carbs": 0, "fat": 0},
        "micronutrients": {},
        "ingredients_parsed": [],
        "skipped_ingredients": []
    }
    
    for item in ingredients:
        if not isinstance(item, str):
            total["skipped_ingredients"].append(item)
            continue
            
        parsed = parse_ingredient(item)
        if not parsed:
            total["skipped_ingredients"].append(item)
            continue
            
        if parsed["name"] not in NUTRITION_DB:
            total["skipped_ingredients"].append(item)
            continue
            
        food = NUTRITION_DB[parsed["name"]]
        weight_factor = parsed["grams"] / 100
        
        # Macros
        for macro in total["macronutrients"]:
            total["macronutrients"][macro] = round(
                total["macronutrients"][macro] + food[macro] * weight_factor, 2
            )
        
        # Micros
        for micro, val in food.items():
            if micro not in ["calories", "protein", "carbs", "fat"]:
                if micro in total["micronutrients"]:
                    amount = float(''.join(filter(str.isdigit, val))) * weight_factor
                    unit = ''.join(filter(str.isalpha, val))
                    total["micronutrients"][micro] = f"{amount:.1f}{unit}"
                else:
                    total["micronutrients"][micro] = val
        
        total["calories"] = round(total["calories"] + food["calories"] * weight_factor, 2)
        total["ingredients_parsed"].append({
            "input": item,
            "parsed": parsed,
            "calories": round(food["calories"] * weight_factor, 2)
        })
    
    return jsonify(total)

@app.route('/')
def home():
    return "Nutrition Microservice is running! Send POST requests to /analyze-nutrition"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
