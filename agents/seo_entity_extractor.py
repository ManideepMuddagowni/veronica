import re
import json
from asyncio import to_thread
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain



# -------- SEOEntityExtractor --------

class SEOEntityExtractor:
    def __init__(self):
        self.llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
        system_template = (
            "You are an assistant that extracts product_name and product_description from user input.\n"
            "Return STRICT JSON ONLY with keys 'product_name' and 'product_description'.\n"
            "No commentary or extra text."
        )
        human_template = "Text: {text}"
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
        self.chain = LLMChain(llm=self.llm, prompt=prompt)

    async def run(self, text: str) -> dict:
        raw = await to_thread(self.chain.run, text=text)
        try:
            return json.loads(raw)
        except Exception as e:
            print(f"SEOEntityExtractor JSON parse error: {e}\nRaw: {raw}")
            # fallback naive split
            return {
                "product_name": text[:30].strip(),
                "product_description": text.strip()
            }



# -------- Example usage --------
# import asyncio

# async def main():
#     router = MultiAgentRouter()
#     user_input = "Whirlpool 192 L 3 Star Vitamagic PRO Frost Free Direct-Cool Single Door Refrigerator with advanced cooling technology."
#     response = await router.route(user_input)
#     print(response)

# asyncio.run(main())
