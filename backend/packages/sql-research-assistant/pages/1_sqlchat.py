import logging
import os, sys, time
from pathlib import Path

import streamlit as st

from langchain.llms.openai import OpenAI
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase # SQLDatabaseToolkit, create_sql_agent
# from langchain_community.utilities.pebblo import get_loader_type
from langchain_community.document_loaders import PebbloSafeLoader, UnstructuredFileLoader, UnstructuredExcelLoader, UnstructuredCSVLoader, UnstructuredXMLLoader, UnstructuredHTMLLoader, unstructured
from langchain_community.document_loaders.generic import GenericLoader
from langchain.document_loaders.blob_loaders import FileSystemBlobLoader
# from langchain.agents import create_pandas_dataframe_agent

import struct
import pyodbc
from sqlalchemy.exc import DBAPIError
from sqlalchemy import create_engine, exc, event, select, text, MetaData
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import pandas as pd

from azure.identity import DefaultAzureCredential

from sql_research_assistant.utils.loadfile import UploadToDB, DocumentLoader, DatabaseUploader
from nextgen.helpers.EnvHelper import EnvHelper
from nextgen.helpers.LLMHelper import NGllmhelper
from nextgen.auth.AuthenticationHelper import AuthenticationHelper

env_helper = EnvHelper()

st.set_page_config(page_title="Load your SQL DB")
mod_page_style = """
            <style>
            #MainMenu {visibility: visible;}
            footer {visibility: hidden;}
            header {visibility: visible;}
            </style>
            """
st.markdown(mod_page_style, unsafe_allow_html=True)

col1, col2, col3 = st.columns([3,1,1])
with col3:
    st.image("sql_research_assistant/assets/Color logo - no background.png", width=100)
with col1:
    st.header('Load SQL DB', divider='green')
col1, col2, col3, col4 = st.columns([2,1,1,1])

if "shared" not in st.session_state:
   st.session_state["shared"] = True
   
# Add the parent directory of `sql_research_assistant` to the Python path
parent_dir = (Path(__file__).parent / "..").resolve()  # Adjust according to your structure
sys.path.insert(0, str(parent_dir))

class DatabaseManager:
    def __init__(self, db_type='temp', db_uri=None):
        self.db_type = db_type
        self.db_uri = db_uri
        self.engine = None
        self.db = None
        self.auth_helper = None  # Initialize the AuthenticationHelper attribute
        self.initialize_auth_helper()  # Call the initialization method for the AuthenticationHelper
        self.initialize()

    def initialize_auth_helper(self):
        # Initialize the AuthenticationHelper instance here
        # For demonstration, using environment variables. Replace with actual values as needed
        use_authentication = True if os.getenv("USE_AUTHENTICATION") == "True" else False
        server_app_id = os.getenv("SERVER_APP_ID")
        server_app_secret = os.getenv("SERVER_APP_SECRET")
        client_app_id = os.getenv("CLIENT_APP_ID")
        tenant_id = os.getenv("SQL_SERVER_TENANT_ID")
        token_cache_path = os.getenv("TOKEN_CACHE_PATH", None)
        
        
        self.auth_helper = AuthenticationHelper(
            use_authentication=use_authentication,
            server_app_id=server_app_id,
            server_app_secret=server_app_secret,
            client_app_id=client_app_id,
            tenant_id=tenant_id,
            token_cache_path=token_cache_path,
        )
    
    def initialize(self):
        if self.db_type == 'azure':
            self.engine = self.create_azure_sql_engine()
        try:
            if self.db_type == 'temp':
                self.engine = self.init_db(self.DATABASE_URI)
            elif self.db_type == 'manual':
                self.engine = self.init_db(self.db_uri)
            elif self.db_type == 'azure':
                # Example Azure SQL connection setup. Adjust as needed.
                self.engine = self.create_azure_sql_engine()
            self.db = SQLDatabase(engine=self.engine) if self.engine else None
            self.setup_database()
        except Exception as e:
            logging.error(f"Database initialization failed: {e}")
            st.error("Failed to initialize the database connection.")
            
    def ensure_connection(self):
        if not self.engine or not self.is_engine_healthy():
            self.initialize()
    
    def is_engine_healthy(self):
        try:
            # Attempt a simple query or ping the database
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            return False

    @property
    def DATABASE_URI(self):
        return "sqlite:///mydatabase.db"

    @property
    def TEMP_DATABASE_URI(self):
        return "sqlite:///tempdatabase.db"

    def init_db(self, uri):
        try:
            engine = create_engine(uri, poolclass=NullPool)
            with engine.connect() as conn:
                conn.execute(select(1))
            return engine
        except DBAPIError as err:
            logging.error(f"Database at {uri} is inaccessible: {err}")
            return None

    # @st.cache_resource(ttl=600)
    def setup_database(self):
        if not self.engine:
            logging.error("No database engine available for setup.")
            return
        # # Database schema setup logic here
        with self.engine.begin() as conn:
            conn.query('select 1')
        logging.info("Database setup complete.")

    def create_azure_sql_engine(self):
        if self.db_type != 'azure' or not self.auth_helper.use_authentication:
            logging.error("Azure SQL Engine can only be created with Azure authentication enabled.")
            return None
        
        if env_helper.SQL_SERVER_AUTH == "keys":
            return self.create_keys_azure_sql_engine(
                env_helper.SQL_SERVER_NAME, 
                env_helper.SQL_SERVER_DATABASE, 
                env_helper.SQL_SERVER_USERNAME, 
                env_helper.SQL_SERVER_PASSWORD, 
                env_helper.SQL_SERVER_DRIVER
            )
        else:
            # headers = {"Authorization": "Bearer "}
            # token = self.auth_helper.get_auth_claims_if_enabled(headers).get_cache_token()("access_token")
            credential = DefaultAzureCredential()
            token_scope = "https://database.windows.net/.default"
            token = credential.get_token(token_scope).token
            if not token:
                logging.error("Failed to obtain access token for Azure SQL Database.")
                return None
            # Use the token to create an engine
            return self.create_token_azure_sql_engine(
                env_helper.SQL_SERVER_NAME, 
                env_helper.SQL_SERVER_DATABASE, 
                env_helper.SQL_SERVER_DRIVER,
                token
            )

    def create_token_azure_sql_engine(self, server, database, driver, token):
        # credential = DefaultAzureCredential()
        # token_scope = "https://database.windows.net/.default"
        # token = credential.get_token(token_scope).token
        token_bytes = token.encode("UTF-16-LE")
        token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
        connection_string = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};"
        def creator():
            return pyodbc.connect(connection_string, attrs_before={1256: token_struct})
        engine = create_engine("mssql+pyodbc://", creator=creator)
        return engine
    
    def create_keys_azure_sql_engine(self, server, database, username, password, driver):
        connection_url = URL.create(
            "mssql+pyodbc",
            username=username,
            password=password,
            host=server,
            database=database,
            query={"driver": driver, "Encrypt": "yes", "TrustServerCertificate": "no", "Connection Timeout": "30"}
        )
        engine = create_engine(str(connection_url))
        return engine

    def show_schema(self):
        if not self.db:
            st.error("No database available to show schema.")
            return
        schema_info = self.db.get_table_info_no_throw()
        st.text(schema_info)
    
