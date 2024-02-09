
# """
# FILE: sample_recognize_entities.py

# Background:

# AzureBlobStorageHelper.py
#     This file likely contains functions and classes to interact with Azure Blob Storage. This could include uploading, downloading, listing, and deleting blobs.
# AzureFormRecognizerHelper.py
#     This file is expected to contain utility functions or classes that interact with the Azure Form Recognizer service. It might include methods to submit documents for analysis and retrieve the results.
# DocumentChunkingHelper.py
#     The functions within this file are probably responsible for dividing larger documents into smaller, more manageable pieces, known as chunks. This could be particularly useful for processing large files that exceed the size limits of certain APIs.
# DocumentLoadingHelper.py
#     This file should contain methods for loading documents from various sources into the application. It might support different file formats and handle data conversion as necessary.
# DocumentProcessorHelper.py
#     Here, we might find a collection of functions or a class dedicated to processing documents. This could involve cleaning, formatting, and preparing text data for analysis or further processing.
# OrchestratorHelper.py
#     The orchestrator helper is likely responsible for managing the workflow of the entire document processing pipeline. It could coordinate the order of operations and the data flow between different processing stages.
# LLMHelper.py
#     This helper could be intended to interact with large language models, possibly for generating text, summarizing, or other natural language processing tasks.
# SettingHelper.py
#     This file is expected to manage application settings, which might include configuration parameters, environment variables, and other preferences that need to be loaded and accessed throughout the application.
# EnvHelper.py
#     This helper likely deals with environment variables, providing a secure way to access sensitive information such as API keys, endpoints, and other credentials.

# CODE DESCRIPTION
#     This code will be called after documents have been chunked, so we can recognize named entities in a batch of documents.
#     Based off the Entities, we can then determine key reporting information like the organization name, the customer name, Contract Type, Expiry Date and the invoice number.

# USAGE:
#     python recognize_entities_async.py


# PROMPT: 

# """

# import os
# import json
# from azure.core.credentials import AzureKeyCredential
# from azure.ai.textanalytics.aio import TextAnalyticsClient

# from ..helpers.ConfigHelper import ConfigHelper 
# from ..helpers.EnvHelper import EnvHelper
# from ..helpers.AzureBlobStorageHelper import AzureBlobStorageClient  

# class DocumentEntityRecognizer:
#     def __init__(self):
#         # Retrieve credentials securely
#         #endpoint = EnvHelper.get_env_variable('AZURE_LANGUAGE_ENDPOINT')
#         #key = EnvHelper.get_env_variable('AZURE_LANGUAGE_KEY')

#         #self.text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
#         self.config = ConfigHelper.get_active_config_or_default()
#         self.blob_storage_client = AzureBlobStorageClient()  # Initialize your AzureBlobStorageClient

#     def recognize_entities(self, documents: list[str], filenames: list[str]) -> dict:
#         # Ensure that documents are provided
#         if not documents:
#             print("No documents provided for entity extraction.")
#             return {}

#         try:
#             # Call the service to recognize entities
#             result = self.text_analytics_client.recognize_entities(documents)
#             result = [doc for doc in result if not doc.is_error]
            
#             # Initialize a dictionary to hold the entities and corresponding document details
#             entities_to_documents = {}

#             # Iterate through the recognized entities and process them
#             for idx, doc in enumerate(result):
#                 for entity in doc.entities:
#                     if entity.category in self.config.entity_extraction_categories:  # Assuming config defines the categories to extract
#                         filename = filenames[idx]
#                         filename_parts = os.path.splitext(filename)
#                         new_filename = filename_parts[0] + '_NERExtracted' + filename_parts[1]
#                         entities_to_documents.setdefault(entity.text, []).append({
#                             'category': entity.category,
#                             'subcategory': entity.subcategory,
#                             'confidence_score': entity.confidence_score,
#                             'document_index': idx,
#                             'document_text': documents[idx],
#                             'filename': new_filename
#                         })

#             # Convert the dictionary to JSON
#             entities_json = json.dumps(entities_to_documents, indent=2)

#             # Upload the JSON to Azure Blob Storage
#             blob_name = f"{filename_parts[0]}_NERExtracted.json"  # Generate a unique blob name
#             self.blob_storage_client.upload_file(bytes_data=entities_json.encode('utf-8'), file_name=blob_name, content_type='application/json')

#             return entities_to_documents

#         except Exception as e:
#             print(f"An error occurred while extracting entities: {e}")
#             return {}

# """'''
# # Example usage
# if __name__ == '__main__':
#     recognizer = DocumentEntityRecognizer()
#     documents = []
#     entities = recognizer.recognize_entities(documents)
#     print(entities)

# """

# #-------------------------------- old alternate code ---------------------------------#

# from typing import List
# from document_chunking import DocumentChunkingBase
# from document_chunking.Strategies import ChunkingSettings
# from ..common.SourceDocument import SourceDocument
# from azure.core.credentials import AzureKeyCredential
# from azure.ai.formrecognizer import DocumentAnalysisClient

# class EntityRecognitionDocumentChunking(DocumentChunkingBase):
#     def __init__(self, endpoint: str, key: str) -> None:
#         self.document_analysis_client = DocumentAnalysisClient(
#             endpoint=endpoint, credential=AzureKeyCredential(key)
#         )
        
#     def chunk_and_recognize_entities(self, documents: List[SourceDocument], chunking: ChunkingSettings) -> List[SourceDocument]:
#         # Existing chunking logic
#         chunked_documents = super().chunk(documents, chunking)
        
#         # Process each chunked document for entity recognition
#         for document in chunked_documents:
#             poller = self.document_analysis_client.begin_analyze_document(
#                 "prebuilt-invoice", document.content
#             )
#             result = poller.result()
#             # Extract entities and append to document metadata or create a new property
#             document.entities = self.extract_entities(result)
        
#         return chunked_documents

#     @staticmethod
#     def extract_entities(analysis_result):
#         # Extract entities from the analysis_result and return them in a structured format
#         entities = []
#         # Your code to extract and structure entities goes here
#         return entities




