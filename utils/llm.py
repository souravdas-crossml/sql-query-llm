"""
Module Docstring: This module provides a function to invoke a Language Learning Model (LLM) for generating SQL queries.

Dependencies:
    - langchain: A library for building and interacting with language-based AI models.
    - prompt: A module containing the SQL query template.
"""

# import dependencies
import re
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
    You are a Senior Data Engineer. Your main role is to generate postgresSQL query based on User response.
    I have shared the column names in triple backticks.
    ''' invoice_id(datatype : int), invoice_data(datatype : date),seller_name(datatype : varchar), seller_address(datatype : varchar), seller_taxid(datatype : varchar),
    seller_iban(datatype : varchar), client_name(datatype : varchar), client_address(datatype : varchar), client_taxid(datatype : varchar), item_name(datatype : varchar),
    quantity(datatype : int), unit_measure(datatype : varchar),net_price(datatype : float),net_worth(datatype : float),vat(datatype : float),
    sales(datatype : float)'''
    Table name: invoice_data
    users are the customers who want data insights.
    **Only answer in SQL query**
    {text}
    Just SQL query:
    **Important note : if query is asked and answer is given by model and again if same query is asked dont try to change the answer keep it same**
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
    try:
        sql_query_str = re.search(r'SELECT.*', sql_query['text'], re.DOTALL).group(0).strip('```').strip()
        _logger.info("Generated SQL query: %s" % sql_query_str)
    except AttributeError:
        _logger.error("No SELECT statement found in the SQL query.")

    # Convert SQL query to string
    return sql_query_str