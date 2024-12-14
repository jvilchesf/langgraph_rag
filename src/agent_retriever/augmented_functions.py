from typing import Optional
import pandas as pd
from io import StringIO

from agent_retriever.state import ShareState
from agent_retriever import prompt
from agent_retriever import utils

from langchain_core.runnables import RunnableConfig

class AugmentedData:
    
    def chunk_data(self, df, chunk_size: int):
        """
        Splits the given DataFrame into smaller chunks.

        Args:
        dataframe (pd.DataFrame): The DataFrame to be chunked.

        Returns:
        list[pd.DataFrame]: A list of DataFrame chunks.
        """
        # Example implementation: split the DataFrame into chunks of 100 rows
       
        chunks = [df[i:i + chunk_size] for i in range(0, df.shape[0], chunk_size)]
        return chunks

    
        # Function to preprocess the markdown table
    def preprocess_markdown_table(self, markdown: str) -> str:
        """
        Preprocess the markdown table by removing leading/trailing pipes, stripping whitespace,
        and removing the separator line.

        Args:
            markdown (str): The raw markdown table as a string.

        Returns:
            str: The cleaned markdown table ready for parsing.
        """
        # Split into lines
        lines = markdown.strip().split('\n')
        
        # Remove leading and trailing pipes and strip whitespace from each line
        clean_lines = [line.strip().strip('|').strip() for line in lines]
        
        # Remove the separator line (second line)
        if len(clean_lines) >= 2 and set(clean_lines[1].replace(':', '').replace('-', '')) == set():
            clean_lines = clean_lines[:1] + clean_lines[2:]
        
        # Join the lines back into a single string
        clean_markdown = '\n'.join(clean_lines)
        
        return clean_markdown
    
    def apply_augmentation(
            self,
            dataframe,
            config: Optional[RunnableConfig] = None
            ):

        #Set chunk size
        chunk_size = 100

        #List with dataframes augmented
        augmented_data_list = []

        augmented_data = AugmentedData()
        chunks = augmented_data.chunk_data(dataframe, chunk_size)

        for chunk in chunks[:2]:
            # Convert the chunk to a Markdown table
            markdown_table = chunk.to_markdown(index=False)

            # Prepare the prompt (ensure 'prompt_2' is defined appropriately)
            p = prompt.prompt_augmented.format(chunk=markdown_table, len_chunk=len(chunk))
            # Invoke the LLM and get the response
            model = utils.load_chat_model(config.response_model)
            response = model.invoke(p)  # Ensure this returns an object with a 'content' attribute
            markdown_content = response.content
            if markdown_content.strip():  # Check if content is not empty
                # Preprocess the markdown table
                clean_markdown = self.preprocess_markdown_table(markdown_content)

                # Use StringIO to simulate a file-like object
                data_io = StringIO(clean_markdown)

                # Reset the pointer in case of multiple parsing attempts
                data_io.seek(0)

                # Read the table using pandas with a regex separator
                try:
                    df = pd.read_csv(
                        data_io,
                        sep=r'\s*\|\s*',  # Regex to split on pipes with optional surrounding whitespace
                        engine='python',
                        header=0,  # The first line is the header
                        na_values=['nan', 'N/A']
                    )
                    augmented_data_list.append(df)
                except pd.errors.ParserError as e:
                    print("Error parsing the markdown table:", e)
            else:
                print("Warning: The content from the LLM is empty.")

            # Concatenate all augmented data
            if augmented_data_list:
                augmented_data_df = pd.concat(augmented_data_list, ignore_index=True)
                # Remove all rows where any column contains '---------'
                augmented_data_df = augmented_data_df[~augmented_data_df.apply(lambda row: row.astype(str).str.contains('---------').any(), axis=1)]
                # Change column names to all lowercase and replace spaces with underscores
                augmented_data_df.columns = augmented_data_df.columns.str.lower().str.replace(' ', '_')
            else:
                print("No data to concatenate.")
            
            return augmented_data_df