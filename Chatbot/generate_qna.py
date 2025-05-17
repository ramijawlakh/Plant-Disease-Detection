import json
import os
import random

# Define the directory and file paths
directory = r"C:\SeniorLLM"
input_file = os.path.join(directory, "disease_info.json")
output_file = os.path.join(directory, "final_clean_training_dataset.json")

# Number of unique variants per question type
NUM_VARIANTS = 5  # Ensures more diversity

# Helper function to extract watering instructions
def get_watering_instruction(treatments):
    parts = [t.strip() for t in treatments.split(',')]
    for part in parts:
        if "water" in part.lower():
            return part.strip()
    return "Ensure proper watering based on soil moisture."

# Function to generate diversified Q&A pairs with better phrasing and less repetition
def generate_qa_pairs(entry):
    disease = entry.get("disease", "Unknown Disease")
    causes = entry.get("causes", "Unknown causes")
    symptoms = entry.get("symptoms", "Unknown symptoms")
    treatments = entry.get("treatments", "No specific treatments mentioned")
    affected = entry.get("affected", "Various plants")
    
    # List to hold Q&A pairs
    qa_pairs = []
    def get_random_variant(variants):
        return random.choice(variants)
    
    # Split treatments into a list for multi-turn use
    treatments_list = [t.strip() for t in treatments.split(',') if t.strip()]
    
    # Handle disease-specific entries
    if "Maintenance" not in disease:
        cause_questions = [
            f"Why does {disease} develop?",
            f"What are the primary causes of {disease}?",
            f"How does {disease} occur?"
        ]
        cause_answers = [
            f"{disease} is mainly caused by {causes} and thrives under specific conditions.",
            f"The leading cause of {disease} is {causes}, often worsened by environmental factors.",
            f"{disease} happens due to {causes}, which create an ideal environment for its spread."
        ]
        
        symptom_questions = [
            f"What are the visible signs of {disease}?",
            f"How do I know if my plant has {disease}?",
            f"What symptoms indicate {disease}?"
        ]
        symptom_answers = [
            f"Signs of {disease} include {symptoms}.",
            f"You can identify {disease} by looking for {symptoms}.",
            f"Common indicators of {disease} are {symptoms}."
        ]
        
        treatment_questions = [
            f"How do I manage {disease}?",
            f"What’s the best way to treat {disease}?",
            f"How can I stop {disease} from spreading?"
        ]
        treatment_answers = [
            f"Effective treatment for {disease} includes {treatments}.",
            f"To control {disease}, consider {treatments}.",
            f"{disease} can be managed using {treatments}."
        ]
        
        affected_questions = [
            f"What plants are most affected by {disease}?",
            f"Which species are vulnerable to {disease}?",
            f"Can {disease} spread to different plant types?"
        ]
        affected_answers = [
            f"{disease} primarily affects {affected}.",
            f"The plants most vulnerable to {disease} are {affected}.",
            f"{disease} has been observed in {affected}."
        ]
        
        for _ in range(NUM_VARIANTS):
            qa_pairs.append({"User": get_random_variant(cause_questions), "Bot": get_random_variant(cause_answers)})
            qa_pairs.append({"User": get_random_variant(symptom_questions), "Bot": get_random_variant(symptom_answers)})
            qa_pairs.append({"User": get_random_variant(treatment_questions), "Bot": get_random_variant(treatment_answers)})
            qa_pairs.append({"User": get_random_variant(affected_questions), "Bot": get_random_variant(affected_answers)})
        
        # Multi-turn conversation
        if treatments_list:
            alternative_treatment = random.choice(treatments_list)
        else:
            alternative_treatment = "consulting a specialist for a tailored approach."
        
        qa_pairs.append({"User": f"I tried {treatments_list[0]} but it’s not working.", "Bot": f"If {treatments_list[0]} didn’t help, consider {alternative_treatment}."})
    
    else:
        plant_name = disease.replace("Maintenance for ", "")
        watering_instruction = get_watering_instruction(treatments)
        qa_pairs.append({"User": f"How do I take care of {plant_name}?", "Bot": f"To maintain {plant_name}, {treatments}."})
        qa_pairs.append({"User": f"How often should I water {plant_name}?", "Bot": f"{watering_instruction}"})
    
    return qa_pairs

# Read input JSON
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        disease_data = json.load(f)
except Exception as e:
    print(f"Error reading {input_file}: {e}")
    exit(1)

# Generate dataset
training_dataset = []
for entry in disease_data:
    training_dataset.extend(generate_qa_pairs(entry))

# Save dataset
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(training_dataset, f, indent=4)
    print(f"Successfully generated {len(training_dataset)} Q&A pairs in {output_file}.")
except Exception as e:
    print(f"Error writing to {output_file}: {e}")