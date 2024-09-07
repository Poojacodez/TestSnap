import os
from flask import Flask, request, jsonify, render_template
import openai
from PIL import Image

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = "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"

# Serve the index.html when accessing the main route
@app.route("/")
def index():
    return render_template("index.html")


# API endpoint to process screenshots and generate test cases
@app.route("/generate-test-cases", methods=["POST"])
def generate_test_cases():
    context = request.form.get("context", "")
    print(f"Received context: {context}")

    # Handle uploaded screenshots
    screenshots = request.files.getlist("screenshots")
    if not screenshots:
        return jsonify({"error": "No screenshots uploaded"}), 400

    screenshot_paths = []
    for screenshot in screenshots:
        if screenshot and screenshot.filename:
            try:
                img = Image.open(screenshot)
                img_path = os.path.join("uploads", screenshot.filename)
                img.save(img_path)
                screenshot_paths.append(img_path)
                print(f"Saved file: {img_path}")
            except Exception as e:
                print(f"Error processing file {screenshot.filename}: {e}")
                return jsonify({"error": f"Error processing file {screenshot.filename}"}), 500
        else:
            print("No file selected or empty filename")

    # Process the screenshots and context with a multimodal LLM
    try:
        test_case_description = generate_test_case_description(screenshot_paths, context)
        return jsonify({"test_cases": test_case_description})
    except Exception as e:
        print(f"Error generating test case description: {e}")
        return jsonify({"error": "Error generating test case description"}), 500


# Function to generate test case descriptions using multimodal LLM
def generate_test_case_description(screenshot_paths, context):
    print(f"Generating test case description for screenshots: {screenshot_paths}")

    images_data = []
    for path in screenshot_paths:
        try:
            with open(path, "rb") as img_file:
                images_data.append(img_file.read())
        except Exception as e:
            print(f"Error reading file {path}: {e}")
            continue

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4",  # Assuming GPT-4 is used (ensure you have API access)
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI specialized in generating test cases for software.",
                },
                {
                    "role": "user",
                    "content": f"Please generate test cases for these screenshots: {screenshot_paths}. Context: {context}",
                },
            ],
        )
        return completion.choices[0].message["content"]
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "Error generating test case description."


if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
