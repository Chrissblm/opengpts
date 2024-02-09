import logging
import os, sys, time
from pathlib import Path
import streamlit as st

from nextgen.helpers.EnvHelper import EnvHelper
from nextgen.helpers.LLMHelper import NGllmhelper
env_helper = EnvHelper()


###****  FOR TESTING ONLY ***###

from langchain.globals import set_debug
from langchain.globals import set_verbose
set_debug(True)
set_verbose(True)
logging.basicConfig(level=logging.DEBUG)
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
os.environ['PYODBC_TRACE'] = '1'

# Setup basic configuration for logging
logging.basicConfig(
    level=logging.DEBUG,  # Set minimum logging level to DEBUG
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),  # Log to stdout
        # If you also want to log to a file, uncomment the next line
        # logging.FileHandler("debug.log", mode='a'),  # Log to a file
    ]
)
   
os.environ["LANGCHAIN_PROJECT"] = "sql_streamlit"
os.environ["LANGCHAIN_API_KEY"] = env_helper.LANGCHAIN_API_KEY
os.environ["LANGCHAIN_TRACING_V2"] = env_helper.LANGCHAIN_TRACING_V2
os.environ["LANGCHAIN_ENDPOINT"] = env_helper.LANGCHAIN_ENDPOINT
os.environ["USE_AUTHENTICATION"] = env_helper.USE_AUTHENTICATION

###****  FOR TESTING ONLY ***###


st.set_page_config(
page_title="Home | Procurement",
page_icon="🧊",
layout="centered",
initial_sidebar_state="expanded",
menu_items={
    'Get Help': 'https://www.extremelycoolapp.com/help',
    'Report a bug': "https://www.extremelycoolapp.com/bug",
    'About': "# This is a header. This is an *extremely* cool app!"
}
)
mod_page_style = """
            <style>
            #MainMenu {visibility: visible;}
            footer {visibility: hidden;}
            header {visibility: visible;}
            </style>
            """
st.markdown(mod_page_style, unsafe_allow_html=True)

col1, col2, col3 = st.columns([3,1,1])
with col3:
    st.image("sql_research_assistant/assets/Color logo - no background.png", width=100)
with col1:
    st.header('Procurement.ai', divider='green')
col1, col2, col3, col4 = st.columns([2,1,1,1])

if "shared" not in st.session_state:
   st.session_state["shared"] = True
