import os
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents.output_parsers.tools import ToolsAgentOutputParser
# from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.format_scratchpad.tools import format_to_tool_messages
from langchain_core.output_parsers import PydanticOutputParser

from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.tools import StructuredTool
from langchain_community.utilities import GoogleSerperAPIWrapper

from langchain_community.callbacks import StreamlitCallbackHandler

from mini.agent.helper import GoogleSearchSchema, ArxivSchema
# from mini.tools.multimodal import Multimodal
from mini.tools.arxiv import Arxiv

class Agent(object):
    def __init__(self, gemini_api_key, serper_api_key):
        os.environ["GEMINI_API_KEY"] = gemini_api_key
        os.environ["SERPER_API_KEY"] = serper_api_key
        self.model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=gemini_api_key)
        self.memory = SQLChatMessageHistory(session_id="default", connection_string="sqlite:///memory.db")
        self.bindtools = self.initialize_tools()
        self.agent = self.build_agent()
        self.arxiv = Arxiv()

    def arxiv_search(self, query):
        try:
            return self.arxiv.search(query)
        except Exception as e:
            return "Terjadi error pada arxiv: " + str(e)

    def google_search(self, query, type):
        try:
            search = GoogleSerperAPIWrapper(type=type)
            response = search.results(query)

            field = "organic" if type == "search" else type

            context = ""
            for r in response[field]:
                context+= f"Title: {r['title']}\n"
                context+= f"Link: {r['link']}\n"
                context+= f"Snippet: {r['snippet']}\n\n"

            return context
        except Exception as e:
            return "Terjadi error pada Google Search: " + str(e)
        
    def initialize_tools(self):
        bindtools = [
            StructuredTool.from_function(
                name="online_search",
                description="Useful for when you need to answer questions based on online search like news, webpage, etc",
                func=self.google_search,
                args_schema=GoogleSearchSchema,
            ),
            StructuredTool.from_function(
                name="paper_search",
                description="Useful for when you need to search for papers",
                func=self.arxiv_search,
                args_schema=ArxivSchema,
            )
        ]
        return bindtools

    def build_agent(self):
        llm_with_tools = self.model.bind_tools(self.bindtools)
        agent_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a helpful assistant that answers questions. Please follow these rules:
                    1. If you don't know the answer, just say that you don't know, don't try to make up an answer.
                    2. Always use tools to answer the question. for example, if the question is about news, you should use online_search tool. Or if the question is about image, you should use image_ask tool.
                    3. Always include the source of the information in the answer. 
                    """,
                ),
                MessagesPlaceholder(variable_name="history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        pipeline = {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_tool_messages(
                x["intermediate_steps"]
            ),
            "history": lambda x: self.memory.messages[-6:],
        }

        agent = (
            pipeline
            | agent_prompt
            | llm_with_tools
            | ToolsAgentOutputParser()
        )

        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.bindtools,
            verbose=True,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
            max_iterations=6,
        )
        return agent_executor

    def ask(self, question, session_id):
        self.memory.session_id = session_id
        inputs = {"input": question}

        answer = self.agent.invoke(
            inputs,
            {"callbacks": [StreamlitCallbackHandler(st.container(), expand_new_thoughts=True)]}
        )["output"]

        self.memory.add_user_message(question)
        self.memory.add_ai_message(answer)
        return answer