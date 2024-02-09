import os

from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits import create_sql_agent
from langchain.tools import BaseTool

from nextgen.helpers.EnvHelper import EnvHelper
from nextgen.helpers.LLMHelper import NGllmhelper
# env_helper = EnvHelper()
llms = NGllmhelper()

try:
    from .prompts import (COMBINE_QUESTION_PROMPT, COMBINE_PROMPT, COMBINE_CHAT_PROMPT,
                          CSV_PROMPT_PREFIX, CSV_PROMPT_SUFFIX, MSSQL_PROMPT, MSSQL_AGENT_PREFIX, 
                          MSSQL_AGENT_FORMAT_INSTRUCTIONS, CHATGPT_PROMPT, BING_PROMPT_PREFIX, DOCSEARCH_PROMPT_PREFIX, APISEARCH_PROMPT_PREFIX)
except Exception as e:
    print(e)

class AzSQLSearchAgent(BaseTool):
    """Agent to interact with SQL databases"""
    
    name = "@sqlsearch"
    description = "Useful when the questions include the term: @sqlsearch.\n"

    llm = llms.get_openai_llm()
    k: int = 30
    
    def _run(self, db, query: str) -> str:

        # Initialize SQLDatabaseToolkit with the new connection method
        toolkit = SQLDatabaseToolkit(db=db, llm=self.llm)
        agent_executor = create_sql_agent(
            prefix=MSSQL_AGENT_PREFIX,
            format_instructions=MSSQL_AGENT_FORMAT_INSTRUCTIONS,
            llm=self.llm,
            toolkit=toolkit,
            callback_manager=self.callbacks,
            top_k=self.k,
            verbose=self.verbose,
            handle_parsing_errors=True
        )

        for i in range(2):
            try:
                response = agent_executor.run(query)
                break
            except Exception as e:
                response = str(e)
                continue

        return response
    
    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("SQLDbTool does not support async")