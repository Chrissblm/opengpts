from pathlib import Path

from langchain.memory import ConversationBufferMemory
from langchain.pydantic_v1 import BaseModel
from langchain_openai import ChatOpenAI, AzureChatOpenAI

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from nextgen.helpers.EnvHelper import EnvHelper
from nextgen.helpers.LLMHelper import NGllmhelper
from nextgen.helpers.SQLDatabase import SQLDatabaseHelper

from sql_research_assistant.utils.loadfile import UploadToDB, DocumentLoader, DatabaseUploader
from nextgen.helpers.SQLDatabase import SQLDatabaseHelper

# env_helper = EnvHelper()
llms = NGllmhelper()
llm = llms.get_openai_llm()

sql_db = SQLDatabaseHelper()
db = sql_db.db

def get_schema():
    return db.get_table_info()

def run_query(query):
    return db.run(query)

def create_table(table_name, schema):
    #logic to create table in sql
    return db.create_table(table_name, schema)

# Prompt
template = """Based on the table schema below, write a SQL query that would answer the user's question:
{schema}

Question: {question}
SQL Query:"""  # noqa: E501
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Given an input question, convert it to a SQL query. No pre-amble."),
        ("human", template),
    ]
)

memory = ConversationBufferMemory(return_messages=True)

# Chain to query with memory

sql_chain = (
    RunnablePassthrough.assign(
        schema=get_schema,
    )
    | prompt
    | llm.bind(stop=["\nSQLResult:"])
    | StrOutputParser()
    | (lambda x: x.split("\n\n")[0])
)


# Chain to answer
template = """Based on the table schema below, question, sql query, and sql response, write a natural language response:
{schema}

Question: {question}
SQL Query: {query}
SQL Response: {response}"""  # noqa: E501
prompt_response = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Given an input question and SQL response, convert it to a natural "
            "language answer. No pre-amble.",
        ),
        ("human", template),
    ]
)

# Supply the input types to the prompt
class InputType(BaseModel):
    question: str


sql_answer_chain = (
    RunnablePassthrough.assign(query=sql_chain).with_types(input_type=InputType)
    | RunnablePassthrough.assign(
        schema=get_schema,
        response=lambda x: db.run(x["query"]),
    )
    | RunnablePassthrough.assign(
        answer=prompt_response | AzureChatOpenAI() | StrOutputParser()
    )
    | (lambda x: f"Question: {x['question']}\n\nAnswer: {x['answer']}")
)
