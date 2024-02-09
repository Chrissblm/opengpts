import os
import logging
from dotenv import load_dotenv
from pathlib import Path
from azure.identity import DefaultAzureCredential

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

logger = logging.getLogger(__name__)


class EnvHelper:
    def __init__(self, **kwargs) -> None:
        # Check if running in Docker or Azure
        if "DOCKER" in os.environ or "WEBSITE_SITE_NAME" in os.environ:
            print("Running in Docker or Azure, skipping .env file load")
        else:
            load_success = load_dotenv()
            if load_success:
                print(".env file has been loaded")
            else:
                print("Failed to load .env file")
       
        # Azure Search
        self.AZURE_SEARCH_SERVICE = os.getenv('AZURE_SEARCH_SERVICE', '')
        self.AZURE_SEARCH_SERVICE_NAME = os.getenv('AZURE_COGNITIVE_SEARCH_SERVICE_NAME', '')
        self.AZURE_COGNITIVE_SEARCH_SERVICE_NAME = os.getenv('AZURE_COGNITIVE_SEARCH_SERVICE_NAME', '')
        self.AZURE_SEARCH_INDEX = os.getenv('AZURE_SEARCH_INDEX', '')
        self.AZURE_SEARCH_KEY = os.getenv('AZURE_SEARCH_KEY', '')
        self.AZURE_SEARCH_USE_SEMANTIC_SEARCH = os.getenv('AZURE_SEARCH_USE_SEMANTIC_SEARCH', '')
        self.AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG = os.getenv('AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG', '')
        self.AZURE_SEARCH_INDEX_IS_PRECHUNKED = os.getenv('AZURE_SEARCH_INDEX_IS_PRECHUNKED', '')
        self.AZURE_SEARCH_TOP_K = os.getenv('AZURE_SEARCH_TOP_K', '')
        self.AZURE_SEARCH_ENABLE_IN_DOMAIN = os.getenv('AZURE_SEARCH_ENABLE_IN_DOMAIN', '')
        self.AZURE_SEARCH_FIELDS_ID = os.getenv('AZURE_SEARCH_FIELDS_ID', 'id')
        self.AZURE_SEARCH_CONTENT_COLUMNS = os.getenv('AZURE_SEARCH_CONTENT_COLUMNS', 'content')
        self.AZURE_SEARCH_CONTENT_VECTOR_COLUMNS = os.getenv('AZURE_SEARCH_CONTENT_VECTOR_COLUMNS', 'content_vector')
        self.AZURE_SEARCH_DIMENSIONS = os.getenv('AZURE_SEARCH_DIMENSIONS', '1536')
        self.AZURE_SEARCH_FILENAME_COLUMN = os.getenv('AZURE_SEARCH_FILENAME_COLUMN', 'filepath')
        self.AZURE_SEARCH_TITLE_COLUMN = os.getenv('AZURE_SEARCH_TITLE_COLUMN', 'title')
        self.AZURE_SEARCH_URL_COLUMN = os.getenv('AZURE_SEARCH_URL_COLUMN', 'url')
        self.AZURE_SEARCH_FIELDS_TAG = os.getenv('AZURE_SEARCH_FIELDS_TAG', 'tag')
        self.AZURE_SEARCH_FIELDS_METADATA = os.getenv('AZURE_SEARCH_FIELDS_METADATA', 'metadata')
        self.AZURE_SEARCH_CONVERSATIONS_LOG_INDEX = os.getenv('AZURE_SEARCH_CONVERSATIONS_LOG_INDEX', 'conversations')
         
        # self.OPENAI_DEPLOYMENT_TYPE = os.getenv('OPENAI_DEPLOYMENT_TYPE', '')
                # self.AZURE_OPENAI_DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', '')
        self.AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', '')
        self.AZURE_OPENAI_API_BASE = f"https://{os.getenv('AZURE_OPENAI_RESOURCE')}.openai.azure.com/"
        self.AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", f"https://{os.getenv('AZURE_OPENAI_RESOURCE')}.openai.azure.com/")
        #self.AZURE_OPENAI_SERVICE = os.getenv('AZURE_OPENAI_SERVICE', '')
        self.AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY', '')
        # self.AZURE_OPENAI_MAX_TOKENS_GPT4 = os.getenv('AZURE_OPENAI_MAX_TOKENS_GPT4', '')
        # self.AZURE_OPENAI_MAX_TOKENS_GPT35 = os.getenv('AZURE_OPENAI_MAX_TOKENS_GPT35', '')
        # self.AZURE_OPENAI_MODEL_GPT4 = os.getenv('AZURE_OPENAI_MODEL_GPT4', '')
        # self.AZURE_OPENAI_MODEL_NAME_GPT4 = os.getenv('AZURE_OPENAI_MODEL_NAME_GPT4', '') #replace defaults
        
        # Azure OpenAI
        self.AZURE_OPENAI_RESOURCE = os.getenv('AZURE_OPENAI_RESOURCE', '')
        # self.AZURE_OPENAI_MODEL = os.getenv('AZURE_OPENAI_MODEL', '')
        # self.AZURE_OPENAI_KEY = os.getenv('AZURE_OPENAI_KEY', '')
        # self.AZURE_OPENAI_MODEL_NAME = os.getenv('AZURE_OPENAI_MODEL_NAME', '')
        # self.AZURE_OPENAI_TEMPERATURE = os.getenv('AZURE_OPENAI_TEMPERATURE', '')
        # self.AZURE_OPENAI_TOP_P = os.getenv('AZURE_OPENAI_TOP_P', '')
        # self.AZURE_OPENAI_MAX_TOKENS = os.getenv('AZURE_OPENAI_MAX_TOKENS', '')
        # self.AZURE_OPENAI_STOP_SEQUENCE = os.getenv('AZURE_OPENAI_STOP_SEQUENCE', '')
        # self.AZURE_OPENAI_SYSTEM_MESSAGE = os.getenv('AZURE_OPENAI_SYSTEM_MESSAGE', '')
        # self.AZURE_OPENAI_STREAM = os.getenv('AZURE_OPENAI_STREAM', '')
        self.AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '')
        os.environ["OPENAI_API_VERSION"] = self.AZURE_OPENAI_API_VERSION
        self.AZURE_OPENAI_EMBEDDING_MODEL = os.getenv('AZURE_OPENAI_EMBEDDING_MODEL', '')

        # Set env for OpenAI SDK
        self.AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY', '')

        self.AZURE_AUTH_TYPE = os.environ.get("AZURE_AUTH_TYPE", "keys")
        self.OPENAI_API_TYPE = "azure" if self.AZURE_AUTH_TYPE == "keys" else "azure_ad"
        if self.AZURE_AUTH_TYPE == "keys": 
            self.AZURE_OPENAI_API_KEY = self.AZURE_OPENAI_API_KEY
            self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
            os.environ["OPENAI_API_KEY"] = self.OPENAI_API_KEY
        else:
            self.AZURE_OPENAI_API_KEY = DefaultAzureCredential(exclude_shared_token_cache_credential=True).get_token("https://cognitiveservices.azure.com/.default").token
            print("authenticaed via Azure AD")

        #openai settings
        self.OPENAI_API_VERSION = os.getenv('OPENAI_API_VERSION', '')
        # self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
        # os.environ["OPENAI_API_VERSION"] = self.OPENAI_API_VERSION
        # os.environ["OPENAI_API_KEY"] = self.OPENAI_API_KEY
        
        # Azure Functions - Batch processing
        # self.BACKEND_URL = os.getenv('BACKEND_URL', '')
        # self.AzureWebJobsStorage = os.getenv('AzureWebJobsStorage', '')
        # self.DOCUMENT_PROCESSING_QUEUE_NAME = os.getenv('DOCUMENT_PROCESSING_QUEUE_NAME', '')
        # # Azure Blob Storageå
        # self.AZURE_BLOB_ACCOUNT_NAME = os.getenv('AZURE_BLOB_ACCOUNT_NAME', '')
        # self.AZURE_BLOB_ACCOUNT_KEY = os.getenv('AZURE_BLOB_ACCOUNT_KEY', '')
        # self.AZURE_BLOB_CONTAINER_NAME = os.getenv('AZURE_BLOB_CONTAINER_NAME', '')
        # # Azure Form Recognizer
        # self.AZURE_FORM_RECOGNIZER_ENDPOINT = os.getenv('AZURE_FORM_RECOGNIZER_ENDPOINT', '')
        # self.AZURE_FORM_RECOGNIZER_KEY = os.getenv('AZURE_FORM_RECOGNIZER_KEY', '')
        # # Azure App Insights
        # self.APPINSIGHTS_CONNECTION_STRING = os.getenv('APPINSIGHTS_CONNECTION_STRING', '')
        # # Azure AI Content Safety
        # self.AZURE_CONTENT_SAFETY_ENDPOINT = os.getenv('AZURE_CONTENT_SAFETY_ENDPOINT', '')
        # if 'https' not in self.AZURE_CONTENT_SAFETY_ENDPOINT and 'api.cognitive.microsoft.com' not in self.AZURE_CONTENT_SAFETY_ENDPOINT:
        #     self.AZURE_CONTENT_SAFETY_ENDPOINT = self.AZURE_FORM_RECOGNIZER_ENDPOINT
        # self.AZURE_CONTENT_SAFETY_KEY = os.getenv('AZURE_CONTENT_SAFETY_KEY', '')
        # # Orchestration Settings
        # self.ORCHESTRATION_STRATEGY = os.getenv('ORCHESTRATION_STRATEGY', 'openai_function')

