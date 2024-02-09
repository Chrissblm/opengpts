

import logging
import os, sys, time
from pathlib import Path

import streamlit as st
from langchain.llms.openai import OpenAI
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase # SQLDatabaseToolkit, create_sql_agent
# from langchain_community.utilities.pebblo import get_loader_type
from langchain_community.document_loaders import PebbloSafeLoader, UnstructuredFileLoader, UnstructuredExcelLoader, UnstructuredCSVLoader, UnstructuredXMLLoader, UnstructuredHTMLLoader, unstructured
from langchain_community.document_loaders.generic import GenericLoader
from langchain.document_loaders.blob_loaders import FileSystemBlobLoader

import sqlite3
from sqlalchemy.exc import DBAPIError
from sqlalchemy import create_engine, exc, event, select, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import pandas as pd
# from langchain.agents import create_pandas_dataframe_agent

from sql_research_assistant.utils.loadfile import UploadToDB, DocumentLoader, DatabaseUploader
from nextgen.helpers.EnvHelper import EnvHelper
from nextgen.helpers.LLMHelper import NGllmhelper

env_helper = EnvHelper()

import streamlit as st

st.set_page_config(page_title="coming soon...")
st.image("sql_research_assistant/assets/Color logo - no background.png", width=100)
st.title("coming soon...")

if 'db_manager' in st.session_state:
    db = st.session_state['db_manager'].db  # Assuming db_manager.db is your SQLDatabase instance
    logging.info(f"DatabaseManager instance found. Type of db: {type(db)}")
else:
    logging.error("DatabaseManager instance not found.")

 
# User inputs for loading the LLM
radio_opt = ["Use Azure Openai", "Connect to your openai api key"]
selected_opt_llm = st.sidebar.radio(label="Choose LLM", options=radio_opt)
if selected_opt_llm == "Connect to your openai api key":
    openai_api_key = st.sidebar.text_input(
        label="OpenAI API Key",
        type="password",
    )
    llm = OpenAI(openai_api_key=openai_api_key, temperature=0, streaming=True)
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
#loads azure llm based on .env file
else:
    llms = NGllmhelper()
    llm = llms.get_openai_llm()
 
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)

if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder="Ask me anything!")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        response = agent_executor.run(user_query, callbacks=[st_cb])
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)

