import os
import logging

from nextgen.helpers.EnvHelper import EnvHelper
from nextgen.helpers.LLMHelper import LLMHelper
 
from langchain.memory import CosmosDBChatMessageHistory
from azure.cosmos import CosmosClient, PartitionKey, exceptions

env_helper = EnvHelper()
llm_helper = LLMHelper()


cosmos = CosmosDBChatMessageHistory(
                cosmos_endpoint=os.environ['AZURE_COSMOSDB_ENDPOINT'],
                cosmos_database=os.environ['AZURE_COSMOSDB_NAME'],
                cosmos_container=os.environ['AZURE_COSMOSDB_CONTAINER_NAME'],
                connection_string=os.environ['AZURE_COMOSDB_CONNECTION_STRING'],
                # session_id=session_id,
                # user_id=user_id
            )
cosmos.prepare_cosmos()


# Initialize the Cosmos client
endpoint = os.environ("AZURE_COSMOSDB_ENDPOINT")
key = os.environ("YOUR_COSMOS_DB_PRIMARY_KEY")
# Create a Cosmos client
cosmos_client = CosmosClient(endpoint, key)

# Select a database
database_name = 'LangChainAppDB'
try:
    database = cosmos_client.create_database_if_not_exists(id=database_name)
except exceptions.CosmosResourceExistsError:
    database = cosmos_client.get_database_client(database=database_name)

# Select or create containers
assistants_container_name = 'Assistants'
threads_container_name = 'Threads'

try:
    assistants_container = database.create_container_if_not_exists(
        id=assistants_container_name, 
        partition_key=PartitionKey(path="/user_id"),
        offer_throughput=400
    )
except exceptions.CosmosResourceExistsError:
    assistants_container = database.get_container_client(assistants_container_name)

try:
    threads_container = database.create_container_if_not_exists(
        id=threads_container_name, 
        partition_key=PartitionKey(path="/user_id"),
        offer_throughput=400
    )
except exceptions.CosmosResourceExistsError:
    threads_container = database.get_container_client(threads_container_name)

# Now you can use `assistants_container` and `threads_container` to interact with your data
# For example, to query items in a container:
# items = list(assistants_container.query_items(
#     query="SELECT * FROM Assistants a WHERE a.user_id=@user_id",
#     parameters=[
#         {"name":"@user_id", "value": "<your-user-id>"}
#     ],
#     enable_cross_partition_query=True
# ))


# def get_cosmos_client():
#     cosmos_client = None
#     if env_helper.CHAT_HISTORY_ENABLED:
#         try:
#             cosmos_endpoint = f'https://{env_helper.AZURE_COSMOSDB_ACCOUNT}.documents.azure.com:443/'

#             if not env_helper.AZURE_COSMOSDB_ACCOUNT_KEY:
#                 credential = env_helper.DefaultAzureCredential()
#             else:
#                 credential = env_helper.AZURE_COSMOSDB_ACCOUNT_KEY

#             cosmos = CosmosDBChatMessageHistory(
#                             cosmosdb_endpoint=cosmos_endpoint, 
#                             credential=credential,
#                             cosmos_database=os.environ['AZURE_COSMOSDB_NAME'],
#                             cosmos_container=os.environ['AZURE_COSMOSDB_CONTAINER_NAME'],
#                             connection_string=os.environ['AZURE_COMOSDB_CONNECTION_STRING'],
#             )
#         except Exception as e:
#             logging.exception("Exception in CosmosDB initialization", e)
#             cosmos_conversation_client = None
#             raise e
#     else:
#         logging.debug("CosmosDB not configured")
        
#     return cosmos_client


# def init_cosmosdb_client():
#     cosmos_conversation_client = None
#     if CHAT_HISTORY_ENABLED:
#         try:
#             cosmos_endpoint = f'https://{AZURE_COSMOSDB_ACCOUNT}.documents.azure.com:443/'

#             if not AZURE_COSMOSDB_ACCOUNT_KEY:
#                 credential = DefaultAzureCredential()
#             else:
#                 credential = AZURE_COSMOSDB_ACCOUNT_KEY

#             cosmos_conversation_client = CosmosConversationClient(
#                 cosmosdb_endpoint=cosmos_endpoint, 
#                 credential=credential, 
#                 database_name=AZURE_COSMOSDB_DATABASE,
#                 container_name=AZURE_COSMOSDB_CONVERSATIONS_CONTAINER,
#                 enable_message_feedback=AZURE_COSMOSDB_ENABLE_FEEDBACK
#             )
#         except Exception as e:
#             logging.exception("Exception in CosmosDB initialization", e)
#             cosmos_conversation_client = None
#             raise e
#     else:
#         logging.debug("CosmosDB not configured")
        
#     return cosmos_conversation_client


# # https://github.com/microsoft/sample-app-aoai-chatGPT/blob/57698c844b89c42724ae41aed412242c61591558/backend/history/cosmosdbservice.py


# import uuid
# from datetime import datetime
# from azure.cosmos.aio import CosmosClient
# from azure.cosmos import exceptions
  
# class CosmosConversationClient():
    
#     def __init__(self, cosmosdb_endpoint: str, credential: any, database_name: str, container_name: str, enable_message_feedback: bool = False):
#         self.cosmosdb_endpoint = cosmosdb_endpoint
#         self.credential = credential
#         self.database_name = database_name
#         self.container_name = container_name
#         self.enable_message_feedback = enable_message_feedback
#         try:
#             self.cosmosdb_client = CosmosClient(self.cosmosdb_endpoint, credential=credential)
#         except exceptions.CosmosHttpResponseError as e:
#             if e.status_code == 401:
#                 raise ValueError("Invalid credentials") from e
#             else:
#                 raise ValueError("Invalid CosmosDB endpoint") from e

