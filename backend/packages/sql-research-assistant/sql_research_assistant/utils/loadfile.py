
import os
import pandas as pd
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError
import sqlalchemy as sa

# from sqlalchemy import create_engine
# from sqlalchemy.types import Integer, Text, String, DateTime
# from langchain_community.utilities.sql_database import SQLDatabase # SQLDatabaseToolkit, create_sql_agent

class DocumentLoader:
    def __init__(self):
        self.file_formats = {
            "csv": pd.read_csv,
            "xls": pd.read_excel,
            "xlsx": pd.read_excel,
            "xlsm": pd.read_excel,
            "xlsb": pd.read_excel,
        }
    
    def load_file(self, uploaded_file):
        loaded_data = {}  # Dictionary to store sheet names and DataFrames
        if uploaded_file is not None:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension in self.file_formats:
                try:
                    if file_extension in ['xls', 'xlsx', 'xlsm', 'xlsb']:
                        sheets = pd.ExcelFile(uploaded_file).sheet_names
                        for sheet in sheets:
                            data = pd.read_excel(uploaded_file, sheet_name=sheet)
                            loaded_data[sheet] = data
                    else:
                        data = self.file_formats[file_extension](uploaded_file)
                        table_name = os.path.splitext(uploaded_file.name)[0]
                        loaded_data[table_name] = data
                except Exception as e:
                    st.error(f"Error loading file: {e}")
                return loaded_data
            else:
                st.error("Unsupported file format")
        return loaded_data

class DatabaseUploader:
    def __init__(self, engine):
        self.engine = engine

    def upload_data(self, data_dict):
        for table_name, data in data_dict.items():
            try:
                # Assuming `data` is a pandas DataFrame
                data.to_sql(table_name, self.engine, if_exists='replace', index=False)
                print(f"Table '{table_name}' uploaded successfully.")
            except Exception as e:
                print(f"Error uploading table {table_name} to database: {e}")
                
    def process_data(self, data, table_name):
        try:
            data.to_sql(table_name, self.engine, if_exists='replace', index=False)
            st.success(f"Table '{table_name}' created successfully.")
        except SQLAlchemyError as e:
            st.error(f"Error creating table in database: {e}")


class UploadToDB:
    def __init__(self, engine):
        self.engine = engine
        self.file_formats = {
            "csv": pd.read_csv,
            "xls": pd.read_excel,
            "xlsx": pd.read_excel,
            "xlsm": pd.read_excel,
            "xlsb": pd.read_excel,
        }

    def upload_file(self, uploaded_file):
        uploaded_data = {}  # Initialize an empty dictionary to store table names and DataFrames
        if uploaded_file is not None:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension in self.file_formats:
                try:
                    if file_extension in ['xls', 'xlsx', 'xlsm', 'xlsb']:
                        sheets = pd.ExcelFile(uploaded_file).sheet_names
                        for sheet in sheets:
                            data = pd.read_excel(uploaded_file, sheet_name=sheet)
                            self.process_data(data, sheet)
                            uploaded_data[sheet] = data  # Add the DataFrame and sheet name to the dictionary
                    else:
                        data = self.file_formats[file_extension](uploaded_file)
                        table_name = os.path.splitext(uploaded_file.name)[0]
                        self.process_data(data, table_name)
                        uploaded_data[table_name] = data  # Add the DataFrame and table name to the dictionary
                except Exception as e:
                    st.error(f"Error processing file: {e}")
                return uploaded_data  # Return the dictionary containing DataFrames and table names
            else:
                st.error("Unsupported file format")
        return uploaded_data  # Ensure function always returns a dictionary, even if empty

    def process_data(self, data, table_name):
        try:
            data.to_sql(table_name, self.engine, if_exists='replace', index=False)
            st.success(f"Table '{table_name}' created successfully.")
        except SQLAlchemyError as e:
            st.error(f"Error creating table in database: {e}")


from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_community.vectorstores import SQLiteVSS


