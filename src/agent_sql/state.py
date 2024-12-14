from typing import TypedDict, List, Any
from dataclasses import dataclass

@dataclass
class State(TypedDict):

    question: str   
    parsed_question: str
    unique_nouns: List[str]
    sql_query: str
    sql_valid : str
    sql_issues: str
    results : List[Any]
