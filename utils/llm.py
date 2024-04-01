"""
Module Docstring: This module provides a function to invoke a Language Learning Model (LLM) for generating SQL queries.

Dependencies:
    - langchain: A library for building and interacting with language-based AI models.
    - prompt: A module containing the SQL query template.
"""

# import dependencies
from langchain import PromptTemplate
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from .logger import create_logger
_logger = create_logger("llm_invoke")


def invoke_llm(text: str, llm: any) -> str:
    """
    Function to invoke the Language Learning Model.

    Args:
        query (str): The query string.
        llm (any): The Language Learning Model.

    Returns:
        str: The response from the Language Learning Model.
    """
    
    # Create a PromptTemplate instance
    template = """
            This is the provided text
            {text}
           Just SQL query:
           **Important note : if query is asked and answer is given by model and again if same query is asked dont try to change the answer keep is same**
           """
    
    # Create a PromptTemplate instance
    prompt = PromptTemplate(template=template, input_variables=["text"])
    _logger.info("================================")
    _logger.info("Created PromptTemplate: %s" % prompt)
    _logger.info("================================")
    
    # Create the LLMChain
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    _logger.info("Created LLMChain")

    # Invoke LangChain to generate SQL query
    sql_query = llm_chain.invoke(text)
    _logger.info("Generated SQL query: %s" % sql_query["text"])

    # Convert SQL query to string
    return sql_query['text']