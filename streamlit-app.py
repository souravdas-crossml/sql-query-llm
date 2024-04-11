import streamlit as st
import os
import tempfile
from utils.llm import invoke_llm
from utils.database_connector import DatabaseConnector
from utils.data_pipeline import DBWriter, SQLQueryBuilder, DataParser  # Import DataParser class
from data_extraction import gemini_output  # Import gemini_output function from data_extraction module
from dotenv import load_dotenv, find_dotenv
from langchain_community.llms import CTransformers
from utils.query import query_database


load_dotenv(find_dotenv())

# Function to connect to the database
def connect_to_database():
    connector = DatabaseConnector()
    connector.create_connection()
    return connector

Writer = DBWriter(connector=connect_to_database())
parser = DataParser()

# Initialize the language model for SQL queries.
llmSQL = CTransformers(
    model = "model/mistral-7b-instruct-v0.1.Q3_K_L.gguf",
    model_type="llama",
    config={
        'max_new_tokens': 512,  # Set the maximum number of tokens here
        'temperature': 0
    }
)

invoice_info_SQLstring = SQLQueryBuilder.build_insert_query(
    table_name = "public.invoice_info",
    columns = (
        "invoice_id", "invoice_date", "seller_name", "seller_address", 
        "seller_taxid", "seller_iban", "client_name", "client_address", 
        "client_taxid", "total_tax", "total"
    )
)


invoice_items_SQLstring = SQLQueryBuilder.build_insert_query(
    table_name="invoice_items",
    columns=(
        "invoice_id", "item_name", "quantity", "unit_measure", "net_price", 
        "net_worth", "vat", "sales"
    )
)

# Function to insert data into the database
def insert_data(data):
    # Create an instance of DataParser
    
    record = parser.ParseData(data)

    Writer.insert_single_query_data(
        query=invoice_info_SQLstring,
        data=record[0]
    )
    for i in record[1]:
      Writer.insert_single_query_data(
          query=invoice_items_SQLstring,
          data=i
      )

# Streamlit app interface
def main():
    st.title('Invoice Data Extraction and Query Generation')

    # Data Extraction Section
    st.header('Data Extraction')
    pdf_files = st.file_uploader('Upload PDF Files', accept_multiple_files=True)
    if pdf_files:
        for pdf_file in pdf_files:
            with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
                tmpfile.write(pdf_file.read())
                tmpfile_path = tmpfile.name
            
            system_prompt = """
                    You are a specialist in comprehending receipts.
                    Input images in the form of receipts will be provided to you,
                    and your task is to respond to questions based on the content of the input image.
                    """  # Provide your system prompt
            user_prompt =  """
                            retrieve these values: invoice number, invoice date, client name, client address and tax ID, seller name, 
                            seller address and tax ID, invoice iban, names of invoice items included into this invoice, gross worth value 
                            for each invoice item from the table, total tax total.format response as following 
                            \"invoice_number\": {}, \"invoice_date\": {}, {\"client_name\": {}, \"client_address\": {}, 
                            \"client_tax_id\": {}, \", \"seller_name\": {},\"seller_address\": {},\"seller_tax_id\": {}, 
                            \"invoice_iban\": {}, \"item\": [{"description": "description or name of the item that has been bougth", 
                            "quantity":"total number of each item", "unit":"unit for measurement", "net_price":"price of each item", 
                            "net_worth":"multiple of quantity and net_price", "tax":"tax or vat" ,"gross_worth": "how much does the item cost"}], 
                            \"total_tax\": {}, \"total\": {}}"
                            """
            
            try:
                extracted_data = gemini_output(tmpfile_path, system_prompt, user_prompt)  # Call gemini_output function
                st.write(f'Extracted Data from {pdf_file.name}:')
                st.write(extracted_data)

                # Insert extracted data into the database
                insert_data(extracted_data)
            except Exception as e:
                st.write(f"Unable to etract and save data for file -> {pdf_file.name}")
                st.write(f"error -> {e}")

            # Remove temporary file
            os.remove(tmpfile_path)

    # Query Generation Section
    st.header('Query Generation')
    prompt = st.text_input('Enter Prompt')
    if st.button('Generate Query'):
        # Generate SQL query
        query = invoke_llm(prompt, llmSQL)
        st.write(f"Generated Query: {query}")

        answer = query_database(query)

        st.write(f"Anwser: {answer}")



if __name__ == '__main__':
    main()
