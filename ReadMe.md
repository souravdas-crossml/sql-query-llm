# Language Learning Model for SQL Query Generation

This project provides a API/function to invoke a Language Learning Model (LLM) for generating SQL queries and executes them in the PostgreSQL DB based on given text inputs. It also includes API/functions that searches information in the Vector DB (Chroma DB).
It utilizes the LangChain library for building and interacting with language-based AI models.

## Dependencies

- [LangChain](https://www.langchain.com/): A library for building and interacting with language-based AI models.
- [SQL Model](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF): Mistral model is used for generating SQL queries.
- [VectorDB Query Model](https://huggingface.co/google/flan-t5-large): Flan t5 model is used for query Vector DB.
- [ChromaDB](https://www.trychroma.com/): Vector Database to store text embeddings.
- [Sentence-transformer models](https://www.sbert.net/docs/pretrained_models.html): Sentence transformer models used for creating text embeddings.
- [PostgreSQL](https://www.postgresql.org/): RDBMS for saving information that is to be queried by SQL model. 




## Run Locally

Clone the project
```bash
  git clone https://github.com/souravdas-crossml/sql-query-llm.git
```

Go to the project directory
```bash
  cd sql-llm
```

Create model folder and paste the downloaded folder by following the link.
```bash
    mkdir model
```

Create python environment
```bash
    python -m venv my_env
```

Activate python environment
```bash
    source my_env/bin/activate
```

Install dependencies
```bash
    pip install -r requirements.txt
```

Load environment variables
```bash
    source .env
```

Start the server
```bash
  uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**NOTE:** Download and copy the model into the model directory from [here](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/tree/main).
**NOTE:** Edit the .env file accoringly.


## API Reference

#### Check Connection

```http
  GET /
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| None | None | Checks if the connection works for the Web servers |

#### Query SQL Database

```http
  Post /sqlQuery
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `input_text`      | `string` | **Required**. Required. The input text for the query.|


#### Query Vector Database

```http
  Post /vectorQuery
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `input_text`      | `string` | **Required**. Required. The input text for the query.|