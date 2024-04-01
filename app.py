"""FastAPI endpoint for generating answers using Llama 2 model."""

# Import dependencies
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.llms import CTransformers
import time
import os
import logging
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from utils.llm import invoke_llm
from utils.query import query_database
from utils.logger import create_logger
from utils.vector_search import VectorQueryFromDirectory

# Ignore warnings
import warnings
warnings.filterwarnings("ignore")

# Setup logging
_logger = create_logger("api")

# Define FastAPI application
app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})

# Define request body model
class InputText(BaseModel):
    """Request body model for input text."""
    text: str

# Initialize the language model for SQL queries.
llmSQL = CTransformers(
    model = "model/mistral-7b-instruct-v0.1.Q3_K_L.gguf",
    model_type="llama",
    config={
        'max_new_tokens': 256,  # Set the maximum number of tokens here
        'temperature': 0.2
    }
)

# Initialize the language model for VectorDB queries.
try:
    tokenizer = AutoTokenizer.from_pretrained("vectorllm_tokentizer/")
    model = AutoModelForSeq2SeqLM.from_pretrained("vectorllm_model/")
    _logger.info("Successfully initialized model from local directory")
except:
    # Load model from hub and save model locally if not available
    _logger.info("Unable to load model locally. Fetching from hugging face...")
    tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-large")
    model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")
    model.save_pretrained("./vectorllm_model/")
    tokenizer.save_pretrained("./vectorllm_tokentizer/")
    _logger.info("Successfully initialized model from Huggingface and saved in local directory")
    
# Initialize the VectorDB client
vectorDB = VectorQueryFromDirectory(
    embedding_model_name='sentence-transformers/all-MiniLM-L6-v2',
    embedding_model_kwargs={"temperature":1, "max_length":1000},
    vectorDB_directory=os.getenv("VECTORDB"),
    llm = model,
    query=None
)


# Define api endpoint to test connection
@app.get("/")
def test_connection() -> dict:
    """
    Test the connection to the FastAPI server.

    Raises:
        HTTPException: If there is an error during the connection test.

    Returns:
        dict: A dictionary indicating the success of the connection test.
    """
    try:
        return {"message": "Connection successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
# Define SQL Query API endpoint
@app.post("/sqlQuery")
async def get_answer(input_text: InputText) -> dict:
    """
    Endpoint to generate an answer using Llama 2 model.

    Args:
        input_text (InputText): The input text provided in the request body.

    Returns:
        dict: A dictionary containing the generated answer.
    """
    try:
        start_time = time.time()
        # Log message
        _logger.info("Generating answer using Llama 2 model.")
        
        # Get text from request body
        text = input_text.text
        _logger.info("Input text: %s" % text)
        
        # Generate response using the language model
        query = invoke_llm(text, llmSQL)
        
        # Query database
        answer = query_database(query)
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        _logger.info("Time elapsed: %.3f seconds" % elapsed_time)
        
        # Return the answer in a dictionary
        return {"answer": answer}
    except Exception as e:
        # Raise an HTTPException if an error occurs
        raise HTTPException(status_code=500, detail=str(e))


# Define Vector DB Query API endpoint
@app.post("/vectorQuery")
async def get_answer(input_text: InputText) -> dict:
    """
    Endpoint to generate an answer using Llama 2 model.

    Args:
        input_text (InputText): The input text provided in the request body.

    Returns:
        dict: A dictionary containing the generated answer.
    """
    try:
        start_time = time.time()
        # Log message
        _logger.info("Generating answer using Llama 2 model.")
        
        # Get text from request body
        text = input_text.text
        _logger.info("Input text: %s" % text)
        
        # Generate response using the language model
        qa = vectorDB.query_vectorDB()
        
        # Query database
        result=chain(
            {"query": text}, 
            return_only_outputs=True
        )
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        _logger.info("Time elapsed: %.3f seconds" % elapsed_time)
        
        # Return the answer in a dictionary
        return {"answer": textwrap.fill(result['result'], width=500)}
    except Exception as e:
        # Raise an HTTPException if an error occurs
        raise HTTPException(status_code=500, detail=str(e))
