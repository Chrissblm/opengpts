# import os
# import datetime
# import logging
# import time


# import streamlit as st
# import pandas as pd
# import numpy as np
# import plotly.express as px
# import plotly.graph_objs as go
# import openai
# from pathlib import Path
# from dotenv import load_dotenv
# import sqlite3


# # Local Imports
# from utilities.tools.analyze import AnalyzeGPT, SQL_Query, ChatGPT_Handler  
# from utilities.helpers.EnvHelper import EnvHelper
# from utilities.helpers.LLMHelper import LLMHelper
# from utilities.GPT.excel_cleanse import CleanseAndEmbed, cleanse_and_embed_data
# from utilities.SQL.convert_to_sql import ConvertToSQL


# env_path = Path('.') / '.env.dev'
# load_dotenv(dotenv_path=env_path.resolve())
# env_helper = EnvHelper()

# logger = logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)
# st.set_page_config(page_title="Configure Prompts", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)

# mod_page_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
# st.markdown(mod_page_style, unsafe_allow_html=True)

# # Determine the environment (Azure or local)
# if os.getenv('WEBSITE_SITE_NAME') is not None:
#     # Running in Azure, load settings from EnvHelper
#     env_helper = EnvHelper()
# else:
#     # Running locally, load settings from .env.dev
#     env_path = Path('.') / '.env.dev' 
#     load_dotenv(dotenv_path=env_path.resolve())

# # Load settings from EnvHelper or .env file
# def load_setting(setting_name, session_name, env_value=None, default_value=''): 
#     if session_name not in st.session_state:
#         env_var = os.environ.get(setting_name)
#         if env_var is not None:
#             st.session_state[session_name] = env_var
#         elif env_value is not None:
#             st.session_state[session_name] = env_value
#         else:
#             st.session_state[session_name] = default_value


# # Load settings from EnvHelper
# load_setting("AZURE_OPENAI_MODEL_NAME", "GPT35", "gpt-35-turbo-16k", env_helper.AZURE_OPENAI_MODEL_NAME) 
# load_setting("AZURE_OPENAI_MODEL_GPT4", "GPT4", "gpt-4", env_helper.AZURE_OPENAI_MODEL_GPT4)
# load_setting("AZURE_OPENAI_ENDPOINT", "endpoint", "https://resourcenamehere.openai.azure.com/", env_helper.OPENAI_API_BASE)
# load_setting("AZURE_OPENAI_API_KEY", "apikey", env_value=env_helper.AZURE_OPENAI_KEY)
# load_setting("AZURE_OPENAI_API_VERSION", "api_version", "2023-03-15-preview" ,env_helper.AZURE_OPENAI_API_VERSION)
# load_setting("AZURE_OPENAI_EMBEDDING_MODEL","embedding","text-embedding-ada-002", env_helper.AZURE_OPENAI_EMBEDDING_MODEL)
# load_setting("SQL_ENGINE", "sqlengine", "sqlite")
# load_setting("SQL_SERVER", "sqlserver", env_value=None)
# load_setting("SQL_DATABASE", "sqldatabase", env_value=None)
# load_setting("SQL_USER", "sqluser", env_value=None)
# load_setting("SQL_PASSWORD", "sqlpassword", env_value=None)
# load_setting("SQLITE_DB_PATH", "sqlitedbpath", "data/northwind.db")

# if 'show_AZ_settings' not in st.session_state:  
#     st.session_state['show_AZ_settings'] = False  
    
# if 'show_SQL_settings' not in st.session_state:  
#     st.session_state['show_SQL_settings'] = False  

# def saveOpenAI():
#     st.session_state.GPT35 = st.session_state.txtGPT35
#     st.session_state.GPT4 = st.session_state.txtGPT4
#     st.session_state.endpoint = st.session_state.txtEndpoint
#     st.session_state.apikey = st.session_state.txtAPIKey
#     # We can close out the settings now
#     st.session_state['show_AZ_settings'] = False

# def toggleSettings_AZ():
#     st.session_state['show_AZ_settings'] = not st.session_state['show_AZ_settings']

# def toggleSettings_SQL():
#     st.session_state['show_SQL_settings'] = not st.session_state['show_SQL_settings']

# def saveSQL():
#     st.session_state.sqlengine = st.session_state.txtSQLEngine
#     st.session_state.sqlserver = st.session_state.txtSQLServer
#     st.session_state.sqldatabase = st.session_state.txtSQLDatabase
#     st.session_state.sqluser = st.session_state.txtSQLUser
#     st.session_state.sqlpassword = st.session_state.txtSQLPassword

#     # We can close out the settings now
#     st.session_state['show_SQL_settings'] = False

