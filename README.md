# Langchain & Langgraph Personal Project

## Overview
This personal project demonstrates how to use **Langchain** and **Langgraph** to unify and analyze banking transactions from three different CSV files. The process involves standardizing multilingual transactions and enabling a natural language interface for SQL queries against these records.

You’ll find two main flows:
1. **Retriever Flow** – Responsible for reading and merging different transaction CSV files, standardizing them, augmenting their data (e.g., auto-adding new columns), and creating an SQLite database.
2. **SQL Agent Flow** – Takes natural language queries and converts them into SQL queries executed against the SQLite database created in the Retriever Flow.

<div style="display: flex;">
  <img src="/images/portfolio_genAI_langgraph_graph_1.png" style="margin-right: 10px;" width = 400 height = 500>
  <img src="/images/portfolio_genAI_langgraph_graph_2.png" width = 400 height = 500>
</div>

---

## Problem
Bank transactions often come in varied formats and languages. Some statements are in German with different delimiters and date formats, while others use English formatting. This inconsistent structure makes it challenging to analyze the data collectively or run aggregated queries.

**Key challenges include:**
1. Inconsistent CSV formats (delimiters, encoding).
2. Different languages (German vs. English).
3. Lack of a unified schema to store transactions from multiple sources.
4. Complex data augmentation (e.g., deriving extra columns like _Merchant Category_ or _Recurring_ from the text).
5. Natural language queries that need to be transformed accurately into SQL.

---

## Solution
1. **Merging & Standardizing Data:**  
   - Parse each CSV file regardless of its encoding or structure.  
   - Map columns to a standardized set of fields like `Date`, `Description`, `Merchant`, etc.  
   - **Langchain** is used to invoke an LLM that inspects CSV headers and maps them to a consistent schema.  
2. **Augmenting Data:**  
   - Automatically analyze transaction rows, add new columns such as `Transaction Type`, `Budget Category`, `Tags`, etc.  
   - Convert data into English as part of a uniform representation.  
3. **Creating a SQL Database:**  
   - Store the merged and augmented data in an SQLite database for easy querying.  
4. **SQL Agent:**  
   - Take a natural language question (e.g., *"What’s the total spending in November?"*).  
   - Parse the question for relevant columns, tables, and unique nouns.  
   - Convert the parsed question into a valid SQL query.  
   - Validate and fix the SQL query if needed.  
   - Execute the query against the SQLite database.  

**Langgraph** orchestrates these steps by defining computational flows (`StateGraph`) and chaining them neatly.

---


## Folder Structure

    images/
    src/
    ├─ agent_retriever/
    │   ├─ files/
    │   │   ├─ dummy1.csv
    │   │   ├─ dummy2.csv
    │   │   └─ dummy3.csv
    │   ├─ __init__.py
    │   ├─ agent_retriever.py
    │   ├─ augmented_functions.py
    │   ├─ configuration.py
    │   ├─ merged_csv.py
    │   ├─ prompt.py
    │   ├─ state.py
    │   └─ utils.py
    ├─ agent_sql/
    │   ├─ agent_sql.py
    │   ├─ configuration.py
    │   ├─ database.py
    │   ├─ database_utils.py
    │   ├─ llm_manager.py
    │   ├─ prompt.py
    │   └─ state.py
    ├─ .env
    ├─ langgraph.json
    ├─ pyproject.tml
    └─ README.md

---

# Agent retriever

## Files

- `__init__.py`: File created to trigger the entire process.
- `agent_retriever.py`: This is the main file of the process, where other important methods such as `standardize_csv`, `augmented_data`, and `create_sqlite` are called. The graph is also created here.
- `merged_csv.py`: This file defines the class responsible for merging the CSVs. Here is where the files are read, sent to the LLM to obtain standardized column names, and a first version of the data is sent to the next step in the flow in a DataFrame format. This class is called from `agent_retriever.py` in the `standardize_csv` function.
- `augmented_functions.py`: Here, a class is defined to take the already processed and standardized data and extract more valuable information based on it. The problem is that since these three files are different, when the columns are standardized, it is hard to infer new columns based on text. For example, a PayPal payment for a monthly Spotify subscription doesn’t straightforwardly reveal extra fields like marketplace, recurring payment, payment method, etc., unless you rely on a dictionary. Maintaining that dictionary can be time-consuming. This is where an LLM truly helps by accurately inferring new columns in a much simpler way.
- Function `create_sqlite` in `agent_retriever.py`: This is an important function to save the data in a .sql format to be queried later.
- `configuration.py`: This file defines process variables needed across multiple methods. Additionally, it contains an important function called `from_runnable_config`, which is used to retrieve these variables when needed.
- `prompt.py`: The prompt is very important; here, the queries and desired output from the LLM are defined. This is where the magic happens.
- `state.py`: States are structures of data that allow the saving of the answer of each step and communicate them to the next step. They are a very important part of the agents' workflows in langgraph.
- `utils.py`: File created to define an LLM function call.
igh-level workflow describing how the project works in two major flows:

### Retriever Flow
1. **Read CSV Files**:  
   - Inspect their encodings (some are semicolon-delimited, one is in German).
2. **Map Columns via LLM**:  
   - Use an LLM prompt to map non-standard column headers to uniform standardized fields (`Date`, `Amount (EUR)`, etc.).
3. **Concatenate Data**:  
   - Merge all CSV files into one DataFrame, preserving only standardized fields.
4. **Augment Data**:  
   - Split the DataFrame into chunks and pass them through an LLM prompt that translates the data to English and adds extra columns (`Transaction Type`, `Merchant Category`, etc.).
5. **Create SQLite Database**:  
   - Save the final, augmented DataFrame to an SQLite file for further querying.

# Agent Sql

## Files

- `agent_sql.py`:
    Defines the Langgraph flow for parsing user questions, generating SQL, validating it, and executing it. The nodes are:
        - parse_query: Checks if the question is relevant and identifies table/columns.
        - get_unique_nouns: Fetches distinct values from relevant columns.
        - generate_sql: Constructs an SQL query from the user question and discovered nouns.
        - validate_and_fix_sql: Corrects table or column name errors.
        - execute_sql: Executes the final SQL query and returns results.
-`database.py` & `database_utils.py`:
    -`database.py`: Manages steps involved in SQL query generation and execution.
    -`database_utils.py`: Contains helper methods to retrieve the schema from the SQLite database and execute queries.
-`llm_manager.py`: Implements a manager class that interacts with the LLM (OpenAI Chat model). Used by both the Retriever flow and SQL flow for prompt engineering.
-`prompt.py` (within `agent_retriever`): Map CSV columns to standardized fields and Augment the data with new columns.
- `configuration.py`: Holds dataclasses that store configuration parameters, such as the database path or the model name. Each flow (retriever vs. SQL agent) has its own configuration class.

## SQL Agent Flow
1. **Parse Natural Language Query**:  
   - Break down the user’s question to identify relevant tables and columns.  
2. **Discover Unique Nouns**:  
   - Identify unique nouns or important values from the relevant columns (e.g., merchant names).
3. **Generate SQL**:  
   - Use the parsed question plus the discovered nouns to generate an SQL query string via an LLM prompt.
4. **Validate & Fix SQL**:  
   - Double-check the generated SQL against the known schema; fix any errors in table or column names.
5. **Execute SQL**:  
   - Run the validated SQL query against the SQLite database and return the results.


