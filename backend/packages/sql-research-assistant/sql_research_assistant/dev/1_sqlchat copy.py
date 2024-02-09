# import logging
# import os, sys, time
# from pathlib import Path

# import streamlit as st
# from langchain.llms.openai import OpenAI
# from langchain.agents import create_sql_agent
# from langchain.sql_database import SQLDatabase
# from langchain.agents.agent_types import AgentType
# from langchain.callbacks import StreamlitCallbackHandler
# from langchain_community.agent_toolkits import SQLDatabaseToolkit
# from langchain_community.utilities.sql_database import SQLDatabase # SQLDatabaseToolkit, create_sql_agent
# # from langchain_community.utilities.pebblo import get_loader_type
# from langchain_community.document_loaders import PebbloSafeLoader, UnstructuredFileLoader, UnstructuredExcelLoader, UnstructuredCSVLoader, UnstructuredXMLLoader, UnstructuredHTMLLoader, unstructured
# from langchain_community.document_loaders.generic import GenericLoader
# from langchain.document_loaders.blob_loaders import FileSystemBlobLoader

# import sqlite3
# from sqlalchemy.exc import DBAPIError
# from sqlalchemy import create_engine, exc, event, select, text
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.pool import NullPool
# import pandas as pd
# # from langchain.agents import create_pandas_dataframe_agent

# from sql_research_assistant.utils.loadfile import UploadToDB, DocumentLoader, DatabaseUploader
# from nextgen.helpers.EnvHelper import EnvHelper
# from nextgen.helpers.LLMHelper import NGllmhelper
# env_helper = EnvHelper()

# st.set_page_config(page_title="Load your SQL DB")
# mod_page_style = """
#             <style>
#             #MainMenu {visibility: visible;}
#             footer {visibility: hidden;}
#             header {visibility: visible;}
#             </style>
#             """
# st.markdown(mod_page_style, unsafe_allow_html=True)

# col1, col2, col3 = st.columns([3,1,1])
# with col3:
#     st.image("sql_research_assistant/assets/Color logo - no background.png", width=100)
# with col1:
#     st.header('Load SQL DB', divider='green')
# col1, col2, col3, col4 = st.columns([2,1,1,1])

# if "shared" not in st.session_state:
#    st.session_state["shared"] = True
   

# # Add the parent directory of `sql_research_assistant` to the Python path
# parent_dir = (Path(__file__).parent / "..").resolve()  # Adjust according to your structure
# sys.path.insert(0, str(parent_dir))

# radio_opt = ["Use Azure SQLDB connection", "Enter SQL database uri", "Create temp SQLite db"]
# selected_opt = st.sidebar.radio("Choose SQL db", options=radio_opt)
# # Define database URI
# DATABASE_URI = "sqlite:///mydatabase.db"
# TEMP_DATABASE_URI = "sqlite:///tempdatabase.db"

# def get_db_config(selected_option):
#     logging.debug(f"Selected database option from function: {selected_option}")  # Debug print
#     if selected_option == "Use Azure SQLDB connection":
#         return {"db_type": "azure", "db_uri": None}
#     elif selected_option == "Enter SQL database uri":
#         db_uri = st.sidebar.text_input("Database URI", placeholder="mysql://user:pass@hostname:port/db")
#         return {"db_type": "manual", "db_uri": db_uri}
#     elif selected_option == "Create temp SQLite db":
#         return {"db_type": "temp", "db_uri": "sqlite:///tempdatabase.db"}
#     else:
#         st.error("Invalid database selection detected.")
#         # Handle default case or notify the user
#         return {"db_type": "default", "db_uri": None}


# def init_db(uri, test_query=True):
#     """
#     Initialize SQLAlchemy engine with optional connection testing.
#     """
#     engine = create_engine(uri, poolclass=NullPool)  # Use NullPool to avoid pooling in SQLite
#     if test_query:
#         try:
#             # Perform a test query to ensure the database is connected
#             with engine.connect() as conn:
#                 conn.execute(select(1))
#             logging.debug(f"Database at {uri} is accessible.")
#         except exc.DBAPIError as err:
#             if err.connection_invalidated:
#                 # If connection is invalidated, return None
#                 st.warning(f"Database at {uri} is inaccessible, attempting fallback.")
#                 return None
#             else:
#                 raise
#     return engine

# def setup_database(uri):
#     """
#     Set up database by creating necessary tables.
#     Adjust with your actual table creation logic.
#     """
#     engine = create_engine(uri)
#     # Start a connection and execute SQL command within a transaction
#     with engine.begin() as conn:
#         logging.debug(conn.execute(text("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)")))
#     print(f"Database setup complete at {uri}")


# @st.cache_resource(ttl=600)
# def get_database_engine():
#     """
#     Get or create a database engine.
#     """
#     engine = init_db(DATABASE_URI)
#     if engine is None:
#         # Fallback to temporary database if primary fails
#         logging.debug("Primary database is inaccessible. Fallback to temporary database.")
#         engine = init_db(TEMP_DATABASE_URI, test_query=False)
#         if engine is None:
#             raise Exception("Failed to initialize any database.")
#         setup_database(TEMP_DATABASE_URI)
#     else:
#         setup_database(DATABASE_URI)
#         logging.debug("Primary database is accessible.")
#     return engine

