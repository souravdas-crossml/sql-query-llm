import re
import os
import json
import argparse
from pathlib import Path
import google.generativeai as genai

from dotenv import load_dotenv, find_dotenv

from logger import create_logger
from data_pipeline import DBWriter, SQLQueryBuilder, PrepareData
from database_connector import DatabaseConnector



_logger = create_logger("Gemini")

load_dotenv(find_dotenv())
api_key = os.getenv('GOOGLE_API_KEY')

genai.configure(api_key=api_key)

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
model = genai.GenerativeModel(
    model_name = "gemini-pro-vision",
    generation_config = MODEL_CONFIG,
    safety_settings = safety_settings
)

Writer = DBWriter(connector=DatabaseConnector())


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
    json_data= json.loads(json_data)
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

def main(folder_path):
  data = []
  files = get_files_from_folder(folder_path)

  for file in files:
      _logger.info("File path %s",os.path.join(folder_path, file))
      output = gemini_output(os.path.join(folder_path, file), system_prompt, user_prompt)
      data.append(output)

  records = PrepareData(data)

  SQLstring = SQLQueryBuilder.build_insert_query(
      table_name = "public.invoice_data",
      columns = ("invoice_id", "invoice_date", "seller_name",
                 "seller_address", "seller_taxid", "seller_iban",
                 "client_name", "client_address", "client_taxid",
                 "item_name", "quantity", "unit_measure", "net_price",
                 "net_worth", "vat", "sales"
                 ),
                 )
  
  for record in records:
    _logger.info("Record to be inserted: %s", str(record))
    Writer.insert_data(
        query=SQLstring,
        data=record
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process PDF files containing invoice data.")
    parser.add_argument("folder_path", type=str, help="Path to the folder containing PDF files.")
    args = parser.parse_args()
    main(args.folder_path)
