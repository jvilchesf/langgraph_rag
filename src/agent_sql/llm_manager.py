from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig

class LlmManager():

    def call_llm(
            self,
            prompt: str,
            config: Optional[RunnableConfig] = None
    ) :
        #get model provider and name
        response_model = config.response_model
        
        #split provider and model
        provider, model = response_model.split("/", maxsplit = 1)

        #Initialize model        
        model = ChatOpenAI(model = model)
        
        #Call LLM
        response = model.invoke(prompt)

        
        return response.content