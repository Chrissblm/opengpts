# from langchain_community.document_loaders import UnstructuredExcelLoader
# from langchain_community.vectorstores import SQLVectorStore

# # Load the Excel file into the SQL database
# loader = UnstructuredExcelLoader("path_to_excel_file.xlsx")
# documents = loader.load()

# # Store the documents in the SQL database
# sql_store = SQLVectorStore("connection_string")
# sql_store.store_documents(documents)

# # Use the SQLVectorStore to generate embeddings for the documents
# embeddings = sql_store.embed_documents(documents)