"""
"""
from typing import List, Tuple, Dict, Union
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

    def insert_data(self, queries_data: List[Tuple[str, Tuple]]) -> None:
        """
        Insert data into the PostgreSQL database.

        Args:
            queries_data (list): List of tuples containing (query, data) pairs to be inserted.
        """
        try:
            self.connector.create_connection()
            cursor = self.connector.connection.cursor()
            for query, data in queries_data:
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
            _logger.info("Connection to the PostgreSQL database closed successfully")
            
    def insert_single_query_data(self, query: str, data: Tuple) -> None:
        """
        Insert data into the PostgreSQL database for a single a query.

        Args:
            query (str): Insert query for the data
            data (Tuple): Data to be inserted.
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
            _logger.info("Connection to the PostgreSQL database closed successfully")




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


class DataParser:
    """
    This class provides methods for parsing data from nested dictionary output from Gemini Vision Pro.
    
    """
        
    def extract_items(self, data: Dict) -> Dict[str, any, List[Dict[str, any]]]:
        """
        Extracts invoice details and items from the provided data dictionary.

        Returns:
            dict: A tuple containing the extracted invoice details dictionary.
            list" A list containing the extracted items details dictionary.
        """
        invoice_details = {
            "invoice_number": data["invoice_number"],
            "invoice_date": data["invoice_date"],
            "client_name": data["client_name"],
            "client_address": data["client_address"],
            "client_tax_id": data["client_tax_id"],
            "seller_name": data["seller_name"],
            "seller_address": data["seller_address"],
            "seller_tax_id": data["seller_tax_id"],
            "invoice_iban": data["invoice_iban"]
        }
        
        items = data["items"]
        total = data["Total"]
        
        # Flatten Total and add to invoice_details
        for key, value in total.items():
            invoice_details[f"{key}"] = value
        
        return invoice_details, items
    
    def ParseData(self, data: Dict) -> Union[Tuple, Tuple]:
        """_summary_

        Returns:
            Union[Tuple, Tuple]: _description_
        """
        
        invoice_details, items = self.extract_items(data)
        
        invoice_no = invoice_details.get('invoice_number', '')
        date_of_issue = invoice_details.get('invoice_date', '')
        seller_name = invoice_details.get('seller_name', '')
        seller_address = invoice_details.get('seller_address', '')
        seller_tax_id = invoice_details.get('seller_tax_id', '')  
        seller_iban = invoice_details.get('invoice_iban', '')  
        client_name = invoice_details.get('client_name', '')
        client_address = invoice_details.get('client_address', '')
        client_tax_id = invoice_details.get('client_tax_id', '')
        net_worth = invoice_details.get('net_worth', '')
        vat = invoice_details.get('vat', '')
        gross_worth = invoice_details.get('gross_worth', '')
        
        invoice_info = replace_empty_with_null(
            (
                invoice_no, 
                date_of_issue, 
                seller_name, 
                seller_address, 
                seller_tax_id, 
                seller_iban, 
                client_name, 
                client_address, 
                client_tax_id, 
                net_worth, 
                vat, 
                gross_worth
            )
        )
        
        item_list = []
        item_tuple = ()
        for item in items:
            item_tuple = (
                item["description"],
                item["quantity"],
                item["unit"],
                item["net_price"],
                item["net_worth"],
                item["gross_worth"]
            )
            item_list.append(
                self.replace_empty_with_null(item_tuple)
            )
        
        return tuple([invoice_info], item_list)

    def replace_empty_with_null(self, input_tuple):
        """
        Replace empty strings in a tuple with NULL.

        Args:
            input_tuple (tuple): Input tuple to be processed.

        Returns:
            tuple: Tuple with empty strings replaced by NULL.
        """
        return tuple(None if value == '' else value for value in input_tuple)