# openai.api_type = "azure"
# openai.api_version = st.session_state.api_version
# openai.api_key = st.session_state.apikey
# openai.api_base = st.session_state.endpoint
# embedding_model = st.session_state['embedding']
# max_tokens = 1250
# max_response_tokens = 1000  # or whatever value is appropriate for your application
# token_limit= 4096
# temperature=0


# def generate_db_path():
#     timestamp = int(time.time())
#     return f"temp_db_{timestamp}.sqlite"

# database_path = generate_db_path()

# def display_tables(db_path):
#     try:
#         with sqlite3.connect(db_path) as con:
#             query = "SELECT name FROM sqlite_master WHERE type='table';"
#             cursor = con.execute(query)
#             tables = cursor.fetchall()
#             if tables:
#                 st.write("Tables in the database:", tables)
#             else:
#                 st.write("No tables found in the database.")
#     except sqlite3.Error as e:
#         st.error(f"An error occurred while accessing the database: {e}")

# def get_table_names(con):
#     cursor = con.execute("SELECT name FROM sqlite_master WHERE type='table';")
#     return [name[0] for name in cursor.fetchall()]

#TODO use to_sql by SQLAlchemy

# def process_file(uploaded_file, db_path):
#     try:
#         if uploaded_file.type in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel", "text/csv"]:
#             convert_to_sql = ConvertToSQL(db_path)
#             convert_to_sql.excel_to_sql(uploaded_file)
#             display_tables(db_path)
#         elif uploaded_file.type == "application/x-sqlite3":
#             with open(db_path, "wb") as f:
#                 f.write(uploaded_file.getvalue())
#             display_tables(db_path)
#     except Exception as e:
#         st.error(f"An error occurred: {e}")

# if 'file_processed' not in st.session_state:
#     st.session_state['file_processed'] = False

# uploaded_file = st.file_uploader("Upload File", type=["csv", "xlsx", "xls", "db"])

# if uploaded_file is not None and not st.session_state['file_processed']:
#     with st.spinner("Processing file..."):
#         try:
#             process_file(uploaded_file, database_path)
#             st.session_state['file_processed'] = True
#         except Exception as e:
#             st.error(f"An error occurred while processing the file: {e}")
#             st.session_state['file_processed'] = False

# if 'selected_table' not in st.session_state:
#     st.session_state['selected_table'] = None

    
# if 'file_processed' in st.session_state and st.session_state['file_processed']:
#     try:
#         with sqlite3.connect(database_path) as con:
#             table_names = get_table_names(con)
#             if st.session_state['selected_table'] in table_names:
#                 index = table_names.index(st.session_state['selected_table'])
#             else:
#                 index = 0
            
#             st.session_state['selected_table'] = st.selectbox('Select a table for cleansing', table_names, index=index)

#             # Get the columns of the selected table
#             query = f"PRAGMA table_info({st.session_state['selected_table']})"
#             df = pd.read_sql_query(query, con)
#             column_names = df['name'].tolist()

#             # Select columns
#             st.session_state['selected_columns'] = st.multiselect('Select columns for cleansing', column_names)

#             if st.button('Cleanse & Embed'):
#                 if 'selected_table' in st.session_state and st.session_state['selected_table'] and st.session_state['selected_columns']:
#                     try:
#                         with st.spinner('Cleansing and embedding data...'):
#                             # Use the selected columns in the query
#                             query = f"SELECT {', '.join(st.session_state['selected_columns'])} FROM {st.session_state['selected_table']}"
#                             df = pd.read_sql_query(query, con)
#                             df = cleanse_and_embed_data(df, embedding_model)
                            
#                         st.success(f"Data in table '{st.session_state['selected_table']}' cleansed and embedded successfully.")
#                         # You might want to display or use the cleansed and embedded DataFrame here
#                     except Exception as e:
#                         st.error(f"An error occurred while processing the data: {e}")
#     except sqlite3.OperationalError as e:
#         st.error(f"Unable to open database file: {e}")

# col1, col2  = st.columns((3,1)) 

# with st.sidebar:  
#     options = ("SQL Query Writing Assistant", "Data Analysis Assistant")
#     index = st.radio("Choose the app", range(len(options)), format_func=lambda x: options[x])
#     if index == 0:
#         system_message="""
#         You are an agent designed to interact with a SQL database with schema detail in <<data_sources>>.
#         Given an input question, create a syntactically correct {sql_engine} query to run, then look at the results of the query and return the answer.
#         You can order the results by a relevant column to return the most interesting examples in the database.
#         Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.
#         You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.
#         DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
#         Remember to format SQL query as in ```sql\n SQL QUERY HERE ``` in your response.

