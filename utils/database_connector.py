"""
Module Docstring: This module provides functions for creating and closing a connection to a PostgreSQL database.

Dependencies: os, psycopg2

"""

# Import dependencies
import os
import psycopg2

from dotenv import load_dotenv, find_dotenv

from .logger import create_logger
_logger = create_logger("db")

load_dotenv(find_dotenv())

class DatabaseConnector:
    """
    This class provides methods for creating and closing a connection to a PostgreSQL database.
    """

    def __init__(
        self,
        host: str = os.getenv("HOST"),
        user: str = os.getenv("USER"),
        port: str = os.getenv("PORT"),
        password: str = os.getenv("PASSWORD"),
        database: str = os.getenv("DATABASE")
    ) -> None:
        """
        Initialize the DatabaseConnector with connection parameters.

        Args:
            host (str, optional): The hostname of the database server. 
                                Defaults to os.getenv("HOST").
            user (str, optional): The username to connect to the database. 
                                Defaults to os.getenv("USER").
            port (str, optional): The port of the database server. 
                                Defaults to os.getenv("PORT").
            password (str, optional): The password to connect to the database. 
                                Defaults to os.getenv("PASSWORD").
            database (str, optional): The name of the database. 
                                Defaults to os.getenv("DATABASE").
        """
        self.conn_params = {
            "host": host,
            "user": user,
            "port": port,
            "password": password,
            "database": database
        }
        self.connection = None
        _logger.info("Connection parameter: %s", self.conn_params)

    def create_connection(self) -> None:
        """
        Create a connection to the PostgreSQL database.
        """
        # Establish a connection to the database
        try:
            self.connection = psycopg2.connect(**self.conn_params)
            _logger.info("Connection to the PostgreSQL database established successfully")
        except Exception as e:
            _logger.info("Failed to establish connection" + str(e))
    def close_connection(self) -> None:
        """
        Close the connection to the PostgreSQL database.
        """
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        """
        Method to support 'with' statement.
        """
        self.create_connection()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Method to support 'with' statement. 
        Closes the connection when exiting the 'with' block.
        """
        self.close_connection()