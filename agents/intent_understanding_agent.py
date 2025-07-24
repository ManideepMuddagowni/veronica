# agents/intent_understanding_agent.py
import re
import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from asyncio import to_thread


class IntentUnderstandingAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
        self.chain = self._create_chain()

    def _create_chain(self):
        system_template = (
"""You are an intent classification agent that determines which downstream agent(s) should handle a product-related query.

Available agents:
- shopping_agent: Handles product information queries (pricing, availability, specifications, comparisons, model numbers) and SEO content generation (product descriptions, meta titles, tags, categorization).
- web_shopping_agent: Handles queries that require searching the web to retrieve missing or hard-to-find product data (rare products, unlisted SKUs, external reviews).

Classification Rules:
- If the query is about SEO generation (product description, technical description, meta title, categorization), respond with: {"agents": ["shopping_agent"]}
- If the query requires online product discovery or data not available internally, respond with: {"agents": ["web_shopping_agent"]}
- If both SEO generation and external product lookup are needed, respond with: {"agents": ["shopping_agent", "web_shopping_agent"]}

Important:
- ONLY return a JSON object in this format: {"agents": ["shopping_agent"]}
- Do NOT include any explanation, comments, markdown, or extra text.
- Use only the agent names listed above. No other agents are allowed.
"""
)


        system_msg = SystemMessagePromptTemplate.from_template(system_template)
        human_template = "Product query: {query}"
        human_msg = HumanMessagePromptTemplate.from_template(human_template)
        prompt = ChatPromptTemplate.from_messages([system_msg, human_msg])
        return LLMChain(llm=self.llm, prompt=prompt)

    async def run(self, user_query: str):
        asin_pattern = r'\b[A-Z0-9]{10}\b'
        ean_pattern = r'\b\d{13}\b'

        normalized_query = user_query.upper()

        if re.search(asin_pattern, normalized_query) or re.search(ean_pattern, user_query):
            return {"agents": ["web_shopping_agent"]}

        try:
            response = await to_thread(self.chain.run, query=user_query)
            result = json.loads(response.strip())
            if "agents" not in result or not isinstance(result["agents"], list):
                raise ValueError("Invalid JSON keys or types")
            return result
        except Exception as e:
            print(f"Intent Understanding LLM error or invalid response: {e}. Defaulting to shopping_agent.")
            return {"agents": ["shopping_agent"]}
