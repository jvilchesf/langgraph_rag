from agent_sql.database import DataBaseManager
from agent_sql.state import State

from langgraph.graph import StateGraph, START, END

database_manager = DataBaseManager()

#Graph
#builder
builder = StateGraph(State)
#Nodes
builder.add_node('parse_query', database_manager.parse_query)
builder.add_node('get_unique_nouns', database_manager.get_unique_nouns)
builder.add_node('generate_sql', database_manager.generate_sql)
builder.add_node('validate_and_fix_sql', database_manager.validate_and_fix_sql)
builder.add_node('execute_sql', database_manager.execute_sql)
#edges
builder.add_edge(START, 'parse_query')
builder.add_edge('parse_query', 'get_unique_nouns')
builder.add_edge('get_unique_nouns', 'generate_sql')
builder.add_edge('generate_sql', 'validate_and_fix_sql')
builder.add_edge('validate_and_fix_sql', 'execute_sql')
builder.add_edge('execute_sql', END)
#compile
graph = builder.compile()