###*****  #NGP Added .env
        #search
        self.TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', '')
        os.environ["TAVILY_API_KEY"] = self.TAVILY_API_KEY

        self.LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY','')
        self.LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2', '')
        self.LANGCHAIN_PROJECT = os.getenv('LANGCHAIN_PROJECT', '')
        self.LANGCHAIN_ENDPOINT = os.getenv('LANGCHAIN_ENDPOINT', '')
        os.environ["LANGCHAIN_API_KEY"] = self.LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_TRACING_V2"] = self.LANGCHAIN_TRACING_V2
        # os.environ["LANGCHAIN_PROJECT"] = self.LANGCHAIN_PROJECT
        os.environ["LANGCHAIN_ENDPOINT"] = self.LANGCHAIN_ENDPOINT
        
        self.REDIS_URL = os.getenv('REDIS_URL', '')
        os.environ['REDIS_URL'] = self.REDIS_URL
        
        
        # Access sql environment variables
        self.SQL_SERVER_NAME = os.getenv('SQL_SERVER_NAME')
        self.SQL_SERVER_DATABASE = os.getenv('SQL_SERVER_DATABASE')
        self.SQL_SERVER_USERNAME = os.getenv('SQL_SERVER_USERNAME')
        self.SQL_SERVER_PASSWORD = os.getenv('SQL_SERVER_PASSWORD')
        self.SQL_SERVER_TENANT_ID = os.getenv('SQL_SERVER_TENANT_ID')
        self.SQL_SERVER_DRIVER = os.getenv('SQL_SERVER_DRIVER', 'ODBC Driver 18 for SQL Server')  
        self.SQL_SERVER_AUTH = os.getenv('SQL_SERVER_AUTH', 'rbac')
        self.USE_AUTHENTICATION = os.getenv('USE_AUTHENTICATION', 'True')

        # self.CHAT_HISTORY_ENABLED = os.getenv('CHAT_HISTORY_ENABLED', 'false')
        # self.AZURE_BLOB_SAS_TOKEN = os.getenv('AZURE_BLOB_SAS_TOKEN', '')

        #vector storage approach
        #self.VECTOR_STORE_TYPE = os.getenv('VECTOR_STORE_TYPE', 'AzureSearch')
        
        self.ROBOCORP_ACTION_SERVER_URL = os.getenv('ROBOCORP_ACTION_SERVER_URL', '')
        self.ROBOCORP_ACTION_SERVER_KEY = os.getenv('ROBOCORP_ACTION_SERVER_KEY', '')
        os.environ["ROBOCORP_ACTION_SERVER_URL"] = self.ROBOCORP_ACTION_SERVER_URL
        os.environ["ROBOCORP_ACTION_SERVER_KEY"] = self.ROBOCORP_ACTION_SERVER_KEY

    @staticmethod
    def check_env():
        for attr, value in EnvHelper().__dict__.items():
            if value == '':
                logging.warning(f"{attr} is not set in the environment variables.")




# FIREWORKS_API_KEY: your_secret_here
# YDC_API_KEY: your_secret_here
# KAY_API_KEY: your_secret_here
# CONNERY_RUNNER_URL: https://your-personal-connery-runner-url
# CONNERY_RUNNER_API_KEY: your_secret_here