class UnstructuredEmbedder:
    def __init__(self, engine):
        self.engine = engine
        self.file_formats = {
            "csv": pd.read_csv,
            "xls": pd.read_excel,
            "xlsx": pd.read_excel,
            "xlsm": pd.read_excel,
            "xlsb": pd.read_excel,
        }

    def upload_file(self, uploaded_file):
        uploaded_data = {}  # Initialize an empty dictionary to store table names and DataFrames
        if uploaded_file is not None:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension in self.file_formats:
                try:
                    if file_extension in ['xls', 'xlsx', 'xlsm', 'xlsb']:
                        loader = UnstructuredExcelLoader(uploaded_file)
                        documents = loader.load()

                    else:
                        data = self.file_formats[file_extension](uploaded_file)
                        table_name = os.path.splitext(uploaded_file.name)[0]
                        self.process_data(data, table_name)
                        uploaded_data[table_name] = data  # Add the DataFrame and table name to the dictionary
                except Exception as e:
                    st.error(f"Error processing file: {e}")
                return uploaded_data  # Return the dictionary containing DataFrames and table names
            else:
                st.error("Unsupported file format")
        return uploaded_data  # Ensure function always returns a dictionary, even if empty



    def upload_file(self, uploaded_file):

        # Load the Excel file into the SQL database
        loader = UnstructuredExcelLoader(uploaded_file)
        documents = loader.load()

        # Store the documents in the SQL database
        sql_store = SQLiteVSS("connection_string")
        sql_store.store_documents(documents)

        # Use the SQLVectorStore to generate embeddings for the documents
        embeddings = sql_store.embed_documents(documents)
                
                
        
# Usage in Streamlit App

# Setup your database connection here. Example for SQLite in-memory database:
# db = UploadToDB.create_engine("sqlite:///:memory:")

# Or use your SQLDB class instance's engine if integrating with Azure SQL or similar:
# sql_db_instance = SQLDB()  # Assuming this is your SQLDB class setup
# db = sql_db_instance.engine

# Then create an instance of the UploadToDB class with the engine:
# file_uploader_to_db = UploadToDB(db)

# In your Streamlit app, use the upload_file method to process uploaded files:
# uploaded_file = st.file_uploader("Choose a file")
# if uploaded_file is not None:
#     file_uploader_to_db.upload_file(uploaded_file)


# ###*** Removed from main .st app***###

# file_formats = {
#     "csv": pd.read_csv,
#     "xls": pd.read_excel,
#     "xlsx": pd.read_excel,
#     "xlsm": pd.read_excel,
#     "xlsb": pd.read_excel,
# }

# def clear_submit():
#     """
#     Clear the Submit Button State
#     Returns:

#     """
#     st.session_state["submit"] = False


# uploaded_file = st.file_uploader(
#     "Upload a Data file",
#     type=list(file_formats.keys()),
#     help="Various File formats are Support",
#     on_change=clear_submit,
# )

# @st.cache_data(ttl="2h")
# def load_data(uploaded_file):
#     table_name = ''  # Set table_name as an empty string
#     try:
#         ext = os.path.splitext(uploaded_file.name)[1][1:].lower()
#         if ext == 'xlsx' or ext == 'xls' or ext == 'xlsb':
#             sheets = pd.ExcelFile(uploaded_file).sheet_names
#             for sheet in sheets:
#                 data = pd.read_excel(uploaded_file, sheet_name=table_name)
#                 # code to upload data to SQL database
#                 upload_to_sql(data, table_name) 
#         else:
#             data = file_formats[ext](uploaded_file)
#             upload_to_sql(data, table_name)
#     except:
#         ext = uploaded_file.split(".")[-1]
#         table_name = os.path.splitext(uploaded_file)[0]
#     if ext in file_formats:
#         return file_formats[ext](uploaded_file), table_name  # Return table_name as well
#     else:
#         st.error(f"Unsupported file format: {ext}")
#         return None

# if uploaded_file:
#     df = load_data(uploaded_file)
#     table_name = df[1]

# def upload_to_sql(data, table_name):
#     # SQL code to create table and insert data
#     create_table_query = f"CREATE TABLE {table_name} ({data.columns})" 
#     insert_into_query = f"INSERT INTO {table_name} VALUES ({data.values})"
    
# def create_and_insert_tables(tables, db):
#     for table_name, df in tables.items():
#         column_names = df.columns.tolist()
#         column_types = df.dtypes.to_dict()

#         create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ("
#         for name, dtype in column_types.items():
#             if dtype == 'object':
#                 create_table_sql += f"[{name}] NVARCHAR(MAX), "
#             elif dtype == 'int64':
#                 create_table_sql += f"[{name}] INT, "
#             elif dtype == 'float64':
#                 create_table_sql += f"[{name}] FLOAT, "
#             elif dtype == 'bool':
#                 create_table_sql += f"[{name}] BIT, "
#             elif dtype == 'datetime64[ns]':
#                 create_table_sql += f"[{name}] DATETIME2, "
#         create_table_sql = create_table_sql[:-2] + ")"
#         db.execute(create_table_sql)