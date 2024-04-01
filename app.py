"""FastAPI endpoint for generating answers using Llama 2 model."""

# Import dependencies
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.llms import CTransformers
import time
import logging

from utils.llm import invoke_llm
from utils.query import query_database
from utils.logger import create_logger


# Setup logging
_logger = create_logger("api")

# Define FastAPI application
app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})

# Define request body model
class InputText(BaseModel):
    """Request body model for input text."""
    text: str

# Initialize the language model
llm = CTransformers(
    model = "model/mistral-7b-instruct-v0.1.Q3_K_L.gguf",
    model_type="llama",
    config={
        'max_new_tokens': 256,  # Set the maximum number of tokens here
        'temperature': 0.2
    }
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
    
# Define API endpoint
@app.post("/query")
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
        query = invoke_llm(text, llm)
        
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
