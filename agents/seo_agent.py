import json
import asyncio
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from agents.seo_entity_extractor import SEOEntityExtractor  # Adjust import as needed
from concurrent.futures import ThreadPoolExecutor

# Utility to run blocking code asynchronously in a thread
executor = ThreadPoolExecutor()

async def to_thread(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, lambda: func(*args, **kwargs))


class SEOAgent:
    def __init__(self):
        llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7)
        system_template = (
            "You are an expert SEO content generator. "
            "You will be given a product name and product description.\n\n"
            "Your task is to generate STRICTLY and ONLY the following in raw JSON:\n\n"
            '{\n'
            '  "meta_description": "SEO meta description under 160 characters",\n'
            '  "seo_keywords": "comma-separated keywords",\n'
            '  "seo_description": "An SEO-enhanced product description (~100 words)"\n'
            '}\n\n'
            "⚠️ DO NOT include commentary, markdown, or explanations. Only return valid JSON. "
            "Start directly with `{` and end with `}`."
        )
        system_msg = SystemMessagePromptTemplate.from_template(system_template)
        human_template = "Product Name: {product_name}\nProduct Description: {product_description}"
        human_msg = HumanMessagePromptTemplate.from_template(human_template)
        prompt = ChatPromptTemplate.from_messages([system_msg, human_msg])

        self.chain = LLMChain(llm=llm, prompt=prompt)

    async def run(self, input_data):
        """
        input_data can be:
         - dict with keys: product_name, product_description (for bulk upload)
         - string (for normal chat queries)
        """
        if isinstance(input_data, dict):
            product_name = input_data.get("product_name", "")
            product_description = input_data.get("product_description", "")
        else:
            extractor = SEOEntityExtractor()
            extracted = await extractor.run(input_data)
            product_name = extracted.get("product_name", "")
            product_description = extracted.get("product_description", "")

        # Run chain in thread to avoid blocking event loop
        raw = await to_thread(self.chain.run, product_name=product_name, product_description=product_description)

        try:
            return json.loads(raw)
        except Exception as e:
            print(f"[SEOAgent] JSON parse error: {e}\nRaw Output: {raw}")
            return {"error": "SEO generation failed", "raw_output": raw}
def create_seo_agent():
    return SEOAgent()