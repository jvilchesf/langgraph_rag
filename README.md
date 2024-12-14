# Langchain & Langgraph Personal Project

## Overview
This personal project demonstrates how to use **Langchain** and **Langgraph** to unify and analyze banking transactions from three different CSV files. The process involves standardizing multilingual transactions and enabling a natural language interface for SQL queries against these records.

You’ll find two main flows:
1. **Retriever Flow** – Responsible for reading and merging different transaction CSV files, standardizing them, augmenting their data (e.g., auto-adding new columns), and creating an SQLite database.
2. **SQL Agent Flow** – Takes natural language queries and converts them into SQL queries executed against the SQLite database created in the Retriever Flow.

<div style="display: flex;">
  <img src="/images/portfolio_genAI_langgraph_graph_1.png" style="margin-right: 10px;">
  <img src="/images/portfolio_genAI_langgraph_graph_2.png">
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

## Steps
Below is a high-level workflow describing how the project works in two major flows:

### 1. Retriever Flow
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

### 2. SQL Agent Flow
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

---

## Folder Structure

images/ src/ ├─ agent_retriever/ │ ├─ files/ │ │ ├─ 20241122-4572815-umsatz.csv │ │ ├─ account-statement_2023-11-01_2024-11-10_en_78d98f.csv │ │ └─ account-statement_2023-11-01_2024-11-10_en-ie_e94656.csv │ ├─ init.py │ ├─ agent_retriever.py │ ├─ augmented_functions.py │ ├─ configration.py │ ├─ merged_csv.py │ ├─ prompt.py │ ├─ state.py │ └─ utils.py ├─ agent_sql/ │ ├─ agent_sql.py │ ├─ configuration.py │ ├─ database_utils.py │ ├─ database.py │ ├─ llm_manager.py │ ├─ prompt.py │ └─ state.py ├─ .env ├─ langgraph.json ├─ pyproject.tml └─ README.md


---

## Data Structure
The final DataFrame (after augmentation) will contain columns like:
- **Date**  
- **Description**  
- **Merchant**  
- **Product_service**  
- **Amount (EUR)**  
- **Currency**  
- **Transaction Type**  
- **Merchant Name**  
- **Merchant Category**  
- **Payment Method**  
- **Location**  
- **Recurring**  
- **Budget Category**  
- **Tags**  
- **Notes**  
- **Payment Status**

Once augmented, these records are stored in an SQLite database (`augmented_data.sqlite`) under a table named `transactions`.  

---

## Important Files

### **`agent_retriever.py`**
Defines the **Langgraph flow** for reading, merging, augmenting, and storing CSV data:
1. **standardize_csv:** Merges CSV files into a standardized DataFrame using `CSVHanlder`.
2. **augmented_data:** Augments the DataFrame by adding new columns (transaction type, merchant category, etc.) via an LLM.
3. **create_sqlite:** Writes the augmented DataFrame into an SQLite file.

### **`merged_csv.py`**
Contains logic in `CSVHanlder` for:
- Reading CSVs with different delimiters/encodings (German vs. English).
- Invoking an LLM prompt to map existing columns to standardized fields.
- Generating a final merged DataFrame.

### **`augmented_functions.py`**
Implements chunk-based augmentation. Splits the DataFrame into manageable chunks and uses a prompt to create additional columns (`Transaction Type`, etc.) in English.

### **`prompt.py` (within `agent_retriever`)**
Holds the prompt templates used to:
- Map CSV columns to standardized fields.
- Augment the data with new columns.

### **`agent_sql.py`**
Defines the **Langgraph flow** for parsing user questions, generating SQL, validating it, and executing it. The nodes are:
- **parse_query**: Checks if the question is relevant and identifies table/columns.
- **get_unique_nouns**: Fetches distinct values from relevant columns.
- **generate_sql**: Constructs an SQL query from the user question and discovered nouns.
- **validate_and_fix_sql**: Corrects table or column name errors.
- **execute_sql**: Executes the final SQL query and returns results.

### **`database.py` & `database_utils.py`**
- **`database.py`**: Manages steps involved in SQL query generation and execution.
- **`database_utils.py`**: Contains helper methods to retrieve the schema from the SQLite database and execute queries.

### **`llm_manager.py`**
Implements a manager class that interacts with the LLM (OpenAI Chat model). Used by both the Retriever flow and SQL flow for prompt engineering.

### **`configuration.py`**
Holds dataclasses that store configuration parameters, such as the database path or the model name. Each flow (retriever vs. SQL agent) has its own configuration class.

---

## Usage
1. **Clone the Repo**  
   ```bash
   git clone https://github.com/your-username/langchain-langgraph-bank-transactions.git

2. **Install Dependencies**

cd langchain-langgraph-bank-transactions
pip install -r requirements.txt

3. **Set Up Environment**
Create a .env file or specify environment variables as needed (e.g., for OpenAI credentials).

3. **Run the Retriever Flow**
Execute the agent_retriever.py flow to generate augmented_data.sqlite.

3. **Run the SQL Agent Flow**
Use agent_sql.py to run queries in natural language. The code will parse your question, build & fix SQL, then execute it.