#         """
#         few_shot_examples=""
#         extract_patterns=[('sql',r"```sql\n(.*?)```")]
#         extractor = ChatGPT_Handler(extract_patterns=extract_patterns)

#         faq_dict = {  
#             "GPT35": [  
#                 "Show me revenue by product in ascending order",  
#                 "Show me top 10 most expensive products",
#                 "Show me net revenue by year. Revenue time is based on shipped date.",  
#                 "For each category, get the list of products sold and the total sales amount",
#                 "Find Quarterly Orders by Product. First column is Product Name, then year then four other columns, each for a quarter. The amount is order amount after discount", 
#             ],  
#             "GPT4": [  
#                 "Pick top 20 customers generated most revenue in 2016 and for each customer show 3 products that they purchased most",  
#                 "Which products have most seasonality in sales quantity in 2016?" ,  
#             ]  
#         }  

#     elif index == 1:
#         system_message="""
#         You are a smart AI assistant to help answer business questions based on analyzing data. 
#         You can plan solving the question with one more multiple thought step. At each thought step, you can write python code to analyze data to assist you. Observe what you get at each step to plan for the next step.
#         You are given following utilities to help you retrieve data and commmunicate your result to end user.
#         1. execute_sql(sql_query: str): A Python function can query data from the <<data_sources>> given a query which you need to create. The query has to be syntactically correct for {sql_engine} and only use tables and columns under <<data_sources>>. The execute_sql function returns a Python pandas dataframe contain the results of the query.
#         2. Use plotly library for data visualization. 
#         3. Use observe(label: str, data: any) utility function to observe data under the label for your evaluation. Use observe() function instead of print() as this is executed in streamlit environment. Due to system limitation, you will only see the first 10 rows of the dataset.
#         4. To communicate with user, use show() function on data, text and plotly figure. show() is a utility function that can render different types of data to end user. Remember, you don't see data with show(), only user does. You see data with observe()
#             - If you want to show  user a plotly visualization, then use ```show(fig)`` 
#             - If you want to show user data which is a text or a pandas dataframe or a list, use ```show(data)```
#             - Never use print(). User don't see anything with print()
#         5. Lastly, don't forget to deal with data quality problem. You should apply data imputation technique to deal with missing data or NAN data.
#         6. Always follow the flow of Thought: , Observation:, Action: and Answer: as in template below strictly. 

#         """

#         few_shot_examples="""
#         <<Template>>
#         Question: User Question
#         Thought 1: Your thought here.
#         Action: 
#         ```python
#         #Import neccessary libraries here
#         import numpy as np
#         #Query some data 
#         sql_query = "SOME SQL QUERY"
#         step1_df = execute_sql(sql_query)
#         # Replace NAN with 0. Always have this step
#         step1_df['Some_Column'] = step1_df['Some_Column'].replace(np.nan,0)
#         #observe query result
#         observe("some_label", step1_df) #Always use observe() instead of print
#         ```
#         Observation: 
#         step1_df is displayed here
#         Thought 2: Your thought here
#         Action:  
#         ```python
#         import plotly.express as px 
#         #from step1_df, perform some data analysis action to produce step2_df
#         #To see the data for yourself the only way is to use observe()
#         observe("some_label", step2_df) #Always use observe() 
#         #Decide to show it to user.
#         fig=px.line(step2_df)
#         #visualize fig object to user.  
#         show(fig)
#         #you can also directly display tabular or text data to end user.
#         show(step2_df)
#         ```
#         Observation: 
#         step2_df is displayed here
#         Answer: Your final answer and comment for the question. Also use Python for computation, never compute result youself.
#         <</Template>>

#         """

#         extract_patterns=[("Thought:",r'(Thought \d+):\s*(.*?)(?:\n|$)'), ('Action:',r"```python\n(.*?)```"),("Answer:",r'([Aa]nswer:) (.*)')]
#         extractor = ChatGPT_Handler(extract_patterns=extract_patterns)
#         faq_dict = {  
#             "GPT35": [  
#                 "Show me daily revenue trends in 2016 per region",  
#                 "Is that true that top 20% customers generate 80% revenue in 2016? What's their percentage of revenue contribution?",  
#                 "Which products have most seasonality in sales quantity in 2016?",  
#                 "Which customers are most likely to churn?", 
#                 "What is the impact of discount on sales? What's optimal discount rate?",
#                 "Predict monthly revenue for next 6 months starting from June-2018. Do not use Prophet. Show the prediction in a chart together with historical data for comparison."

