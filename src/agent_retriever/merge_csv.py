from dataclasses import dataclass

import os
import chardet
import pandas as pd
import json

from agent_retriever import prompt
from agent_retriever import utils

from langchain_core.messages import AIMessage, AnyMessage
from langchain_core.runnables import RunnableConfig

@dataclass
class CSVHanlder:

    def csv_to_df(
        self,        
        file_path: str,
        file_encoding: str):
        """
        Method to return a csv file as a dataframe

        Args:
        file_enconding: str containing file encoding format
        file_path: str containing file path
        """
        # Initialize df to None
        df = None

        # Read the CSV with the detected encoding
        try:
            if "umsatz" in file_path:  
                df = pd.read_csv(
                    file_path,
                    delimiter=';',          # Use semicolon as the delimiter
                    quotechar='"',          # Fields are enclosed in double quotes
                    encoding='latin1',      # Encoding for German characters
                    decimal=',',            # Comma as decimal separator
                    parse_dates=['Buchungstag', 'Valutadatum'],  # Parse date columns
                    dayfirst=True,           # Day comes first in date format
                    date_format='%d.%m.%Y'   # Specify the date format
                )
            else:
                df = pd.read_csv(file_path, encoding=file_encoding)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
        return df
    
    def call_llm(
        self,
        column_names: str,
        response_model: str
    ) -> AIMessage:
        
        standard_fields = prompt.standard_fields
        output_example = prompt. output_example
        p = prompt.prompt.format(headers = column_names, standard_fields = standard_fields, output_example = output_example)
        model = utils.load_chat_model(response_model)
        response = model.invoke(p)
        return response.content

    def merge_files(
        self,
        path_folder: str,
        config: RunnableConfig        
    ) -> AnyMessage:
    
        # Response model
        response_model = config.response_model
        #List of df 
        standardized_dfs = []

        for file in os.listdir(path_folder):
            
            if file.endswith('.csv'):
                file_path = os.path.join(path_folder, file)
                print(f"Processing file: {file}")

                # Detect file encoding
                with open(file_path, 'rb') as f:
                    result = chardet.detect(f.read())
                file_encoding = result['encoding']

                if not file_encoding:
                    print(f"Could not detect encoding for {file_path}. Skipping file.")

                df = self.csv_to_df(file_path, file_encoding)
                if df is None:
                    print(f"Failed to read {file_path}. Skipping file.")

                column_names = df.columns
                # call llm
                response = self.call_llm(column_names, response_model)

                #transform to dict
                mapping = json.loads(response)

                # Create a new DataFrame with standardized fields
                new_df = pd.DataFrame()

                # Map each column in the mapping to the new DataFrame
                for std_field, csv_column in mapping.items():
                    if csv_column in df.columns:
                        new_df[std_field] = df[csv_column]
                    else:
                        # If the column is not in df, fill with None or appropriate default
                        new_df[std_field] = None

                # Append the new DataFrame to the list
                standardized_dfs.append(new_df)
            else:
                print(f"error has ocurred with the file: {file}")
        
        
        # Concatenate all standardized DataFrames into a final DataFrame
        if standardized_dfs:
            final_df = pd.concat(standardized_dfs, ignore_index=True)
            print("Final DataFrame created successfully.")
        else:
            final_df = pd.DataFrame(columns=prompt.standard_fields)
            print("No data to process.")

        return final_df