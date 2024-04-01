"""Load testing script for the SQL Query API and Vector Query API using Locust."""

from locust import HttpUser, task, between

class QueryUser(HttpUser):
    """
    Locust user class for load testing the SQL Query API and Vector Query API.

    Attributes:
        wait_time (tuple): Tuple representing the range of time between consecutive requests.
    """

    wait_time = between(1, 5)  # Time between consecutive requests

    @task
    def query_database(self) -> None:
        """
        Task to simulate a user querying the database using the SQL Query API.

        Returns:
            None
        """
        try:
            input_text = "Select invoice no where the grossworth is greater than 100."
            response = self.client.post("/sqlQuery", json={"text": input_text})
            if response.status_code != 200:
                print(f"SQL Query request failed with status code: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"An error occurred during SQL Query: {e}")
            
    @task
    def query_vectorDB(self) -> None:
        """
        Task to simulate a user querying the VectorDB using the Vector Query API.

        Returns:
            None
        """
        try:
            input_text = "Query VectorDB for relevant information."
            response = self.client.post("/vectorQuery", json={"text": input_text})
            if response.status_code != 200:
                print(f"Vector Query request failed with status code: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"An error occurred during Vector Query: {e}")
