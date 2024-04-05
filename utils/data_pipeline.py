"""
"""

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
            cursor.executemany(query, data)
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


class DataProcessor:
    """
    This class provides methods for preparing data inin the specified schema.
    """
    def __init__(self, mergedData: List[Dict[str, str]]) -> None:
        """_summary_

        Args:
            schema (Dict[str, str]): _description_
            mergedData (List[Dict[str, str]]): _description_
        """
        self.mergedData = mergedData
        
        def _prepare_data(self)->List[Dict[str, str]]:
            """_summary_

            Returns:
                List[Dict[str, str]]: _description_
            """
            data = []
            for item in merged_json:
                # Extract relevant information
                invoice_no = item.get('invoice_no', '')
                date_of_issue = item.get('date_of_issue', '')
                seller_name = item.get('seller', {}).get('name', '')
                seller_address = item.get('seller', {}).get('address', '')
                seller_tax_id = item.get('seller', {}).get('tax_id', '')  # Remove .get() method
                seller_iban = item.get('seller', {}).get('iban', '')  # Use .get() method to handle missing key
                client_name = item.get('client', {}).get('name', '')
                client_address = item.get('client', {}).get('address', '')
                client_tax_id = item.get('client', {}).get('tax_id', '')  # Use .get() method to handle missing key
                # Iterate over each item in the 'items' list
                for item_info in item.get('items', []):
                    data.append({
                        'Invoice No.': invoice_no,
                        'Date of Issue': date_of_issue,
                        'Seller Name': seller_name,
                        'Seller Address': seller_address,
                        'Seller Tax ID': seller_tax_id,
                        'Seller IBAN': seller_iban,
                        'Client Name': client_name,
                        'Client Address': client_address,
                        'Client Tax ID': client_tax_id,
                        'Description': item_info.get('description', ''),
                        'Quantity': item_info.get('quantity', ''),
                        'Unit of Measure': item_info.get('unit_of_measure', ''),
                        'Net Price': item_info.get('net_price', ''),
                        'Net Worth': item_info.get('net_worth', ''),
                        'VAT': item_info.get('vat', ''),
                        'Gross Worth': item_info.get('gross_worth', '')
                    })