#             ],  
#             "GPT4": [  
#                 "Predict monthly revenue for next 6 months starting from June-2018. Do not use Prophet. Show the prediction in a chart together with historical data for comparison.",  
#                 "What is the impact of discount on sales? What's optimal discount rate?" ,  
#             ]  
#         }  

#     st.button("Azure Settings",on_click=toggleSettings_AZ)
#     if st.session_state['show_AZ_settings']:  
#         # with st.expander("Settings",expanded=expandit):
#         with st.form("AzureOpenAI"):
#             st.title("Azure OpenAI Settings")
#             st.text_input("Chat GPT-35 deployment name:", value=st.session_state.GPT35,key="txtGPT35")  
#             st.text_input("Chat GPT-4 deployment name (if not specified, default to ChatGPT-35):", value=st.session_state.GPT4,key="txtGPT4") 
#             st.text_input("Azure OpenAI Endpoint:", value=st.session_state.endpoint,key="txtEndpoint")  
#             st.text_input("Azure OpenAI Key:", value="", type="password",key="txtAPIKey")
    
#             st.form_submit_button("Submit",on_click=saveOpenAI)

#     st.button("SQL Settings",on_click=toggleSettings_SQL)
#     if st.session_state['show_SQL_settings']:  
#         # with st.expander("Settings",expanded=expandit):
#         with st.form("SQLSettings"):
#             st.radio("SQL Engine:",["sqlite","sqlserver"],index=0,key="txtSQLEngine")
#             st.write("SQL Server Settings (Optional)")
#             st.text_input("SQL Server:", value=st.session_state.sqlserver,key="txtSQLServer")  
#             st.text_input("Database:", value=st.session_state.sqldatabase,key="txtSQLDatabase")
#             st.text_input("User:", value=st.session_state.sqluser,key="txtSQLUser")  
#             st.text_input("Password:", type="password",value=st.session_state.sqlpassword,key="txtSQLPassword")

#             st.form_submit_button("Submit",on_click=saveSQL)

#     # sql_list=["sqlite"]
#     # if not (st.session_state.sqlserver == '' or st.session_state.sqldatabase == '' or st.session_state.sqluser == '' or st.session_state.sqlpassword == ''):
#     #     sql_list.append("sqlserver")
#     # sql_engine = st.selectbox('SQL Engine',sql_list)  

#     chat_list=[]
#     if st.session_state.GPT35 != '':
#         chat_list.append("GPT35")
#     if st.session_state.GPT4 != '':
#         chat_list.append("GPT4")
#     gpt_engine = st.selectbox('GPT Model', chat_list)  
#     if gpt_engine == "GPT35":  
#         gpt_engine = st.session_state.GPT35  
#         faq = faq_dict["GPT35"]  
#     else:  
#         gpt_engine = st.session_state.GPT4
#         faq = faq_dict["GPT4"]  
    
#     option = st.selectbox('FAQs',faq)  

#     show_code = st.checkbox("Show code", value=False)  
#     show_prompt = st.checkbox("Show prompt", value=False)
#     # step_break = st.checkbox("Break at every step", value=False)  
#     question = st.text_area("Ask me a question", option)
  
#     if st.button("Submit"):  
#         if st.session_state.apikey == '' or st.session_state.endpoint == '' or st.session_state.GPT35 == '' or st.session_state.sqlengine == '':
#             st.error("You need to specify Azure Open AI Deployment Settings!")
#         elif st.session_state.sqlengine =="sqlserver" and (st.session_state.sqlserver == '' or st.session_state.sqldatabase == '' or st.session_state.sqluser == '' or st.session_state.sqlpassword == ''):
#             st.error("You need to specify SQL Server Settings!")
#         else:
#             if st.session_state.sqlengine =="sqlserver":
#                 sql_query_tool = SQL_Query(driver='ODBC Driver 17 for SQL Server',dbserver=st.session_state.sqlserver, database=st.session_state.sqldatabase, db_user=st.session_state.sqluser ,db_password=st.session_state.sqlpassword)
#             else:
#                 sql_query_tool = SQL_Query(db_path=st.session_state.sqlitedbpath)
#             analyzer = AnalyzeGPT(sql_engine=st.session_state.sqlengine,content_extractor= extractor, sql_query_tool=sql_query_tool,  system_message=system_message, few_shot_examples=few_shot_examples,st=st,  
#                                 gpt_deployment=gpt_engine,max_response_tokens=max_response_tokens,token_limit=token_limit,  
#                                 temperature=temperature)  
#             if index==0:
#                 analyzer.query_run(question,show_code,show_prompt, col1)  
#             elif index==1:
#                 analyzer.run(question,show_code,show_prompt, col1)  
#             else:
#                 st.error("Not implemented yet!")

