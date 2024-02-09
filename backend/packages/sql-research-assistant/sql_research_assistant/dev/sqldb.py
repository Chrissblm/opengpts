
import tempfile
import os, sys
from pathlib import Path
import logging
import struct, pyodbc
from sqlalchemy import create_engine, event
from sqlalchemy.engine.url import URL
from azure.identity import DefaultAzureCredential

from langchain_community.utilities.sql_database import SQLDatabase # SQLDatabaseToolkit, create_sql_agent

from nextgen.helpers.EnvHelper import EnvHelper
from nextgen.helpers.LLMHelper import NGllmhelper
# from dotenv import load_dotenv
from nextgen.auth.AuthenticationHelper import AuthenticationHelper

logging.basicConfig(level=logging.INFO)
env_helper = EnvHelper()
llms = NGllmhelper()
llm = llms.get_openai_llm()

# Add the parent directory of `sql_research_assistant` to the Python path
parent_dir = (Path(__file__).parent / "..").resolve()  # Adjust according to your structure
sys.path.insert(0, str(parent_dir))

class SQLDB:
    def __init__(self, db_type=None, db_uri=None):
        self.engine = None
        # self.db = None
            
        try:
            if db_type == 'temp':
                # Assuming you want to use an SQLite database stored in 'assets/database.db'
                db_filepath = (Path(__file__).parent/ "sql_research_assistant/assets/database.db").absolute()
                self.engine = create_engine(f'sqlite:///{db_filepath}')
                self.db = SQLDatabase(engine=self.engine)

            elif db_type == 'manual':
                # Correctly handle the manual case by directly using the provided URI
                if db_uri:
                    self.engine = create_engine(db_uri)
                    
            elif db_type == 'azure':
                self.server = env_helper.SQL_SERVER_NAME
                self.database = env_helper.SQL_SERVER_DATABASE
                self.username = env_helper.SQL_SERVER_USERNAME
                self.password = env_helper.SQL_SERVER_PASSWORD
                self.driver = env_helper.SQL_SERVER_DRIVER
                if env_helper.SQL_SERVER_AUTH == "keys":
                    self.engine = self.create_keys_azure_sql_engine(self.server, self.database, self.username, self.password, self.driver)
                else:
                    self.engine = self.create_token_azure_sql_engine(self.server, self.database, self.driver)

            if self.engine:
                self.db = SQLDatabase(engine=self.engine)

            # else:
            #     self.db = None
            #     raise Exception("Failed to initialize database engine.")
        
        except Exception as e:
            print(f"Error initializing SQLDB: {e}")
            self.db = None
            # Consider a fallback or re-raise the exception with more context
            
            
    def create_token_azure_sql_engine(self, server, database, driver):
        credential = DefaultAzureCredential()
        # Define the scope for the token and fetch
        token_scope = "https://database.windows.net/.default"
        token = credential.get_token(token_scope).token

        # Encode the token for use in the connection
        token_bytes = token.encode("UTF-16-LE")
        token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
        connection_string = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};"
        
        # Custom creator function to use with SQLAlchemy
        def creator():
            return pyodbc.connect(connection_string, attrs_before={1256: token_struct})
        
        # Create the SQLAlchemy engine using the custom connection creator
        engine = create_engine("mssql+pyodbc://", creator=creator)
        return engine
    
    def create_keys_azure_sql_engine(self, server, database, username, password, driver):
        # Construct the connection URL
        connection_url = URL.create(
            "mssql+pyodbc",
            username=username,
            password=password,
            host=server,
            database=database,
            query={
                "driver": driver,
                "Encrypt": "yes",
                "TrustServerCertificate": "no",
                "Connection Timeout": "30",
            },
        )
        # Use the from_uri class method to create the SQLDatabase instance
        engine = SQLDatabase.from_uri(str(connection_url))
        return engine
    
    def create_local_sqllite_engine(self):
        # # Create a temporary file for SQLite database
        # temp_db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        # temp_db_file_path = temp_db_file.name
        # temp_db_file.close()  # Close the file so SQLAlchemy can use it
        
        # Create an engine linked to the temporary file
        db_filepath = (Path(__file__)/ "sql_research_assistant/assets/database.db").absolute()
        engine = create_engine(f'sqlite:///{db_filepath}')
        print(f"Temporary SQLite database created at: {db_filepath}")
        
        return engine

