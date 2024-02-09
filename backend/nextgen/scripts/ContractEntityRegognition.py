
# """
# FILE: sample_recognize_custom_entities.py

# DESCRIPTION:
#     This sample demonstrates how to recognize custom entities in documents.
#     Recognizing custom entities is also available as an action type through the begin_analyze_actions API.

#     For information on regional support of custom features and how to train a model to
#     recognize custom entities, see https://aka.ms/azsdk/textanalytics/customentityrecognition

# USAGE:
#     python sample_recognize_custom_entities.py

#     Set the environment variables with your own values before running the sample:
#     1) AZURE_LANGUAGE_ENDPOINT - the endpoint to your Language resource.
#     2) AZURE_LANGUAGE_KEY - your Language subscription key
#     3) CUSTOM_ENTITIES_PROJECT_NAME - your Language Studio project name
#     4) CUSTOM_ENTITIES_DEPLOYMENT_NAME - your Language Studio deployment name
# """


# import os
# from azure.core.credentials import AzureKeyCredential
# from azure.ai.textanalytics import TextAnalyticsClient

# from azure.core.credentials import AzureKeyCredential
# from azure.ai.textanalytics import TextAnalyticsClient

# class ContractNER:
#     def __init__(self, endpoint, key, project_name, deployment_name):
#         self.text_analytics_client = TextAnalyticsClient(
#             endpoint=endpoint,
#             credential=AzureKeyCredential(key),
#         )
#         self.project_name = project_name
#         self.deployment_name = deployment_name

#     def recognize_custom_entities(self, documents):
#         poller = self.text_analytics_client.begin_recognize_custom_entities(
#             documents,
#             project_name=self.project_name,
#             deployment_name=self.deployment_name
#         )
#         result = poller.result()
#         return result



# def recognize_custom_entities() -> None:
#     from contract_ner import ContractNER
#     from ..helpers.EnvHelper import EnvHelper

#     env_helper = EnvHelper()
#     # Initialize Contract NER with the necessary configuration
#     contract_ner = ContractNER(
#         endpoint=env_helper.AZURE_LANGUAGE_ENDPOINT,
#         key=env_helper.AZURE_LANGUAGE_KEY,
#         project_name=env_helper.CUSTOM_ENTITIES_PROJECT_NAME,
#         deployment_name=env_helper.CUSTOM_ENTITIES_DEPLOYMENT_NAME
#     )

#     text_analytics_client = TextAnalyticsClient(
#         endpoint=endpoint,
#         credential=AzureKeyCredential(key),
#     )

#     with open(path_to_sample_document) as fd:
#         document = [fd.read()]

#     poller = text_analytics_client.begin_recognize_custom_entities(
#         document,
#         project_name=project_name,
#         deployment_name=deployment_name
#     )

#     document_results = poller.result()
#     for custom_entities_result in document_results:
#         if custom_entities_result.kind == "CustomEntityRecognition":
#             for entity in custom_entities_result.entities:
#                 print(
#                     "Entity '{}' has category '{}' with confidence score of '{}'".format(
#                         entity.text, entity.category, entity.confidence_score
#                     )
#                 )
#         elif custom_entities_result.is_error is True:
#             print("...Is an error with code '{}' and message '{}'".format(
#                 custom_entities_result.error.code, custom_entities_result.error.message
#                 )
#             )
