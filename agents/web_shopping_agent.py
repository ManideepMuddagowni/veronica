from langchain_community.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from tools.web_shopping_tool import search_product_combined
from conversation_history.memory import get_memory

def create_agent():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    memory = get_memory()
    tools = [search_product_combined]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
    )
    return agent
