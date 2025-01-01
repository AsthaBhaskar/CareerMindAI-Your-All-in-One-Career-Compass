# File: backend/app.py
from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS to allow frontend requests from different origins

# Load the fine-tuned model from Hugging Face
model_name = "asthaaa300/results"  # Replace with your Hugging Face model repository name
print("Loading model and tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
print("Model and tokenizer loaded successfully.")

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Roadmap Generator API!"})

@app.route("/generate-roadmap", methods=["POST"])
def generate_roadmap():
    try:
        # Get JSON data from the request
        user_input = request.json
        career_goal = user_input.get("career_goal", "")
        skills = user_input.get("skills", [])
        learning_preference = user_input.get("learning_preference", "")

        # Validate inputs
        if not career_goal or not skills or not learning_preference:
            return jsonify({"error": "All fields (career_goal, skills, learning_preference) are required."}), 400

        # Build the input prompt
        prompt = (
            f"Career Goal: {career_goal}\n"
            f"Skills: {', '.join(skills)}\n"
            f"Learning Preference: {learning_preference}\n"
            f"Roadmap:"
        )
        
        # Generate the roadmap
        print("Generating roadmap...")
        inputs = tokenizer(prompt, return_tensors="pt")
        outputs = model.generate(
            inputs.input_ids,
            max_length=300,
            num_beams=4,
            early_stopping=True,
            no_repeat_ngram_size=2  # Prevent repetitive outputs
        )
        roadmap = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print("Roadmap generated successfully.")

        # Return the generated roadmap
        return jsonify({"roadmap": roadmap})

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": "An error occurred while generating the roadmap."}), 500

if __name__ == "__main__":
    app.run(debug=True)
