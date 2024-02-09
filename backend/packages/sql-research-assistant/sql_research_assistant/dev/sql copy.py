# from pathlib import Path

# from langchain.memory import ConversationBufferMemory
# from langchain.pydantic_v1 import BaseModel
# from langchain_openai import ChatOpenAI, AzureChatOpenAI
# from langchain_community.chat_models import ChatOllama
# from langchain.utilities import SQLDatabase
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.runnables import RunnablePassthrough

# from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
# from langchain_community.agent_toolkits import create_sql_agent

# import os
# import logging
# import struct
# import pyodbc
# from azure.identity import DefaultAzureCredential
        
# from nextgen.helpers.EnvHelper import EnvHelper
# env_helper: EnvHelper = EnvHelper()

# #TODO replace with AzureChatOpenAI
# # ollama_llm = "llama2"
# # llm = ChatOllama(model=ollama_llm)

# from backend.nextgen.helpers.LLMHelper import NGllmhelper
# llmsng = NGllmhelper()
# llm = llmsng.get_openai_llm()

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
# os.environ['PYODBC_TRACE'] = '1'

# # class SQLConnect:
# #     def __init__(self):
# #         env_helper: EnvHelper = EnvHelper()
 
# #         # Access individual environment variables
# #         self.sql_server_name = env_helper.SQL_SERVER_NAME
# #         self.sql_server_database = env_helper.SQL_SERVER_DATABASE

# #     def get_sql_connection_string(self):
# #         # Build the connection string
# #         connection_string = (
# #             f"DRIVER={{ODBC Driver 18 for SQL Server}};"
# #             f"SERVER=tcp:{self.sql_server_name},1433;"
# #             f"DATABASE={self.sql_server_database};"
# #             "Encrypt=yes;"
# #             "TrustServerCertificate=no;"
# #             "Connection Timeout=30;"
# #         )
# #         # Return the connection string
# #         return connection_string

# #     # Use environment variable for connection string
# #     connection_string = get_sql_connection_string
    
# #     def get_conn(self):
# #         """Establishes a database connection using Azure Active Directory."""
# #         # Detect environment and adjust DefaultAzureCredential accordingly
# #         is_local = os.environ.get('IS_LOCAL', 'true').lower() == 'true'
# #         credential_options = {
# #             "exclude_interactive_browser_credential": not is_local
# #         }
# #         credential = DefaultAzureCredential(**credential_options)
# #         token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
# #         token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
# #         SQL_COPT_SS_ACCESS_TOKEN = 1256  # This connection option is defined by Microsoft in msodbcsql.h
# #         conn = pyodbc.connect(self.get_sql_connection_string(), attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
# #         return conn

# # # Initialize SQLConnect and SQLDatabaseToolkit
# # sql_connect_instance = SQLConnect()
# # db = conn=sql_connect_instance.get_conn()
# # toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# # # Example usage of toolkit
# # def get_all():
# #     with sql_connect_instance.get_conn() as conn:
# #         cursor = conn.cursor()
# #         cursor.execute("SELECT * FROM Persons")
# #         rows = cursor.fetchall()
# #         for row in rows:
# #             print(row)
# #     return

# from urllib.parse import quote_plus
# import pyodbc
# import os
# from azure.identity import DefaultAzureCredential

# from langchain_community.utilities.sql_database import SQLDatabase
# from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
# from langchain_community.agent_toolkits import create_sql_agent

# class SQLConnectTokenAuth:
#     def __init__(self):
#         self.server_name = os.getenv("SQL_SERVER_NAME")
#         self.database_name = os.getenv("SQL_SERVER_DATABASE")

#     def get_access_token(self):
#         # Assuming your environment is correctly set up for DefaultAzureCredential
#         credential = DefaultAzureCredential()
#         token = credential.get_token("https://database.windows.net/.default")
#         return token.token

#     def get_connection_string(self):
#         token = self.get_access_token()
#         conn_str = (
#             "DRIVER={ODBC Driver 18 for SQL Server};"
#             f"SERVER={self.server_name};"
#             f"DATABASE={self.database_name};"
#             "Encrypt=yes;"
#             "TrustServerCertificate=no;"
#             "Connection Timeout=30;"
#         )
#         # Token is not directly part of the connection string; it will be passed to pyodbc separately
#         return conn_str, token


# def _run(query: str, llm) -> str:
#     sql_connect = SQLConnectTokenAuth()
#     conn_str, token = sql_connect.get_connection_string()

#     # Creating a pyodbc connection using the token
#     SQL_COPT_SS_ACCESS_TOKEN = 1256
#     token_struct = bytes(token, "UTF-16LE")
#     attrs_before = {SQL_COPT_SS_ACCESS_TOKEN: token_struct}

#     # Using pyodbc to connect
#     conn = pyodbc.connect(conn_str, attrs_before=attrs_before)
#     db = SQLDatabase(conn=conn)  # Assuming SQLDatabase can wrap around a pyodbc connection

#     toolkit = SQLDatabaseToolkit(db=db, llm=llm)

#     with conn.cursor() as cursor:
#         cursor.execute(query)
#         result = cursor.fetchall()

# # Define the methods to interact with the database
# # Assuming get_schema and run_query are updated to receive toolkit as an argument
# def get_schema(toolkit):
#     return toolkit.get_table_info()

# def run_query(query, toolkit):
#     return toolkit.run_query(query)


# # Prompt
# template = """Based on the table schema below, write a SQL query that would answer the user's question:
# {schema}

# Question: {question}
# SQL Query:"""  # noqa: E501
# prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", "Given an input question, convert it to a SQL query. No pre-amble."),
#         ("human", template),
#     ]
# )

# memory = ConversationBufferMemory(return_messages=True)

# # Chain to query with memory

# sql_chain = (
#     RunnablePassthrough.assign(
#         schema=lambda _: get_schema(db),
#     )
#     | prompt
#     | llm.bind(stop=["\nSQLResult:"])
#     | StrOutputParser()
#     | (lambda x: x.split("\n\n")[0])
# )


# # Chain to answer
# template = """Based on the table schema below, question, sql query, and sql response, write a natural language response:
# {schema}

# Question: {question}
# SQL Query: {query}
# SQL Response: {response}"""  # noqa: E501
# prompt_response = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "Given an input question and SQL response, convert it to a natural "
#             "language answer. No pre-amble.",
#         ),
#         ("human", template),
#     ]
# )


# # Supply the input types to the prompt
# class InputType(BaseModel):
#     question: str


# sql_answer_chain = (
#     RunnablePassthrough.assign(query=sql_chain).with_types(input_type=InputType)
#     | RunnablePassthrough.assign(
#         schema = get_schema(toolkit),
#         response=lambda x: db.run(x["query"]),
#     )
#     | RunnablePassthrough.assign(
#         answer=prompt_response | ChatOpenAI() | StrOutputParser()
#     )
#     | (lambda x: f"Question: {x['question']}\n\nAnswer: {x['answer']}")
# )

