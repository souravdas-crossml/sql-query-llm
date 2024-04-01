from unittest.mock import MagicMock
from utils.database_connector import DatabaseConnector

def test_create_connection_success():
    """
    Test creating a database connection successfully.
    """
    # Given
    connector = DatabaseConnector()
    connector.create_connection = MagicMock(return_value=None)
    
    # When
    connector.create_connection()
    
    # Then
    assert connector.connection is not None
    connector.logger.info.assert_called_with("Connection to the PostgreSQL database established successfully")

def test_create_connection_failure():
    """
    Test failure in creating a database connection.
    """
    # Given
    connector = DatabaseConnector()
    connector.create_connection = MagicMock(side_effect=Exception("Connection failed"))
    
    # When
    connector.create_connection()
    
    # Then
    assert connector.connection is None
    connector.logger.info.assert_called_with("Failed to establish connection: Connection failed")

def test_close_connection():
    """
    Test closing a database connection.
    """
    # Given
    connector = DatabaseConnector()
    connector.connection = MagicMock()
    
    # When
    connector.close_connection()
    
    # Then
    assert connector.connection is None
    connector.connection.close.assert_called_once()

def test_exit():
    """
    Test closing a database connection using the context manager.
    """
    # Given
    connector = DatabaseConnector()
    connector.connection = MagicMock()
    
    # When
    with connector as conn:
        pass
    
    # Then
    assert connector.connection is None
    connector.connection.close.assert_called_once()