#         try:
#             self.database_client = self.cosmosdb_client.get_database_client(database_name)
#         except exceptions.CosmosResourceNotFoundError:
#             raise ValueError("Invalid CosmosDB database name") 
        
#         try:
#             self.container_client = self.database_client.get_container_client(container_name)
#         except exceptions.CosmosResourceNotFoundError:
#             raise ValueError("Invalid CosmosDB container name") 
        

#     async def ensure(self):
#         if not self.cosmosdb_client or not self.database_client or not self.container_client:
#             return False, "CosmosDB client not initialized correctly"
            
#         try:
#             database_info = await self.database_client.read()
#         except:
#             return False, f"CosmosDB database {self.database_name} on account {self.cosmosdb_endpoint} not found"
        
#         try:
#             container_info = await self.container_client.read()
#         except:
#             return False, f"CosmosDB container {self.container_name} not found"
            
#         return True, "CosmosDB client initialized successfully"

#     async def create_conversation(self, user_id, title = ''):
#         conversation = {
#             'id': str(uuid.uuid4()),  
#             'type': 'conversation',
#             'createdAt': datetime.utcnow().isoformat(),  
#             'updatedAt': datetime.utcnow().isoformat(),  
#             'userId': user_id,
#             'title': title
#         }
#         ## TODO: add some error handling based on the output of the upsert_item call
#         resp = await self.container_client.upsert_item(conversation)  
#         if resp:
#             return resp
#         else:
#             return False
    
#     async def upsert_conversation(self, conversation):
#         resp = await self.container_client.upsert_item(conversation)
#         if resp:
#             return resp
#         else:
#             return False

#     async def delete_conversation(self, user_id, conversation_id):
#         conversation = await self.container_client.read_item(item=conversation_id, partition_key=user_id)        
#         if conversation:
#             resp = await self.container_client.delete_item(item=conversation_id, partition_key=user_id)
#             return resp
#         else:
#             return True

        
#     async def delete_messages(self, conversation_id, user_id):
#         ## get a list of all the messages in the conversation
#         messages = await self.get_messages(user_id, conversation_id)
#         response_list = []
#         if messages:
#             for message in messages:
#                 resp = await self.container_client.delete_item(item=message['id'], partition_key=user_id)
#                 response_list.append(resp)
#             return response_list


#     async def get_conversations(self, user_id, limit, sort_order = 'DESC', offset = 0):
#         parameters = [
#             {
#                 'name': '@userId',
#                 'value': user_id
#             }
#         ]
#         query = f"SELECT * FROM c where c.userId = @userId and c.type='conversation' order by c.updatedAt {sort_order}"
#         if limit is not None:
#             query += f" offset {offset} limit {limit}" 
        
#         conversations = []
#         async for item in self.container_client.query_items(query=query, parameters=parameters):
#             conversations.append(item)
        
#         return conversations

#     async def get_conversation(self, user_id, conversation_id):
#         parameters = [
#             {
#                 'name': '@conversationId',
#                 'value': conversation_id
#             },
#             {
#                 'name': '@userId',
#                 'value': user_id
#             }
#         ]
#         query = f"SELECT * FROM c where c.id = @conversationId and c.type='conversation' and c.userId = @userId"
#         conversations = []
#         async for item in self.container_client.query_items(query=query, parameters=parameters):
#             conversations.append(item)

#         ## if no conversations are found, return None
#         if len(conversations) == 0:
#             return None
#         else:
#             return conversations[0]
 
#     async def create_message(self, uuid, conversation_id, user_id, input_message: dict):
#         message = {
#             'id': uuid,
#             'type': 'message',
#             'userId' : user_id,
#             'createdAt': datetime.utcnow().isoformat(),
#             'updatedAt': datetime.utcnow().isoformat(),
#             'conversationId' : conversation_id,
#             'role': input_message['role'],
#             'content': input_message['content']
#         }

#         if self.enable_message_feedback:
#             message['feedback'] = ''
        
#         resp = await self.container_client.upsert_item(message)  
#         if resp:
#             ## update the parent conversations's updatedAt field with the current message's createdAt datetime value
#             conversation = await self.get_conversation(user_id, conversation_id)
#             if not conversation:
#                 return "Conversation not found"
#             conversation['updatedAt'] = message['createdAt']
#             await self.upsert_conversation(conversation)
#             return resp
#         else:
#             return False
    
#     async def update_message_feedback(self, user_id, message_id, feedback):
#         message = await self.container_client.read_item(item=message_id, partition_key=user_id)
#         if message:
#             message['feedback'] = feedback
#             resp = await self.container_client.upsert_item(message)
#             return resp
#         else:
#             return False

#     async def get_messages(self, user_id, conversation_id):
#         parameters = [
#             {
#                 'name': '@conversationId',
#                 'value': conversation_id
#             },
#             {
#                 'name': '@userId',
#                 'value': user_id
#             }
#         ]
#         query = f"SELECT * FROM c WHERE c.conversationId = @conversationId AND c.type='message' AND c.userId = @userId ORDER BY c.timestamp ASC"
#         messages = []
#         async for item in self.container_client.query_items(query=query, parameters=parameters):
#             messages.append(item)

#         return messages
