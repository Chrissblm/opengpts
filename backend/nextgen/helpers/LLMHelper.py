import os
from functools import lru_cache

from langchain_openai import AzureChatOpenAI, ChatOpenAI, OpenAIEmbeddings, AzureOpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings, AzureChatOpenAI, AzureOpenAIEmbeddings

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from nextgen.helpers.EnvHelper import EnvHelper


# Use the current user identity to authenticate with Azure OpenAI, Cognitive Search and Blob Storage (no secrets needed,
# just use 'az login' locally, and managed identity when deployed on Azure). If you need to use keys, use separate AzureKeyCredential instances with the
# keys for each service
# If you encounter a blocking error during a DefaultAzureCredential resolution, you can exclude the problematic credential by using a parameter (ex. exclude_shared_token_cache_credential=True)
#azure_credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
# azure_credential = DefaultAzureCredential()
# token_provider = get_bearer_token_provider(azure_credential, "https://cognitiveservices.azure.com/.default")    

# import boto3
# from langchain_community.chat_models import BedrockChat, ChatAnthropic, ChatFireworks
# from langchain_google_vertexai import ChatVertexAI
# import openai

class NGllmhelper:
    def __init__(self):
        env_helper: EnvHelper = EnvHelper()
 
        #self.use_azure_active_directory = False
        #Azure Openai
        self.deployment_name = env_helper.AZURE_OPENAI_DEPLOYMENT_NAME
        self.azure_openai_api_key = env_helper.AZURE_OPENAI_API_KEY
        self.azure_openai_api_base = env_helper.AZURE_OPENAI_API_BASE
        self.azure_openai_api_version = env_helper.AZURE_OPENAI_API_VERSION
        self.embedding_model = env_helper.AZURE_OPENAI_EMBEDDING_MODEL
        self.azure_openai_endpoint = env_helper.AZURE_OPENAI_API_BASE

        #openai
        self.openai_api_key = env_helper.OPENAI_API_KEY
        
        #TODO CHeck if this is needed. Its also on EnvHelper
        # self.credential = DefaultAzureCredential()
        # os.environ["AZURE_OPENAI_AD_TOKEN"] = self.credential.get_token("https://cognitiveservices.azure.com/.default").token
        # if self.credential.get_token is None:
        #     print("Azure AD token provider is None")
        #     os.environ["AZURE_OPENAI_API_KEY"] = self.azure_openai_api_key
        # else:
        #     self.azure_openai_ad_token = self.credential.get_token
        #     os.environ["OPENAI_API_TYPE"] = "azure"  #TODO Not sure this is nessasary
        #     print("Azure AD token provided")
    
    @lru_cache(maxsize=4)
    def get_openai_llm(self, gpt_4: bool = False, azure: bool = False):
               
        if not azure:
            if gpt_4:
                llm = ChatOpenAI(model="gpt-4-1106-preview",openai_api_key=self.openai_api_key, temperature=0, streaming=True)
            else:
                llm = ChatOpenAI(model="gpt-3.5-turbo-1106",openai_api_key=self.openai_api_key, temperature=0, streaming=True)
        else:
            llm = AzureChatOpenAI(
                temperature=0,
                deployment_name=self.deployment_name,
                azure_endpoint=self.azure_openai_api_base,  
                openai_api_version=self.azure_openai_api_version,
                streaming=True,
            )
        return llm
    
    @lru_cache(maxsize=4)
    def get_openai_embedding(self, azure: bool = False):
        if not azure:
            embedding = OpenAIEmbeddings(model=self.embedding_model)
        else:
            embedding = AzureOpenAIEmbeddings(
                model=self.embedding_model,
            )
        return embedding

    @lru_cache(maxsize=4)
    def get_embedding_model(self, azure: bool = False):
        if not azure:
            embedding = OpenAIEmbeddings(model=self.embedding_model)
        else:
            embedding = AzureOpenAIEmbeddings(
                model=self.embedding_model,
            )
        return embedding
  