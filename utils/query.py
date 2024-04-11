"""
Module Docstring: This module provides a function to query a PostgreSQL 
database using DatabaseConnector.
"""
# Import dependencies
from .database_connector import DatabaseConnector
from .logger import create_logger

_logger = create_logger("query")

def query_database(query:str) -> list:
    """
    Function to query the database using DatabaseConnector and close the connection after the query.

    Args:
        query (str): query string that will be executed

    Returns:
        list: A list of query results.
    """
    # Create a DatabaseConnector instance
    db_connector = DatabaseConnector()

    try:
        # Create a database connection
        db_connector.create_connection()

        # Perform database query
        cursor = db_connector.connection.cursor()
        cursor.execute(query)
        r = [dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
        
        # Close cursor
        cursor.close()

        return r

    finally:
        # Close connection
        db_connector.close_connection()
