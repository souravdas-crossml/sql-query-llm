"""

"""

from typing import List

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains.query_constructor import parser
from langchain_community.llms import CTransformers
from abc import ABC, abstractmethod

from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


table_schema = """
{
  "invoice_no": "string",
  "date_of_issue": "string",
  "seller": {
    "name": "string",
    "address": "string",
    "tax_id": "string",
    "iban": "string"
  },
  "client": {
    "name": "string",
    "address": "string",
    "tax_id": "string"
  },
  "items": [
    {
      "description": "string",
      "quantity": "string",
      "unit_of_measure": "string",
      "net_price": "string",
      "net_worth": "string",
      "vat": "string",
      "gross_worth": "string"
    }
  ],
  "summary": {
    "vat": "string",
    "net_total": "string",
    "vat_total": "string",
    "gross_total": "string"
  }
}
"""

schema_description = """
Here is the description to determine what each key represents:
1. **invoice_no**:
    - Description: Invoice number.
2. **date_of_issue**:
    - Description: Date of invoice issuance.
3. **seller**:
    - Description: Information about the seller.
      - **name**: Name of the seller.
      - **address**: Address of the seller.
      - **tax_id**: Tax identification number of the seller.
      - **iban**: IBAN of the seller.
4. **client**:
    - Description: Information about the client.
      - **name**: Name of the client.
      - **address**: Address of the client.
      - **tax_id**: Tax identification number of the client.
5. **items**:
    - Description: List of items in the invoice.
      - **description**: Description of the item.
      - **quantity**: Quantity of the item.
      - **unit_of_measure**: Unit of measurement of the item.
      - **net_price**: Net price of the item.
      - **net_worth**: Net worth of the item.
      - **vat**: VAT percentage of the item.
      - **gross_worth**: Gross worth of the item.
6. **summary**:
    - Description: Summary of the invoice.
      - **vat**: VAT percentage.
      - **net_total**: Net total amount.
      - **vat_total**: VAT total amount.
      - **gross_total**: Gross total amount.
"""

input_variable = [
            "user_message", 
        ]
            
template = """
    Create a MongoDB raw query for the following user question: 
    ###{user_message}###
    
    This is table schema : "{table_schema}"
    This is schema  description : {schema_description}
    """

# Initialize the language model for SQL queries.
llm = CTransformers(
    model = "model/mistral-7b-instruct-v0.1.Q3_K_L.gguf",
    model_type="llama",
    config={
        'max_new_tokens': 2048,  # Set the maximum number of tokens here
        'temperature': 0
    }
)

    
# class BaseChain(ABC):

#     def __init__(self, llm, **kwargs) -> None:
#         self.llm = llm

#     @property
#     @abstractmethod
#     def template(self) -> str:
#         """Template String that is required to build PromptTemplate"""
#         pass

#     @property
#     @abstractmethod
#     def input_variables(self) -> List[str]:
#         """Array of strings that are required as variable inputs for placeholders in template"""
#         pass

#     @staticmethod
#     @abstractmethod
#     def populate_input_variables(payload) -> dict:
#         """Populate the input variables by using the provided payload"""
#         pass

#     @abstractmethod
#     def partial_variables(self) -> dict:
#         """Populate partial variables while creating the chain"""
#         pass

#     @abstractmethod
#     def chain(self) -> LLMChain:
#         """Create and return LLM Chain"""
#         pass
    
# class Response(BaseModel):
#   query: list = Field(description="It must be a list")

#   def to_dict(self):
#     return self.query

# parser = PydanticOutputParser(pydantic_object=Response)

class MongoQueryBuilder:
    def __init__(self, llm, payload) -> None:
        self.llm = llm
        self.payload = payload

    def template(self) -> str:
        return template

    def input_variables(self) -> List[str]:
        return 
        
    def populate_partial_variables(self, payload: dict) -> dict:
        return {
            "user_message": payload["question"],
            "schema_description": schema_description,
            "table_schema" : table_schema
        }

    def chain(self):
        chain_prompt = PromptTemplate(
            input_variables=input_variable,
            template=template,
            partial_variables=self.populate_partial_variables(),
        )
        
        query_builder_agent = LLMChain(
            llm=self.llm,
            prompt=chain_prompt,
        )
        
        mongo_query = query_builder_agent.invoke_chain(payload["user_message"])
        return str(mongo_query)


# Example payload for query generation
payload = {
    "user_message": "What are the top-selling items by quantity?",
}

# Generate and run the query
query = MongoQueryBuilder(llm=llm, payload=payload)
print(query)