import streamlit as st
import os
import tempfile
from data_extraction import gemini_output
from utils.llm import invoke_llm
from utils.database_connector import DatabaseConnector
from utils.data_pipeline import DBWriter, SQLQueryBuilder, PrepareData

# Function to connect to the database
def connect_to_database():
    connector = DatabaseConnector()
    connector.create_connection()
    return connector

# Function to insert data into the database
def insert_data(data):
    Writer = DBWriter(connector=connect_to_database())
    records = PrepareData(data)
    SQLstring = SQLQueryBuilder.build_insert_query(
        table_name="public.invoice_data",
        columns=("invoice_id", "invoice_date", "seller_name", "seller_address", "seller_taxid", "seller_iban", "client_name", "client_address", "client_taxid", "item_name", "quantity", "unit_measure", "net_price", "net_worth", "vat", "sales")
    )
    for record in records:
        Writer.insert_data(query=SQLstring, data=record)

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
            user_prompt =  "Convert Invoice data into json format with appropriate json tags as required for the data in image "  # Provide your user prompt
            extracted_data = gemini_output(tmpfile_path, system_prompt, user_prompt)
            st.write(f'Extracted Data from {pdf_file.name}:')
            st.write(extracted_data)

            # Insert extracted data into the database
            insert_data(extracted_data)

            # Remove temporary file
            os.remove(tmpfile_path)

    # Query Generation Section
    st.header('Query Generation')
    prompt = st.text_input('Enter Prompt')
    if st.button('Generate Query'):
        # Generate SQL query
        query = invoke_llm(prompt)
        st.write('Generated Query:')
        st.write(query)

if __name__ == '__main__':
    main()
