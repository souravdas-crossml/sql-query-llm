"""
This module provides a document loader class that loads documents from a directory, splits them into chunks of text, 
creates embeddings using a specified model, and stores the embeddings in a vector store.

Dependencies:
- langchain.embeddings: Provides the HuggingFaceEmbeddings class for creating embeddings.
- langchain.text_splitter: Provides the RecursiveCharacterTextSplitter class for splitting text into chunks.
- langchain.vectorstores: Provides the FAISS class for creating the vector store.
- typing.List: Used for type hinting the return value of the text_splitter function.

Usage:
1. Instantiate the VectorQueryFromDirectory class with the required parameters.
2. Call the query_vectorDB method to query the vector DB (ChromaDB in this case) using the provided query.
"""

import logging
from typing import List
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA


# Configure logging
from .logger import create_logger
_logger = create_logger("VectorQuery")


class VectorQueryFromDirectory:
    """
    A class to query a vector DB (ChromaDB) using embeddings created from text chunks.
    """

    def __init__(self,
                 embedding_model_name: str,
                 embedding_model_kwargs: dict,
                 vectorDB_directory: str,
                 llm: any,
                 query: str, 
                 chunk_size: int = 1000) -> None:
        """
        Initializes the VectorQueryFromDirectory object with the specified parameters.

        Args:
            embedding_model_name (str): Name of the embedding model to be used.
            embedding_model_kwargs (dict): Keyword arguments for the embedding model.
            vectorDB_directory (str): Directory path for storing the vector store.
            llm (any): The Language Learning Model.
            query (str): The query string.
            chunk_size (int, optional): Size of the document chunks to be processed. Defaults to 1000.
        """
        self._chunk_size = chunk_size
        self._embedding_model_name = embedding_model_name
        self._embedding_model_kwargs = embedding_model_kwargs
        self._llm = llm
        self._query = None
        self._vectorDB_directory = vectorDB_directory
    
    def create_embedding(self) -> HuggingFaceEmbeddings:
        """
        Creates embeddings using the specified model and model_kwargs.

        Returns:
            HuggingFaceEmbeddings: Embeddings created by the specified model.
        """
        embeddings = HuggingFaceEmbeddings(
            model_name=self._embedding_model_name, 
            model_kwargs=self._embedding_model_kwargs
        )
        return embeddings
    
    def text_splitter(self) -> List[str]:
        """
        Splits the input query into chunks of text.

        Returns:
            List[str]: A list of strings representing the split text chunks.
        """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._chunk_size,
            chunk_overlap=100
        )
        chunks = splitter.split_text(self._query)
        return chunks

    def query_vectorDB(self):
        """
        Query the vector DB (ChromaDB) using embeddings created from text chunks.

        Returns:
            any: The response from the Language Learning Model.
        """
        vectordb = Chroma(
            persist_directory=self._vectorDB_directory, 
            embedding_function=self.create_embedding()
        )
        
        prompt_template="""
        Use the following pieces of information to answer the user's question.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.

        Context: {context}
        Question: {question}

        Only return the helpful answer below and nothing else.

        """
        
        prompt = PromptTemplate(
            template=prompt_template, 
            input_variables=["context", "question"]
        )
        
        chain_type_kwargs={"prompt": prompt}
        
        try:
            return RetrievalQA.from_chain_type(
                llm=self._llm, 
                chain_type="stuff", 
                retriever=vectordb.as_retriever(search_kwargs={'k': 3}),
                return_source_documents=True, 
                chain_type_kwargs=chain_type_kwargs
            )
            _logger.info("Created retrival agent for chroma DB successfully.")
        except Exception as e:
            _logger.error(f"Failed to query vector DB: {e}")
            return None
