import logging
import os
import sys
from pathlib import Path
import struct
import pyodbc
import pandas as pd
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import create_engine, exc, event, select, text, MetaData
from sqlalchemy.exc import DBAPIError
from sqlalchemy import text
from sqlalchemy.engine.url import URL

from langchain.sql_database import SQLDatabase

from azure.identity.aio import DefaultAzureCredential

from nextgen.helpers.EnvHelper import EnvHelper
env_helper = EnvHelper()

# Ensure your AuthenticationHelper is compatible with async operations
from nextgen.auth.AuthenticationHelper import AuthenticationHelper

# Add the parent directory of `sql_research_assistant` to the Python path
parent_dir = (Path(__file__).parent / "..").resolve()  # Adjust according to your structure
sys.path.insert(0, str(parent_dir))


class SQLDatabaseHelper:
    def __init__(self, db_type='temp', db_uri=None):
        self.db_type = db_type
        self.db_uri = db_uri
        self.engine = None
        self.db = None 
        self.auth_helper = None
        self.initialize_auth_helper()
        self.initialize()

    def initialize_auth_helper(self):
        # Initialize the AuthenticationHelper instance here
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
            logging.error("Failed to initialize the database connection.")

    def ensure_connection(self):
        if not self.engine or not self.is_engine_healthy():
            self.initialize()

    def is_engine_healthy(self):
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            return False

    @property
    def DATABASE_URI(self):
        return "sqlite+aiosqlite:///mydatabase.db"

    @property
    def TEMP_DATABASE_URI(self):
        return "sqlite+aiosqlite:///tempdatabase.db"

    def init_db(self, uri):
        try:
            engine = create_engine(uri, echo=True)
            with engine.connect() as conn:
                conn.execute(select(1))
            return engine
        except DBAPIError as err:
            logging.error(f"Database at {uri} is inaccessible: {err}")
            return None
        
    def setup_database(self):
        if not self.engine:
            logging.error("No database engine available for setup.")
            return
        with self.engine.begin() as conn:
            conn.execute(select(1))
            # conn.execute(text("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)"))
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
            token = credential.get_token(token_scope)
            if not token:
                logging.error("Failed to obtain access token for Azure SQL Database.")
                return None
            # Use the token to create an engine
            return self.create_token_azure_sql_engine(
                env_helper.SQL_SERVER_NAME, 
                env_helper.SQL_SERVER_DATABASE, 
                env_helper.SQL_SERVER_DRIVER,
                token.token  # Adjusted to use token directly
            )

    def create_token_azure_sql_engine(self, server, database, driver, token):
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
            logging.error("No database available to show schema.")
            return
        schema_info = self.db.get_table_info_no_throw()
        print(schema_info)


###**** TODO REVIEW IF TIME ****
# class SQLDatabaseHelper:
#     def __init__(self, db_type='temp', db_uri=None):
#         self.db_type = db_type
#         self.db_uri = db_uri
#         self.engine = None
#         self.auth_helper = AuthenticationHelper()  # Simplified for demonstration
#         self.initialize_sync()
#         self.initialize_auth_helper()  # Call the initialization method for the AuthenticationHelper

#     def initialize_auth_helper(self):
#         # Initialize the AuthenticationHelper instance here
#         use_authentication = True if os.getenv("USE_AUTHENTICATION") == "True" else False
#         server_app_id = os.getenv("SERVER_APP_ID")
#         server_app_secret = os.getenv("SERVER_APP_SECRET")
#         client_app_id = os.getenv("CLIENT_APP_ID")
#         tenant_id = os.getenv("SQL_SERVER_TENANT_ID")
#         token_cache_path = os.getenv("TOKEN_CACHE_PATH", None)

#         if not all([server_app_id, server_app_secret, client_app_id, tenant_id]):
#             logging.error("AuthenticationHelper initialization failed due to missing required arguments.")
#             return  # Early return to avoid calling the constructor with missing args

