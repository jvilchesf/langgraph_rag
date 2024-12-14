from agent_sql.database_utils import database_utils
from agent_sql import prompt
from agent_sql.llm_manager import LlmManager
from agent_sql.configuration import DatabaseConfiguration

from langchain_core.output_parsers import JsonOutputParser

class DataBaseManager:
    def __init__(self):
        self.db_utils = database_utils()
        self.llm_manager = LlmManager()


    def parse_query(
            self,
            state: dict
    ) -> str:
        
        config = DatabaseConfiguration.from_runnable_config()
        #User initial query
        question = state['question']

        #get schema
        schema = self.db_utils.get_schema(config)

        #set prompt
        p = prompt.PARSE_QUERY_PROMPT.format(schema = schema, question = question)

        #invoke model
        response = self.llm_manager.call_llm(p, config)

        #pase response
        output_parser = JsonOutputParser()
        parsed_response = output_parser.parse(response)

        return {"parsed_question":parsed_response}

    def get_unique_nouns(
            self,
            state: dict
    ) -> dict:
        """find unique nouns in relevat tables and columns"""

        #get config parameters
        config = DatabaseConfiguration.from_runnable_config()

        # get parsed question dict
        parsed_question = state['parsed_question']

        #check if the answer is relevant
        if not parsed_question['is_relevant']:
            return {"unique_nouns": []}

        unique_nouns = set()
        #go trough the tables
        for table_info in parsed_question['relevant_tables']:
            table_name = table_info['table_name']
            noun_columns = table_info['noun_columns']
            columns = table_info['columns']

            if noun_columns:
                        column_names = ', '.join(f"`{col}`" for col in noun_columns)
                        query = f"SELECT DISTINCT {column_names} FROM {table_name} GROUP BY {column_names}"
                        #query = f"SELECT * FROM {table_name};"
                        results = self.db_utils.execute_query(query, config)
                        if results is None:
                            print("Query execution returned no results.")
                            continue

                        for row in results:
                            unique_nouns.update(str(value) for value in row if value)

        return {"unique_nouns": list(unique_nouns)}

    def generate_sql(
            self,
            state:dict        
    ) -> dict:
        """Generate SQL query based on parsed question and unique nouns."""
        
        #get config parameters
        config = DatabaseConfiguration.from_runnable_config()

        question = state['question']
        parsed_question = state['parsed_question']
        unique_nouns = state['unique_nouns']

        #check relevancy
        if not parsed_question['is_relevant']:
            return {"sql_query": "NOT_RELEVANT", "is_relevant": False}
    
        #get schema
        schema = self.db_utils.get_schema(config)

        #format prompt
        p = prompt.GENERATE_SQL_PROMPT.format(schema = schema, question = question, parsed_question = parsed_question, unique_nouns = unique_nouns)

        #call llm
        response = self.llm_manager.call_llm(p, config)

        if response.strip() == "NOT_ENOUGH_INFO":
            return {"sql_query": "NOT_RELEVANT"}
        else:
            return {"sql_query": response}
        
    def validate_and_fix_sql(self,
                            state: dict
    ) -> dict:
        """Validate and fix the generated SQL query."""
        
        #get config parameters
        config = DatabaseConfiguration.from_runnable_config()
        
        sql_query = state['sql_query']

        if sql_query == "NOT_RELEVANT":
            return {"sql_query": "NOT_RELEVANT", "sql_valid": False}
        
        schema = self.db_utils.get_schema(config)
        p = prompt.VALIDATE_FIX_SQL_PROMPT.format(schema = schema, sql_query = sql_query)
        
        #call llm
        response =self.llm_manager.call_llm(p, config)

        #parse response
        output_parser = JsonOutputParser()
        result = output_parser.parse(response)

        if result["valid"] and result["issues"] is None:
            return {"sql_query": sql_query, "sql_valid": True}
        else:
            return {
                "sql_query": result["corrected_query"],
                "sql_valid": result["valid"],
                "sql_issues": result["issues"]
            }
        
    def execute_sql(
            self, 
            state: dict
    ) -> dict:
        
        """Execute SQL query and return results."""
        query = state['sql_query']
        
        if query == "NOT_RELEVANT":
            return {"results": "NOT_RELEVANT"}

        try:
            config = DatabaseConfiguration.from_runnable_config()
            results = self.db_utils.execute_query(query, config)
            return {"results": results}
        except Exception as e:
            return {"error": str(e)}