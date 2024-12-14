# Overview
This is a personal project I've been working on to get hands-on experience with Langchain and Langgraph.

The main idea is to read three different CSV files, each containing bank transactions, standarize them and query them. 

The first step is to read the data and standardize their structure and language, as one of them is in German. I use an LLM to define and create this structure. Once the data is structured, I create an "SQL" table that will be used in the second step.
 
The second step involves creating an "SQL query" based on "natural language." For this, it was necessary to implement a prompt to generate the desired query.

To tackle this task, I've created two different flows in Langgraph. The first flow is a "retriever flow," and the second one is an "SQL agent" flow.

<img src = "/images/portfolio_genAI_langgraph_graph_1.png">

<img src = "/images/portfolio_genAI_langgraph_graph_2.png">

# File structure