#         self.auth_helper = AuthenticationHelper(
#             use_authentication=use_authentication,
#             server_app_id=server_app_id,
#             server_app_secret=server_app_secret,
#             client_app_id=client_app_id,
#             tenant_id=tenant_id,
#             token_cache_path=token_cache_path,
#         )
    
#     def initialize_sync(self):
#         """Synchronously initializes the database engine."""
#         if self.db_type == 'azure':
#             self.engine = self.create_azure_sql_engine_sync()
#         try:
#             if self.db_type == 'temp':
#                 self.engine = self.init_db_sync(self.DATABASE_URI)
#             elif self.db_type == 'manual':
#                 self.engine = self.init_db_sync(self.db_uri)
#             elif self.db_type == 'azure':
#                 # Example Azure SQL connection setup. Adjust as needed.
#                 self.engine = self.create_azure_sql_engine_sync()
#             self.db = SQLDatabase(engine=self.engine) if self.engine else None
#             self.setup_database()
#         except Exception as e:
#             logging.error(f"Database initialization failed: {e}")
#             logging.error("Failed to initialize the database connection.")

#     def init_db_sync(self, uri):
#         try:
#             engine = create_engine(uri, echo=True)
#             with engine.connect() as conn:
#                 conn.execute(select(1))
#             return engine
#         except DBAPIError as err:
#             logging.error(f"Database at {uri} is inaccessible: {err}")
#             return None

#     def create_azure_sql_engine_sync(self):
#         """Create Azure SQL engine synchronously."""
#         if self.db_type != 'azure' or not self.auth_helper.use_authentication:
#             logging.error("Azure SQL Engine can only be created with Azure authentication enabled.")
#             return None
        
#         if env_helper.SQL_SERVER_AUTH == "keys":
#             return self.create_keys_azure_sql_engine(
#                 env_helper.SQL_SERVER_NAME, 
#                 env_helper.SQL_SERVER_DATABASE, 
#                 env_helper.SQL_SERVER_USERNAME, 
#                 env_helper.SQL_SERVER_PASSWORD, 
#                 env_helper.SQL_SERVER_DRIVER
#             )
#         else:
#             # headers = {"Authorization": "Bearer "}
#             # token = self.auth_helper.get_auth_claims_if_enabled(headers).get_cache_token()("access_token")
#             credential = DefaultAzureCredential()
#             token_scope = "https://database.windows.net/.default"
#             token = credential.get_token(token_scope).token
#             if not token:
#                 logging.error("Failed to obtain access token for Azure SQL Database.")
#                 return None
#             # Use the token to create an engine
#             return self.create_token_azure_sql_engine(
#                 env_helper.SQL_SERVER_NAME, 
#                 env_helper.SQL_SERVER_DATABASE, 
#                 env_helper.SQL_SERVER_DRIVER,
#                 token
#             )
#     def create_token_azure_sql_engine(self, server, database, driver, token):
#         # credential = DefaultAzureCredential()
#         # token_scope = "https://database.windows.net/.default"
#         # token = credential.get_token(token_scope).token
#         token_bytes = token.encode("UTF-16-LE")
#         token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
#         connection_string = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};"
#         def creator():
#             return pyodbc.connect(connection_string, attrs_before={1256: token_struct})
#         engine = create_engine("mssql+pyodbc://", creator=creator)
#         return engine
    
#     def create_keys_azure_sql_engine(self, server, database, username, password, driver):
#         connection_url = URL.create(
#             "mssql+pyodbc",
#             username=username,
#             password=password,
#             host=server,
#             database=database,
#             query={"driver": driver, "Encrypt": "yes", "TrustServerCertificate": "no", "Connection Timeout": "30"}
#         )
#         engine = create_engine(str(connection_url))
#         return engine
    
#     async def ensure_connection_async(self):
#         """Asynchronously ensures the database connection is healthy."""
#         if not self.engine or not await self.is_engine_healthy_async():
#             await self.initialize_async()

#     async def is_engine_healthy_async(self):
#         try:
#             async with self.engine.connect() as conn:
#                 await conn.execute(text("SELECT 1"))
#             return True
#         except Exception as e:
#             logging.error(f"Database connection failed: {e}")
#             return False

