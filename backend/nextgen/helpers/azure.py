
#https://github.com/microsoft/sample-app-aoai-chatGPT/blob/57698c844b89c42724ae41aed412242c61591558/app.py#L251

# import os
# import logging

# from openai import AsyncAzureOpenAI
# from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider
# from nextgen.auth.auth_utils import get_authenticated_user_details
# from backend.history.cosmosdbservice import CosmosConversationClient

# from backend.utils import format_as_ndjson, format_stream_response, generateFilterString, parse_multi_columns, format_non_streaming_response

# Frontend Settings via Environment Variables
# AUTH_ENABLED = os.environ.get("AUTH_ENABLED", "true").lower() == "true"

# CHAT_HISTORY_ENABLED = AZURE_COSMOSDB_ACCOUNT and AZURE_COSMOSDB_DATABASE and AZURE_COSMOSDB_CONVERSATIONS_CONTAINER
# frontend_settings = { 
#     "auth_enabled": AUTH_ENABLED, 
#     "feedback_enabled": AZURE_COSMOSDB_ENABLE_FEEDBACK and CHAT_HISTORY_ENABLED,
# }

# # Chat History CosmosDB Integration Settings
# AZURE_COSMOSDB_DATABASE = os.environ.get("AZURE_COSMOSDB_DATABASE")
# AZURE_COSMOSDB_ACCOUNT = os.environ.get("AZURE_COSMOSDB_ACCOUNT")
# AZURE_COSMOSDB_CONVERSATIONS_CONTAINER = os.environ.get("AZURE_COSMOSDB_CONVERSATIONS_CONTAINER")
# AZURE_COSMOSDB_ACCOUNT_KEY = os.environ.get("AZURE_COSMOSDB_ACCOUNT_KEY")
# AZURE_COSMOSDB_ENABLE_FEEDBACK = os.environ.get("AZURE_COSMOSDB_ENABLE_FEEDBACK", "false").lower() == "true"


# # CosmosDB Mongo vcore vector db Settings
# AZURE_COSMOSDB_MONGO_VCORE_CONNECTION_STRING = os.environ.get("AZURE_COSMOSDB_MONGO_VCORE_CONNECTION_STRING")  #This has to be secure string
# AZURE_COSMOSDB_MONGO_VCORE_DATABASE = os.environ.get("AZURE_COSMOSDB_MONGO_VCORE_DATABASE")
# AZURE_COSMOSDB_MONGO_VCORE_CONTAINER = os.environ.get("AZURE_COSMOSDB_MONGO_VCORE_CONTAINER")
# AZURE_COSMOSDB_MONGO_VCORE_INDEX = os.environ.get("AZURE_COSMOSDB_MONGO_VCORE_INDEX")
# AZURE_COSMOSDB_MONGO_VCORE_TOP_K = os.environ.get("AZURE_COSMOSDB_MONGO_VCORE_TOP_K", AZURE_SEARCH_TOP_K)
# AZURE_COSMOSDB_MONGO_VCORE_STRICTNESS = os.environ.get("AZURE_COSMOSDB_MONGO_VCORE_STRICTNESS", AZURE_SEARCH_STRICTNESS)  
# AZURE_COSMOSDB_MONGO_VCORE_ENABLE_IN_DOMAIN = os.environ.get("AZURE_COSMOSDB_MONGO_VCORE_ENABLE_IN_DOMAIN", AZURE_SEARCH_ENABLE_IN_DOMAIN)
# AZURE_COSMOSDB_MONGO_VCORE_CONTENT_COLUMNS = os.environ.get("AZURE_COSMOSDB_MONGO_VCORE_CONTENT_COLUMNS", "")
# AZURE_COSMOSDB_MONGO_VCORE_FILENAME_COLUMN = os.environ.get("AZURE_COSMOSDB_MONGO_VCORE_FILENAME_COLUMN")
# AZURE_COSMOSDB_MONGO_VCORE_TITLE_COLUMN = os.environ.get("AZURE_COSMOSDB_MONGO_VCORE_TITLE_COLUMN")
# AZURE_COSMOSDB_MONGO_VCORE_URL_COLUMN = os.environ.get("AZURE_COSMOSDB_MONGO_VCORE_URL_COLUMN")
# AZURE_COSMOSDB_MONGO_VCORE_VECTOR_COLUMNS = os.environ.get("AZURE_COSMOSDB_MONGO_VCORE_VECTOR_COLUMNS")

# # On Your Data Settings
# DATASOURCE_TYPE = os.environ.get("DATASOURCE_TYPE", "AzureCognitiveSearch")
# SEARCH_TOP_K = os.environ.get("SEARCH_TOP_K", 5)
# SEARCH_STRICTNESS = os.environ.get("SEARCH_STRICTNESS", 3)
# SEARCH_ENABLE_IN_DOMAIN = os.environ.get("SEARCH_ENABLE_IN_DOMAIN", "true")

