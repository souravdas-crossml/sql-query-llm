"""
"""
from typing import List, Tuple
from .database_connector import DatabaseConnector
from .logger import create_logger
_logger = create_logger("DBWriter")

class DBWriter:
    """
    This class provides methods for inserting data into a PostgreSQL database.
    """

    def __init__(self, connector: DatabaseConnector) -> None:
        """
        Initialize the DataInserter with a DatabaseConnector instance.

        Args:
            connector (DatabaseConnector): An instance of DatabaseConnector.
        """
        self.connector = connector

    def insert_data(self, query: str, data: tuple) -> None:
        """
        Insert data into the PostgreSQL database.

        Args:
            query (str): The SQL query to execute for insertion.
            data (tuple): Tuple containing the data to be inserted.
        """
        try:
            self.connector.create_connection()
            cursor = self.connector.connection.cursor()
            cursor.execute(query, data)
            self.connector.connection.commit()
            _logger.info("Data inserted successfully")
        except Exception as e:
            _logger.error("Failed to insert data: " + str(e))
            if self.connector.connection:
                self.connector.connection.rollback()  # Rollback changes if insertion fails
        finally:
            if cursor:
                cursor.close()
            self.connector.close_connection()



class SQLQueryBuilder:
    """
    This class provides methods for building SQL queries to insert multiple records into a PostgreSQL database.
    """

    @staticmethod
    def build_insert_query(table_name: str, columns: tuple) -> str:
        """
        Build an SQL INSERT query for a given table and columns.

        Args:
            table_name (str): The name of the table to insert into.
            columns (tuple): Tuple containing the column names.

        Returns:
            str: The generated SQL INSERT query.
        """
        columns_str = ', '.join(columns)
        placeholders_str = ', '.join(['%s'] * len(columns))
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders_str})"
        return query



def PrepareData(mergedData) -> List[Tuple[str]]:
    data = []
    for item in mergedData:
        # Extract relevant information
        invoice_no = item.get('invoice_no', '')
        date_of_issue = item.get('date_of_issue', '')
        seller_name = item.get('seller', {}).get('name', '')
        seller_address = item.get('seller', {}).get('address', '')
        seller_tax_id = item.get('seller', {}).get('tax_id', '')  
        seller_iban = item.get('seller', {}).get('iban', '')  
        client_name = item.get('client', {}).get('name', '')
        client_address = item.get('client', {}).get('address', '')
        client_tax_id = item.get('client', {}).get('tax_id', '')  

        # Iterate over each item in the 'items' list
        for item_info in item.get('items', []):
            invoice_tuple_data = (
                invoice_no,
                date_of_issue,
                seller_name,
                seller_address,
                seller_tax_id,
                seller_iban,
                client_name,
                client_address,
                client_tax_id,
                item_info.get('description', ''),
                item_info.get('quantity', ''),
                item_info.get('unit_of_measure', ''),
                item_info.get('net_price', ''),
                item_info.get('net_worth', ''),
                item_info.get('vat', ''),
                item_info.get('gross_worth', '')
            )
            invoice_tuple_data = replace_empty_with_null(invoice_tuple_data)
            data.append(invoice_tuple_data)

    return data

def replace_empty_with_null(input_tuple):
    """
    Replace empty strings in a tuple with NULL.

    Args:
        input_tuple (tuple): Input tuple to be processed.

    Returns:
        tuple: Tuple with empty strings replaced by NULL.
    """
    return tuple(None if value == '' else value for value in input_tuple)