#     @property
#     def DATABASE_URI(self):
#         return "sqlite:///mydatabase.db"  # Sync URI

#     @property
#     def TEMP_DATABASE_URI(self):
#         return "sqlite+aiosqlite:///tempdatabase.db"  # Async URI for temp database

#     def setup_database_sync(self):
#         """Sets up database schema synchronously."""
#         if not self.engine:
#             logging.error("No database engine available for setup.")
#             return
#         with self.engine.begin() as conn:
#             conn.execute(text("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)"))
#         logging.info("Database setup complete.")

#     async def initialize_async(self):
#         """Asynchronously initializes the database engine for Azure SQL using AAD token authentication."""
#         if self.db_type == 'azure':
#             self.engine = await self.create_azure_sql_engine_async()
#         # Additional async initialization logic here

#     async def create_azure_sql_engine_async(self):
#         """Asynchronously creates Azure SQL engine using AAD token authentication."""
#         if self.db_type != 'azure':
#             logging.error("Azure SQL Engine can only be created for azure db_type.")
#             return None

#         credential = DefaultAzureCredential()
#         token_scope = "https://database.windows.net/.default"
#         token = await credential.get_token(token_scope)
#         access_token = token.token

#         # Async engine creation with token authentication
#         connection_str = f"mssql+pyodbc://@{env_helper.SQL_SERVER_NAME}/{env_helper.SQL_SERVER_DATABASE}?driver=ODBC Driver 17 for SQL Server;Authentication=ActiveDirectoryAccessToken;Encrypt=yes;TrustServerCertificate=no;"
#         engine = create_async_engine(connection_str, echo=True, connect_args={"access_token": access_token})
#         return engine

#     def setup_database(self):
#         if not self.engine:
#             logging.error("No database engine available for setup.")
#             return
#         # # Database schema setup logic here
#         # metadata = MetaData()
#         # # Define your tables here with metadata.create_all(engine)
#         # # For example, to keep the initial test table:
#         with self.engine.begin() as conn:
#             conn.execute(text("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)"))
#         logging.info("Database setup complete.")
    
    
        
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




#TODO future optimisation

# Optimizing your code for speed and reducing congestion, especially when interacting with databases, involves several strategies. Here's how you can optimize your current setup:

# 1. Connection Pooling
    # SQLAlchemy automatically uses connection pooling when you create an engine instance. This means that connections are reused rather than being created and destroyed with each use, which significantly reduces overhead. However, you can further customize the pool size and overflow behavior to better match your application's workload.

    # python
    # Copy code
    # from sqlalchemy.pool import QueuePool

    # engine = create_engine("mssql+pyodbc://", creator=creator, poolclass=QueuePool, pool_size=10, max_overflow=20)
    # This configuration sets a pool of 10 connections with the ability to temporarily exceed the pool size by 20 connections if necessary.

# 2. Efficient Queries
    # Indexing: Ensure that your database tables are properly indexed. This is particularly important for columns that you frequently query against.
    # Batch Operations: If you're inserting, updating, or deleting many records at once, batch those operations to reduce the number of round-trips to the database.
    # Query Optimization: Review and optimize your SQL queries. Avoid using SELECT * in favor of specifying only the columns you need. Use joins efficiently and where necessary, consider using views or stored procedures.
 
# 3. Asynchronous Operations
    # Consider using asynchronous database access if your framework and database driver support it. Asynchronous operations can improve the performance of I/O-bound applications by not blocking the main execution thread.

# 4. Caching
    # Implement caching for frequently accessed data that doesn't change often. This can significantly reduce database load and improve application performance.

# 5. Minimize Data Transfer
    # Only fetch the data you need. Avoid fetching large amounts of data that you'll filter in your application code.
    # For large datasets, consider pagination or streaming results if supported by your database driver.

# 6. Concurrency and Parallelism
    # Use threading or multiprocessing to perform concurrent database operations, especially for tasks that can be parallelized without leading to race conditions.
    # Be cautious with the number of concurrent operations to avoid overwhelming the database.

