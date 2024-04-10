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
    we are having two tables first table name is invoice_info which contains columns name which is given in triple backticks.
    '''invoice_id(datatype : int)which is primary_key of table,invoice_date(datatype : date),seller_name(datatype : varchar), seller_address(datatype : varchar), seller_taxid(datatype : varchar),
    seller_iban(datatype : varchar), client_name(datatype : varchar), client_address(datatype : varchar), client_taxid(datatype : varchar),
    total(datatype : int)'''
    Second table name is invoice_items which contains columns name which is given in triple backticks.
    '''item_id(datatype : int) which is primary key of table, invoice_id(datatype : int) which is forigen key in this table,quantity(datatype : int), unit_measure(datatype : varchar),net_price(datatype : float),net_worth(datatype : float),vat(datatype : float),
    sales(datatype : float)'''
    If customers ask question related to invoice try to make correct postgresSQL query and if there is question which includes both the table information try 
    to use joins using both the tables.
    For date time question make use of appropriate date functions used in postgresSQL for queries related to date or time.
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