# def get_schema():
#     return db.get_table_info()


# def show_db_schema(db: SQLDatabase):
#     """Displays the schema of the database in the Streamlit app."""
#     schema_info = db.get_table_info_no_throw()
#     st.text(schema_info)

# # # User inputs for loading the LLM
# # radio_opt = ["Use Azure Openai", "Connect to your openai api key"]
# # selected_opt_llm = st.sidebar.radio(label="Choose LLM", options=radio_opt)
# # if selected_opt_llm == "Connect to your openai api key":
# #     openai_api_key = st.sidebar.text_input(
# #         label="OpenAI API Key",
# #         type="password",
# #     )
# #     llm = OpenAI(openai_api_key=openai_api_key, temperature=0, streaming=True)
# #     if not openai_api_key:
# #         st.info("Please add your OpenAI API key to continue.")
# #         st.stop()
# # #loads azure llm based on .env file
# # else:
# #     llms = NGllmhelper()
# #     llm = llms.get_openai_llm()

# db = None
# try:
#     logging.debug("Inside try block...")
#     logging.debug("Before getting DB config")
#     db_config = get_db_config(selected_opt)
#     logging.debug(f"Database configuration: {db_config}")


#     if db_config["db_type"] == "temp":
#         logging.debug("Selected temp database...")
#         # If temporary database is selected, use the get_database_engine function
#         engine = get_database_engine()
#         # Assuming get_database_engine already handles temp db logic
#         db = SQLDatabase(engine=engine)  # Wrap engine in SQLDatabase
#         logging.debug("Temp Database is ready for use.")
        
#     elif db_config["db_uri"]:  # If there's a URI provided
#         logging.debug("Database URI provided...")
#         # Assuming SQLDB is a custom or framework class that wraps or produces SQLDatabase
#         sql_db = SQLDB(db_type=db_config["db_type"], db_uri=db_config["db_uri"])
#         db = sql_db.db
        
#     else:  # If no URI is needed (e.g., Azure or temp SQLite)
#         logging.debug("Using Azure database...")
#         sql_db = SQLDB(db_type=db_config["db_type"])
#         db = sql_db.db

#     # Check if db is successfully initialized
#     logging.debug("Checking if db is initialized...")
#     if db:
#         st.write("Database and toolkit initialized.")
#        # Display database schema
#         show_db_schema(db)
#         logging.debug("Schema overview displayed.")
#     else:
#         st.error("Failed to initialize the database connection.")

# except Exception as e:
#     st.error(f"Error configuring database: {e}")

# # Make sure to check if db is not None before initializing DatabaseUploader
# if db is not None:
#     doc_loader = DocumentLoader()
#     db_uploader = DatabaseUploader(db)
# else:
#     st.error("Database not initialized. Unable to create DatabaseUploader.")
    
# ###*** Loads files ***

# def clear_submit():
#     """
#     Clear the Submit Button State
#     Returns:

#     """
#     st.session_state["submit"] = False

# @st.cache_data(show_spinner=True)
# def load_data_from_file(uploaded_file):
#     return loaded_data

# # Streamlit file uploader
# uploaded_file = st.file_uploader("Choose a file")
# if uploaded_file is not None:
#     # Load the file into DataFrames
#     loaded_data = doc_loader.load_file(uploaded_file)
    
#     with st.sidebar:   
#         if st.button(f"Upload ALL '{uploaded_file.name}' to SQL database"):
#             UploadToDB(uploaded_file) #upload all tables
#             st.success(f"'{uploaded_file.name}' uploaded successfully.")

#     if uploaded_file is not None:
#         loaded_data = load_data_from_file(uploaded_file)

#         if loaded_data:
#                 for table_name, df in loaded_data.items():
#                     st.write(f"Preview of '{table_name}':")
#                     st.dataframe(df.head())  # Show the first few rows of the DataFrame

#                     button_key = f"upload_{table_name}"
#                     if st.button(f"Upload '{table_name}' to SQL database", key=button_key):
#                         # Assuming db_uploader has a method upload_data that accepts a dictionary
#                         db_uploader.upload_data({table_name: df})
#                         st.success(f"'{table_name}' uploaded successfully.")
#     else:
#         st.error("No data was loaded. Please check the file format and try again.")


# # if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
# #     st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# # for msg in st.session_state.messages:
# #     st.chat_message(msg["role"]).write(msg["content"])

# # user_query = st.chat_input(placeholder="Ask me anything!")

# # if user_query:
# #     st.session_state.messages.append({"role": "user", "content": user_query})
# #     st.chat_message("user").write(user_query)

# #     with st.chat_message("assistant"):
# #         st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
# #         response = agent_executor.run(user_query, callbacks=[st_cb])
# #         st.session_state.messages.append({"role": "assistant", "content": response})
# #         st.write(response)