# Select the DB Type


# Function to initialize or get the existing database manager instance
def get_or_initialize_db_manager(db_type, db_uri):
    if 'db_manager' not in st.session_state or not st.session_state.db_manager.is_engine_healthy():
        st.session_state.db_manager = DatabaseManager(db_type=db_type, db_uri=db_uri)
        st.session_state.db_manager.ensure_connection()
    return st.session_state.db_manager

if 'db_manager' not in st.session_state or not st.session_state.db_manager.is_engine_healthy():
    selected_option = st.sidebar.radio("Choose SQL DB", ["Use Azure SQLDB connection", "Enter SQL database uri", "Create temp SQLite db"])
else:
    st.write("Database connection is healthy.")
    
db_uri = st.sidebar.text_input("Database URI", "") if selected_option == "Enter SQL database uri" else None
db_type = "azure" if selected_option == "Use Azure SQLDB connection" else "manual" if selected_option == "Enter SQL database uri" else "temp"


db_manager = get_or_initialize_db_manager(db_type, db_uri)
db = db_manager
db.show_schema()

###*** Loads files ***

# Function to clear submit state
def clear_submit():
    st.session_state["submit"] = False

# Function to load data from file
@st.cache_data(show_spinner=True)
def load_data_from_file(uploaded_file):
    # Use your DocumentLoader logic here to load the file
    loaded_data = doc_loader.load_file(uploaded_file)
    return loaded_data

# Initialize DocumentLoader and DatabaseUploader with the database from DatabaseManager
if db.db is not None:
    doc_loader = DocumentLoader()
    db_uploader = DatabaseUploader(db.db)
else:
    st.error("Database not initialized. Unable to create DatabaseUploader.")

# File uploading logic
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    loaded_data = load_data_from_file(uploaded_file)

    if loaded_data:
        for table_name, df in loaded_data.items():
            st.write(f"Preview of '{table_name}':")
            st.dataframe(df.head())

            button_key = f"upload_{table_name}"
            if st.button(f"Upload '{table_name}' to SQL database", key=button_key):
                db_uploader.upload_data({table_name: df})
                st.success(f"'{table_name}' uploaded successfully.")
    else:
        st.error("No data was loaded. Please check the file format and try again.")
        
        
        
        
        #TODO  Auth to look at down the track
        
        ###***Section 1 ***###
        
        # from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        # from sqlalchemy.orm import sessionmaker
        # from your_auth_helper_module import AuthenticationHelper

        # class AsyncDatabaseManager:
        #     def __init__(self, db_type='azure', headers=None):
        #         self.db_type = db_type
        #         self.headers = headers
        #         self.auth_helper = AuthenticationHelper(
        #             # Initialization parameters...
        #         )
        #         self.engine = None

        #     async def initialize(self):
        #         if self.db_type == 'azure':
        #             access_token = await self.auth_helper.get_auth_claims_if_enabled(self.headers)
        #             if access_token:
        #                 self.engine = await self.create_azure_sql_engine(access_token["access_token"])
        #             else:
        #                 # Handle error or fallback
        #                 pass

        #     async def create_azure_sql_engine(self, access_token):
        #         token_struct = self.encode_access_token(access_token)
        #         connection_string = self.construct_connection_string(token_struct)
                
        #         # Use async engine creation
        #         engine = create_async_engine(connection_string, echo=True)
        #         return engine

        #     def encode_access_token(self, access_token):
        #         # Your existing token encoding logic
        #         pass

        #     def construct_connection_string(self, token_struct):
        #         # Your existing connection string construction logic
        #         pass

        #     async def fetch_data(self):
        #         # Example async operation using the engine
        #         async with AsyncSession(self.engine) as session:
        #             # Async operations with session
        #             pass

        ###***Section 2 - USAGE EXAMPLE ***###
        
        # async def main():
        #     db = AsyncDatabaseManager(db_type='azure', headers=request.headers)
        #     await db.initialize()
        #     # Now you can use db to perform database operations
        #     await db.fetch_data()

        # # Assuming you're using an async framework or runtime
        # # like FastAPI or running this inside an async event loop
        # import asyncio
        # asyncio.run(main())
