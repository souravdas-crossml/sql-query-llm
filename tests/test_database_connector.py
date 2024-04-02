import pytest
from unittest.mock import Mock
from utils.database_connector import DatabaseConnector

@pytest.fixture
def connector():
    return DatabaseConnector()

def test_create_connection_success(connector):
    """
    Test creating a database connection successfully.
    """
    # Given
    connector.create_connection = Mock(return_value=None)
    
    # When
    connector.create_connection()
    
    # Then
    assert connector.connection is not None
    connector.logger.info.assert_called_with("Connection to the PostgreSQL database established successfully")

def test_create_connection_failure(connector):
    """
    Test failure in creating a database connection.
    """
    # Given
    connector.create_connection = Mock(side_effect=Exception("Connection failed"))
    
    # When
    connector.create_connection()
    
    # Then
    assert connector.connection is None
    connector.logger.info.assert_called_with("Failed to establish connection: Connection failed")

def test_close_connection(connector):
    """
    Test closing a database connection.
    """
    # Given
    connector.connection = Mock()
    
    # When
    connector.close_connection()
    
    # Then
    assert connector.connection is None
    connector.connection.close.assert_called_once()

def test_exit(connector):
    """
    Test closing a database connection using the context manager.
    """
    # Given
    connector.connection = Mock()
    
    # When
    with connector as conn:
        pass
    
    # Then
    assert connector.connection is None
    connector.connection.close.assert_called_once()
