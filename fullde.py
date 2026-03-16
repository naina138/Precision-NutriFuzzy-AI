import json
import os
import numpy as np
from fuzzywuzzy import process

# Function to load JSON data
def load_json_data(file_path):
    try:
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' not found."
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) or isinstance(data, dict) else "Error: Invalid JSON structure."
    except json.JSONDecodeError as e:
        return f"Error: Failed to parse JSON. {e}"

# Function for fuzzy matching
def get_best_match(user_input, choices):
    return process.extractOne(user_input, choices) if choices else (None, 0)

# Function to find disease in diet data
def find_disease(disease_input, diet_data):
    disease_names = [d["name"].strip().lower() for d in diet_data["diseases"]]
    
    # Exact match first
    matched_disease = next((d for d in diet_data["diseases"] if d["name"].strip().lower() == disease_input), None)
    if matched_disease:
        return matched_disease
    
    # Fuzzy match if no exact match found
    best_match, score = process.extractOne(disease_input, disease_names)
    if best_match and score > 70:
        return next(d for d in diet_data["diseases"] if d["name"].strip().lower() == best_match)
    
    return None

# Function to get diet from 4gpt.json (Disease-specific diet recommendations)
def get_diet_from_4(age_group, disease, file_path="4.json"):
    data = load_json_data(file_path)
    if isinstance(data, str):  
        return data  
    
    recommendations = data.get("diet_recommendations", [])
    all_age_groups = [entry["age_group"] for entry in recommendations]
    all_conditions = [entry["disease_condition"] for entry in recommendations]
    
    best_age_group, age_score = get_best_match(age_group, all_age_groups)
    best_disease, disease_score = get_best_match(disease, all_conditions)
    
    if age_score >= 80 and disease_score >= 80:
        for entry in recommendations:
            if entry["age_group"] == best_age_group and entry["disease_condition"] == best_disease:
                return entry
    return "No matching diet recommendation found in 4gpt.json."

# Function for fuzzy age group matching
def fuzzy_membership(age, center, spread=5):
    return np.exp(-0.5 * ((age - center) / spread) ** 2)

def get_fuzzy_age_group(age):
    age_groups = {"20-30": 25, "30-40": 35, "40-50": 45, "50-60": 55}
    membership_scores = {group: fuzzy_membership(age, center) for group, center in age_groups.items()}
    return max(membership_scores, key=membership_scores.get)

# Function to get diet from 6web.json (Includes genetic & microbiome-based diet)
def get_diet_from_6(age, condition, file_path="6web.json"):
    data = load_json_data(file_path)
    if isinstance(data, str):  
        return data  
    
    age_group = get_fuzzy_age_group(age)

    for entry in data:
        if entry["entities"]["age_group"] == age_group:
            genetic_marker = entry["entities"]["genetic_marker"]
            microbiome_profile = entry["entities"]["microbiome_profile"]
            if entry["entities"]["condition"].lower() == condition.lower():
                return {
                    "response": entry["response"],
                    "genetic_marker": genetic_marker,
                    "microbiome_profile": microbiome_profile
                }
    
    return "No matching diet recommendation found in 6web.json."

# Load JSON dataset for diet plans
def load_data(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Error: File not found!")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid JSON format!")
        return []

# Gaussian fuzzy membership function
def compute_similarity(user_age, user_height, user_weight, user_has_disease, user_disease_type, entry):
    age_score = fuzzy_membership(user_age, entry["age"], spread=10)  # Age fuzziness ±10 years
    height_score = fuzzy_membership(user_height, entry["height"], spread=0.1)  # Height fuzziness ±0.1m
    weight_score = fuzzy_membership(user_weight, entry["weight"], spread=10)  # Weight fuzziness ±10kg
    disease_score = 1 if (user_has_disease == entry["has_disease"] and (not user_has_disease or user_disease_type.lower() == entry["disease_type"].lower())) else 0

    # Count how many attributes match (at least two required)
    match_count = sum([age_score > 0.5, height_score > 0.5, weight_score > 0.5, disease_score == 1])

    # Only consider entries with at least two matches
    if match_count >= 2:
        return (age_score + height_score + weight_score + disease_score) / 4  # Average similarity score
    return 0  # Ignore if less than two attributes match

# Find the best matching diet plan
def get_diet_recommendation(data, user_age, user_height, user_weight, user_has_disease, user_disease_type):
    best_match = None
    highest_score = 0

    for entry in data:
        score = compute_similarity(user_age, user_height, user_weight, user_has_disease, user_disease_type, entry)
        if score > highest_score:
            highest_score = score
            best_match = entry

    return best_match