# 7. Monitor and Analyze
    # Utilize monitoring and performance analysis tools to understand where bottlenecks occur. Azure provides monitoring tools that can help identify slow queries, resource contention, and other potential performance issues.

# 8. Database-Specific Features
    # Leverage database-specific features and optimizations. Azure SQL Database offers features like Automatic Tuning, which automatically manages indexes and query performance.

# 9. Avoid Repeated Authentications
    # In your current setup, you fetch a new token for each engine creation. If your operations allow, consider reusing the token across multiple connections or refreshing it only when it's close to expiration.

    # By implementing these strategies, you can optimize your application for better performance and reduced database load. Each application and workload is unique, so it's important to measure and adjust based on your specific performance metrics and requirements.

    # User
    # give me example code for each of the options above
    # GPT
    # Sure, let's go through each optimization strategy with example code snippets or explanations.

# 1. Connection Pooling
    # python
    # Copy code
    # from sqlalchemy import create_engine
    # from sqlalchemy.pool import QueuePool

    # # Use a custom connection creator with specific pooling options
    # engine = create_engine(
    #     "mssql+pyodbc://",
    #     creator=creator,
    #     poolclass=QueuePool,
    #     pool_size=10,  # The size of the pool to be maintained
    #     max_overflow=20  # The number of connections to allow in overflow
    # )

# 2. Efficient Queries
    # Indexing: This is done on the database side, for example, CREATE INDEX idx_column_name ON table_name(column_name);.
    # Batch Operations:
    # python
    # Copy code
    # from sqlalchemy import insert

    # # Insert multiple records in a single query
    # conn.execute(
    #     table.insert(),
    #     [{"column_name": "value1"}, {"column_name": "value2"}]
    # )
    # Query Optimization:
    # python
    # Copy code
    # # Instead of SELECT *
    # query = select([table.c.column1, table.c.column2]).where(table.c.column1 == 'value')

# 3. Asynchronous Operations
    # python
    # Copy code
    # # SQLAlchemy 1.4+ supports async operations
    # from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    # from sqlalchemy.orm import sessionmaker

    # async_engine = create_async_engine("mssql+pyodbc+async://", creator=creator)
    # AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession)

    # async with AsyncSessionLocal() as session:
    #     result = await session.execute(select(MyModel))
    #     data = result.scalars().all()

# 4. Caching
    # python
    # Copy code
    # # Example using a simple Python dictionary for caching
    # my_cache = {}

    # def get_data(key):
    #     if key in my_cache:
    #         return my_cache[key]
    #     else:
    #         data = fetch_data_from_db(key)  # Assume this is a function to fetch data
    #         my_cache[key] = data
    #         return data

# 5. Minimize Data Transfer
    # python
    # Copy code
    # # Pagination example
    # query = select([table]).limit(100).offset(200)  # Get 100 records, starting from the 201st record

# 6. Concurrency and Parallelism
    # python
    # Copy code
    # from concurrent.futures import ThreadPoolExecutor

    # def fetch_data(id):
    #     # Function to fetch data from the database
    #     pass

    # # Using ThreadPoolExecutor to run database fetches in parallel
    # with ThreadPoolExecutor(max_workers=5) as executor:
    #     futures = [executor.submit(fetch_data, id) for id in range(10)]
    #     results = [f.result() for f in futures]

# 7. Monitor and Analyze
    # Utilize Azure's monitoring tools through the Azure portal or Azure Monitor APIs to track performance metrics.

# 8. Database-Specific Features
    # Explore Azure SQL Database's Automatic Tuning for self-tuning capabilities.

# 9. Avoid Repeated Authentications
    # Reuse tokens:
    # python
    # Copy code
    # # Assuming `credential` and `get_token` is set up to fetch Azure AD tokens
    # token = credential.get_token(token_scope).token  # Fetch once and reuse if not expired
    # For the token reuse strategy, ensure your application logic checks the token's expiration and refreshes it as needed, rather than fetching a new token for every connection or query.
    
    
    