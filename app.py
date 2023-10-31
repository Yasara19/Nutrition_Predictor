from flask import Flask, request, jsonify
import os, io
from google.cloud import vision_v1
from google.cloud.vision_v1 import types
import re

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'cloudapi.json'

app = Flask(__name__)

@app.route('/extract_hemoglobin', methods=['POST'])
def extract_hemoglobin():
   # Check if an image file is included in the request
    if 'file' not in request.files:
        return jsonify({"error": "No image file provided."})

    # Get the image file from the request
    image_file = request.files['file']

    # Check if the file has an allowed extension (e.g., .jpg, .jpeg, .png)
    allowed_extensions = {'jpg', 'jpeg', 'png'}
    if not image_file or not image_file.filename or not image_file.filename.split('.')[-1].lower() in allowed_extensions:
        return jsonify({"error": "Invalid or missing image file."})

    # Read the image file content
    image_content = image_file.read()

    # Process the image with Google Vision API
    client = vision_v1.ImageAnnotatorClient()
    image = vision_v1.types.Image(content=image_content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if texts:
        extracted_text = texts[0].description
    else:
        extracted_text = "No text found in the image."

    # Define a regular expression pattern to match values ending with "g/dl"
    pattern = re.compile(r'(\d+\.\d+)\s*g/dl', re.IGNORECASE)

    # Find and extract values ending with "g/dl"
    matches = pattern.findall(extracted_text)

    # Initialize variables to store the first value
    first_value = None

    # Check if any matches were found
    if matches:
        # Extract the first value from the first match
        first_value = matches[0]

    # Prepare and send the response
    if first_value is not None:
        result = f"{first_value}"
    else:
        result = "No values ending with 'g/dl' found."

    return jsonify({"result": result})


@app.route('/extract_glucose', methods=['POST'])
def extract_glucose():
    # Check if an image file is included in the request
    if 'file' not in request.files:
        return jsonify({"error": "No image file provided."})

    # Get the image file from the request
    image_file = request.files['file']

    # Check if the file has an allowed extension (e.g., .jpg, .jpeg, .png)
    allowed_extensions = {'jpg', 'jpeg', 'png'}
    if not image_file or not image_file.filename or not image_file.filename.split('.')[-1].lower() in allowed_extensions:
        return jsonify({"error": "Invalid or missing image file."})

    # Read the image file content
    image_content = image_file.read()

    # Process the image with Google Vision API
    client = vision_v1.ImageAnnotatorClient()
    image = vision_v1.Image(content=image_content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if texts:
        extracted_text = texts[0].description
        pattern = re.compile(r'(\d+)\s*(mg/dl|mmol/L)', re.IGNORECASE)

        matches = pattern.findall(extracted_text)

        # Extract values, convert to integers, and find the smallest "mg/dl" value
        mg_dl_values = [int(match[0]) for match in matches if match[1].lower() == 'mg/dl']

        if mg_dl_values:
            smallest_value = min(mg_dl_values)
            unit = "mg/dl"
        else:
            # If no "mg/dl" values found, extract "mmol/L" values
            mmol_L_values = [int(match[0]) for match in matches if match[1].lower() == 'mmol/L']

            if mmol_L_values:
                smallest_value = min(mmol_L_values)
                unit = "mmol/L"
            else:
                return jsonify({"message": "No 'mg/dl' or 'mmol/L' values found"})

        result = f"{smallest_value}"
        return jsonify({"result": result})

    else:
        return jsonify({"message": "No text found in the image"}), 404
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