# Main chatbot function
def main():
    print("👋 Welcome to the AI-Based Diet Recommendation System! Let's get started.\n")
    
    age = int(input("📌 Enter your age: ").strip())
    age_group = input("📌 Enter your age group (Infants, Children, Adolescents, Adults, Elderly, Pregnant Women): ").strip()
    height_ft = int(input("📌 Enter your height (feet): ").strip())
    height_in = int(input("📌 Enter your height (inches): ").strip())
    weight = float(input("📌 Enter your weight (in kg): ").strip())
    
    disease = input("📌 Do you have any disease? (yes/no): ").strip().lower()
    disease_condition = input("📌 Enter your disease (or type 'none'): ").strip() if disease == "yes" else "None"
    
    height_cm = (height_ft * 30.48) + (height_in * 2.54)  # Convert height to cm
    
    # Load diet data from JSON files
    diet_data_1 = load_json_data('1.json')
    diet_data_3 = load_json_data('3.json')
    diet_data_5 = load_data('5gpt.json')  # Load additional diet data

    # Search for disease in both JSON files
    matched_disease_1 = find_disease(disease_condition.lower(), diet_data_1)
    matched_disease_3 = find_disease(disease_condition.lower(), diet_data_3)

    # Combine diet recommendations
    combined_recommendations = {}
    if matched_disease_1:
        for nutrient, guideline in matched_disease_1["diet_guidelines"].items():
            combined_recommendations[nutrient] = guideline

    if matched_disease_3:
        for nutrient, guideline in matched_disease_3["diet_guidelines"].items():
            if nutrient in combined_recommendations:
                combined_recommendations[nutrient] += f"; {guideline}"
            else:
                combined_recommendations[nutrient] = guideline

    # Get diet recommendations from 4gpt.json
    diet_4 = get_diet_from_4(age_group, disease_condition)
    
    # Get diet recommendations from 6web.json
    diet_6_data = get_diet_from_6(age, disease_condition)

    # Get the best match from 5gpt.json
    user_has_disease = disease.lower() == "yes"
    user_disease_type = disease_condition if user_has_disease else "No Disease"
    user_height_m = height_cm / 100  # Convert cm to meters
    best_diet_plan = get_diet_recommendation(diet_data_5, age, user_height_m, weight, user_has_disease, user_disease_type)

    print("\n********** 📋 DIET RECOMMENDATION **********")
    print(f"👤 Age Group: {age_group}")
    print(f"📏 Height: {height_cm:.2f} cm | ⚖️ Weight: {weight} kg\n")
    
    print("🔹 **Combined Diet Recommendations for Disease Condition:**")
    if combined_recommendations:
        for nutrient, guideline in combined_recommendations.items():
            print(f"- {nutrient}: {guideline}")
    else:
        print("No matching disease found in the dataset.")
    
    print("\n🔹 **Diet Based on Disease Condition:**")
    if isinstance(diet_4, dict):
        print(f"- 🥗 Nutrient Focus: {', '.join(diet_4['nutrient_focus'])}")
        print(f"- 🍎 Recommended Foods: {', '.join(diet_4['recommended_foods'])}")
        print(f"- 🍽️ Meal Type: {diet_4['meal_type']}")
        print(f"- 💡 Advice: {diet_4['advice']}")
    else:
        print(diet_4)
    
    print("\n🔹 **Personalized Genetic & Microbiome-Based Diet:**")
    if isinstance(diet_6_data, dict):
        print(f"- **Genetic Marker:** {diet_6_data['genetic_marker']}")
        print(f"- **Microbiome Profile:** {diet_6_data['microbiome_profile']}")
        print(f"- 🍽️ Meal Plan: {diet_6_data['response']}")
    else:
        print(diet_6_data)

    print("\n🔹 **Best Matching Diet Plan from 5gpt.json:**")
    if best_diet_plan:
        print(f"Age: {best_diet_plan['age']}, Height: {best_diet_plan['height']}m, Weight: {best_diet_plan['weight']}kg")
        print(f"Disease: {best_diet_plan['disease_type']}")
        print("\nDiet Plan:")
        print(f"- Breakfast: {best_diet_plan['diet_plan']['breakfast']}")
        print(f"- Lunch: {best_diet_plan['diet_plan']['lunch']}")
        print(f"- Dinner: {best_diet_plan['diet_plan']['dinner']}")
        print(f"- Drink: {best_diet_plan['diet_plan']['drink']}")
    else:
        print("No suitable diet plan found for the given inputs.")

    print("******************************************")
    print("✨ Stay healthy and eat well! 😊")

if __name__ == "__main__":
    main()
