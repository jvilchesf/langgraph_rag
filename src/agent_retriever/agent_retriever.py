import os
import sqlite3
import pandas as pd
from io import StringIO
from typing import Optional


from agent_retriever.configuration import RetrieverConfiguration
from agent_retriever.merge_csv import CSVHanlder
from agent_retriever.state import ShareState
from agent_retriever.augmented_functions import AugmentedData

from langchain_core.runnables import RunnableConfig
from langchain_core.documents import Document
from langgraph.graph import StateGraph, START, END

async def standardize_csv(
        state: ShareState,
        config: Optional[RunnableConfig] = None
) -> list[Document]:
    
    config = RetrieverConfiguration.from_runnable_config(config)
    path_folder = config.path_folder
    csv_handler = CSVHanlder()
    df_merged = csv_handler.merge_files(path_folder, config)

    #return {"Content": df_merged.to_string(), "ProcessStatus":"standarize_csv_done"}
    return {"Content": [df_merged], "ProcessStatus":"standarize_csv_done"}

async def augmented_data(
        state: ShareState,
        config: Optional[RunnableConfig] = None
):
    # Config
    config = RetrieverConfiguration.from_runnable_config(config)
    # Call function to augment data
    content = state.Content[0]

    augmented_data = AugmentedData()

    df_augmented = augmented_data.apply_augmentation(content, config) 

    if df_augmented is None:
        # Handle the case where augmentation fails
        return {"Content": [], "ProcessStatus": "augmentation_failed"}

    #return {"Content": df_augmented.to_string(), "ProcessStatus":"augmented_data_done"}
    return {"Content": [df_augmented], "ProcessStatus":"augmented_data_done"}
    


import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_sqlite(
        state: ShareState,
        config: Optional[RunnableConfig] = None
):
    try:
        df = state.Content[0]
        if df.empty:
            raise ValueError("state.Content is empty")
        
        logger.info("Starting SQLite creation process.")

        # Define the path to the SQLite database file in the mounted data directory
        db_filename = 'augmented_data.sqlite'
        db_destinny = 'src/agent_retriever/data'
        db_path = os.path.join(db_destinny, db_filename)

        print(f"{df.info()=}")

        # Create a connection to the SQLite database file
        with sqlite3.connect(db_path) as conn:
            # Write the DataFrame to a SQLite table
            df.to_sql('transactions', conn, if_exists='replace', index=False)
            logger.info(f"DataFrame successfully written to table 'transactions' in {db_filename}")

        return {"Content": "SQLite database created successfully", "ProcessStatus": "sqlite_creation_done"}
    
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        return {"Content": "Failed to create SQLite database", "ProcessStatus": "sqlite_creation_failed"}


#Model
builder = StateGraph(ShareState, config_schema=RetrieverConfiguration)
#Nodes
builder.add_node(standardize_csv)
builder.add_node(augmented_data)
builder.add_node(create_sqlite)
#Edges
builder.add_edge(START, 'standardize_csv')
builder.add_edge('standardize_csv', 'augmented_data')
builder.add_edge('augmented_data','create_sqlite')
builder.add_edge("create_sqlite", END)
#Compile
graph = builder.compile()

