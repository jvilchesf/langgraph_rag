import sqlite3
import os
import requests
from typing import Optional
from agent_sql.configuration import DatabaseConfiguration

from langchain_core.runnables import RunnableConfig

class database_utils:
    def get_schema(
            self,
            config: Optional[RunnableConfig] = None
    ):

        db_path = config.db_path

        schema = {}
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"The database file at {db_path} does not exist.")

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            for table_name in tables:
                table_name = table_name[0]
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                schema[table_name] = [(col[1], col[2]) for col in columns]

        return schema
    
    def execute_query(
                self,
                query: str,
                config: Optional[RunnableConfig] = None
        ):
            
            #Get sqlite file 
            db_path = config.db_path           
            if not os.path.exists(db_path):
                raise FileNotFoundError(f"The database file at {db_path} does not exist.")

            #Execute query
            try:
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(query)
                     # Fetch column names
                    results = cursor.fetchall()           
                    # Return both column results
                    return results
            except sqlite3.Error as e:
                raise Exception(f"Error executing query: {str(e)}")