"""
Chroma Document Collection

This module provides a class for interacting with ChromaDB and managing document collections.

Dependencies:
- chromadb: Provides the HttpClient class for interacting with ChromaDB.
- chromadb.config: Provides the Settings class for configuring ChromaDB settings.
- logging: Provides functionality for logging.
- typing: Provides support for type hints.
- dotenv: Provides functionality for loading environment variables from .env files.
- os: Provides functions for interacting with the operating system.

Usage:
1. Instantiate the ChromaDocumentCollection class with the required parameters.
2. Call the get_document_collection method to retrieve or create a document collection from ChromaDB.
"""
# Import depemdencies
import os
import logging
from typing import Optional
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings

# Configure logging
from .logger import create_logger
_logger = create_logger("chroma_client")

class ChromaDocumentCollection:
    """
    A class to interact with ChromaDB and manage document collections.

    Attributes:
        chroma_client (chromadb.HttpClient): An HTTP client for interacting with ChromaDB.
        collection (Optional[DocumentCollection]): The document collection object.
    """

    def __init__(self) -> None:
        """
        Initializes the ChromaDocumentCollection.

        It loads the host and port from environment variables and creates the ChromaDB HTTP client.
        """

        # Get host and port from environment variables
        self.host: str = os.getenv("CHROMA_HOST", "localhost")
        self.port: int = int(os.getenv("CHROMA_PORT", "8005"))

        # Create ChromaDB HTTP client
        try:
            self.chroma_client = chromadb.HttpClient(
                host=self.host,
                port=self.port,
                settings=Settings(
                    allow_reset=True,
                    anonymized_telemetry=False
                )
            )
        except Exception as e:
            _logger.error(f"Failed to create ChromaDB HTTP client: {e}")
            raise e
        self.collection: Optional[chromadb.DocumentCollection] = None

    def get_document_collection(self, 
                                collection_name: str = os.getenv(
                                "CHROMA_COLLECTION")
                                ) -> chromadb.DocumentCollection:
        """
        Get or create a document collection from ChromaDB.

        Args:
            collection_name (str, optional): The name of the collection. Defaults to os.getenv("CHROMA_COLLECTION").

        Returns:
            chromadb.DocumentCollection: The document collection object.
        """
        if self.collection is None:
            while True:
                try:
                    self.collection = self.chroma_client.get_or_create_collection(
                        name=collection_name
                    )
                    break
                except Exception as e:
                    _logger.error(f"Failed to get or create document collection: {e}")
                    pass

        return self.collection
