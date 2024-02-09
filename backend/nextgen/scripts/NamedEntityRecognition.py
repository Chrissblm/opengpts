# import os    
# from utilities.helpers.AzureFormRecognizerHelper import AzureFormRecognizerClient
# from utilities.helpers.EnvHelper import EnvHelper
# from utilities.helpers.DocumentChunkingHelper import DocumentChunkingHelper
# from utilities.helpers.DocumentProcessorHelper import DocumentProcessorHelper

# from utilities.document_chunking.Layout import LayoutDocumentChunking
# from utilities.helpers.DocumentLoadingHelper import DocumentLoadingHelper
# from utilities.document_chunking.Strategies import ChunkingSettings

# from azure.ai.textanalytics import TextAnalyticsClient


# class NamedEntityRecognition:
#     def __init__(self) -> None:
#         self.env_helper = EnvHelper()
#         self.document_loading_helper = DocumentLoadingHelper()
#         self.azure_form_recognizer_client = AzureFormRecognizerClient(
#             endpoint=self.env_helper.AZURE_FORM_RECOGNIZER_ENDPOINT,
#             key=self.env_helper.AZURE_FORM_RECOGNIZER_KEY
#         )
    
#     def perform_ner_on_invoices():
#         # Load the documents that need to be processed
#         document_loading_helper = DocumentLoadingHelper()
#         documents_to_process = document_loading_helper.load_documents()

#         # Instantiate the document chunking class
#         chunking_settings = ChunkingSettings(chunk_size=1024, chunk_overlap=256)  # Set appropriate values
#         document_chunker = LayoutDocumentChunking()

#         # Chunk the documents
#         chunked_documents = document_chunker.chunk(documents_to_process, chunking_settings)

#         # Set up the Azure Form Recognizer Client
#         env_helper = EnvHelper()
#         azure_form_recognizer_client = AzureFormRecognizerClient(
#             endpoint=env_helper.AZURE_FORM_RECOGNIZER_ENDPOINT,
#             key=env_helper.AZURE_FORM_RECOGNIZER_KEY
#         )

#         # Process each chunk with Azure Form Recognizer to extract NER
#         ner_results = []
#         for chunk in chunked_documents:
#             # You may need to adjust this call according to your implementation of AzureFormRecognizerClient
#             ner_result = azure_form_recognizer_client.begin_analyze_document_from_url(
#                 source_url=chunk.source,  # or pass the content if not using URLs
#                 use_layout=True  # Assuming you're using the layout model
#             )
#             ner_results.extend(ner_result)  # Collect results

#         # Compile the results into a structured format
#         return ner_results

# # Usage
# if __name__ == "__main__":
#     invoice_processor = InvoiceProcessor()
#     results = invoice_processor.perform_ner_on_invoices()
#     # Do something with the results, like saving to a file or database