# # ACS Integration Settings
# AZURE_SEARCH_SERVICE = os.environ.get("AZURE_SEARCH_SERVICE")
# AZURE_SEARCH_INDEX = os.environ.get("AZURE_SEARCH_INDEX")
# AZURE_SEARCH_KEY = os.environ.get("AZURE_SEARCH_KEY", None)
# AZURE_SEARCH_USE_SEMANTIC_SEARCH = os.environ.get("AZURE_SEARCH_USE_SEMANTIC_SEARCH", "false")
# AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG = os.environ.get("AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG", "default")
# AZURE_SEARCH_TOP_K = os.environ.get("AZURE_SEARCH_TOP_K", SEARCH_TOP_K)
# AZURE_SEARCH_ENABLE_IN_DOMAIN = os.environ.get("AZURE_SEARCH_ENABLE_IN_DOMAIN", SEARCH_ENABLE_IN_DOMAIN)
# AZURE_SEARCH_CONTENT_COLUMNS = os.environ.get("AZURE_SEARCH_CONTENT_COLUMNS")
# AZURE_SEARCH_FILENAME_COLUMN = os.environ.get("AZURE_SEARCH_FILENAME_COLUMN")
# AZURE_SEARCH_TITLE_COLUMN = os.environ.get("AZURE_SEARCH_TITLE_COLUMN")
# AZURE_SEARCH_URL_COLUMN = os.environ.get("AZURE_SEARCH_URL_COLUMN")
# AZURE_SEARCH_VECTOR_COLUMNS = os.environ.get("AZURE_SEARCH_VECTOR_COLUMNS")
# AZURE_SEARCH_QUERY_TYPE = os.environ.get("AZURE_SEARCH_QUERY_TYPE")
# AZURE_SEARCH_PERMITTED_GROUPS_COLUMN = os.environ.get("AZURE_SEARCH_PERMITTED_GROUPS_COLUMN")
# AZURE_SEARCH_STRICTNESS = os.environ.get("AZURE_SEARCH_STRICTNESS", SEARCH_STRICTNESS)




# def should_use_data():
#     global DATASOURCE_TYPE
#     if AZURE_SEARCH_SERVICE and AZURE_SEARCH_INDEX:
#         DATASOURCE_TYPE = "AzureCognitiveSearch"
#         logging.debug("Using Azure Cognitive Search")
#         return True
    
#     if AZURE_COSMOSDB_MONGO_VCORE_DATABASE and AZURE_COSMOSDB_MONGO_VCORE_CONTAINER and AZURE_COSMOSDB_MONGO_VCORE_INDEX and AZURE_COSMOSDB_MONGO_VCORE_CONNECTION_STRING:
#         DATASOURCE_TYPE = "AzureCosmosDB"
#         logging.debug("Using Azure CosmosDB Mongo vcore")
#         return True
    
#     # if ELASTICSEARCH_ENDPOINT and ELASTICSEARCH_ENCODED_API_KEY and ELASTICSEARCH_INDEX:
#     #     DATASOURCE_TYPE = "Elasticsearch"
#     #     logging.debug("Using Elasticsearch")
#     #     return True
    
#     # if PINECONE_ENVIRONMENT and PINECONE_API_KEY and PINECONE_INDEX_NAME:
#     #     DATASOURCE_TYPE = "Pinecone"
#     #     logging.debug("Using Pinecone")
#     #     return True
    
#     # if AZURE_MLINDEX_NAME and AZURE_MLINDEX_VERSION and AZURE_ML_PROJECT_RESOURCE_ID:
#     #     DATASOURCE_TYPE = "AzureMLIndex"
#     #     logging.debug("Using Azure ML Index")
#     #     return True

#     return False

    
# SHOULD_USE_DATA = should_use_data()


# SHOULD_STREAM = True if AZURE_OPENAI_STREAM.lower() == "true" else False
# # Initialize Azure OpenAI Client
# def init_openai_client(use_data=SHOULD_USE_DATA):
#     azure_openai_client = None
#     try:
#         # Endpoint
#         if not AZURE_OPENAI_ENDPOINT and not AZURE_OPENAI_RESOURCE:
#             raise Exception("AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_RESOURCE is required")
        
#         endpoint = AZURE_OPENAI_ENDPOINT if AZURE_OPENAI_ENDPOINT else f"https://{AZURE_OPENAI_RESOURCE}.openai.azure.com/"
        
#         # Authentication
#         aoai_api_key = AZURE_OPENAI_KEY
#         ad_token_provider = None
#         if not aoai_api_key:
#             logging.debug("No AZURE_OPENAI_KEY found, using Azure AD auth")
#             ad_token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

#         # Deployment
#         deployment = AZURE_OPENAI_MODEL
#         if not deployment:
#             raise Exception("AZURE_OPENAI_MODEL is required")

#         # Default Headers
#         default_headers = {
#             'x-ms-useragent': USER_AGENT
#         }

#         if use_data:
#             base_url = f"{str(endpoint).rstrip('/')}/openai/deployments/{deployment}/extensions"
#             azure_openai_client = AsyncAzureOpenAI(
#                 base_url=str(base_url),
#                 api_version=AZURE_OPENAI_PREVIEW_API_VERSION,
#                 api_key=aoai_api_key,
#                 azure_ad_token_provider=ad_token_provider,
#                 default_headers=default_headers,
#             )
#         else:
#             azure_openai_client = AsyncAzureOpenAI(
#                 api_version=AZURE_OPENAI_PREVIEW_API_VERSION,
#                 api_key=aoai_api_key,
#                 azure_ad_token_provider=ad_token_provider,
#                 default_headers=default_headers,
#                 azure_endpoint=endpoint
#             )
#         return azure_openai_client
#     except Exception as e:
#         logging.exception("Exception in Azure OpenAI initialization", e)
#         azure_openai_client = None
#         raise e