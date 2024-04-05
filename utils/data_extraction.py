"""
"""

import google.generativeai as genai
from pathlib import Path
import re
import json
import csv
import os
GOOGLE_API_KEY="AIzaSyAKQ8_cgU2VzQ_ydN1S4gUs-mi6ObZvGtQ"
genai.configure(api_key=GOOGLE_API_KEY)
# Model Configuration
MODEL_CONFIG = {
  "temperature": 0.2,
  "top_p": 1,
  "top_k": 32,
  "max_output_tokens": 4096,
}
## Safety Settings of Model
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  }
]
model = genai.GenerativeModel(model_name = "gemini-pro-vision",
                              generation_config = MODEL_CONFIG,
                              safety_settings = safety_settings)
def image_format(image_path):
    img = Path(image_path)
    if not img.exists():
        raise FileNotFoundError(f"Could not find image: {img}")
    image_parts = [
        {
            "mime_type": "image/png", ## Mime type are PNG - image/png. JPEG - image/jpeg. WEBP - image/webp
            "data": img.read_bytes()
        }
    ]
    return image_parts
def gemini_output(image_path, system_prompt, user_prompt):
    image_info = image_format(image_path)
    input_prompt= [system_prompt, image_info[0], user_prompt]
    response = model.generate_content(input_prompt)
    json_data = re.sub(r'```', '', response.text)
    json_data = re.sub(r'json', '', json_data)
    json_data= json.loads(
    json_data
    )
    return json_data
system_prompt = """
               You are a specialist in comprehending receipts.
               Input images in the form of receipts will be provided to you,
               and your task is to respond to questions based on the content of the input image.
               """
#system_prompt = "Convert Invoice data into json format with appropriate json tags as required for the data in image "
# image_path = ["invoices_images/invoice_50_charspace_51_1.jpg","invoices_images/invoice_0_charspace_1_1.jpg", "invoices_images/invoice_1_charspace_2_1.jpg"]
user_prompt = "Convert Invoice data into json format with appropriate json tags as required for the data in image "
def get_files_from_folder(folder_path):
    files = []
    # Iterate over all files in the folder
    for file_name in os.listdir(folder_path):
        # Check if the path is a file (not a directory)
        if os.path.isfile(os.path.join(folder_path, file_name)):
            files.append(file_name)
    return files
# Example usage:
folder_path = 'invoices_images'
files_in_folder = get_files_from_folder(folder_path)
for i in files_in_folder:
    print(str(i))
    output = gemini_output("invoice_images/"+str(i), system_prompt, user_prompt)
    print(output)
    collection = db['invoice_data']
    insert_result = collection.insert_one(output)
    print("Inserted ID:", insert_result.inserted_id)