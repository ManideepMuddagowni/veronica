import asyncio
import json

class AgentWrapper:
    def __init__(self, name, agent_instance):
        self.name = name
        self.agent = agent_instance
        self.memory = []

    async def run(self, query: str, context=None):
        self.memory.append({"query": query, "context": context})
        if asyncio.iscoroutinefunction(self.agent.run):
            response = await self.agent.run(query)
        else:
            # Run sync functions in a thread to not block async loop
            response = await asyncio.to_thread(self.agent.run, query)
        self.memory.append({"response": response})
        return response


# master_route_agent.py (or wherever your MasterRouterAgent is defined)

class MasterRouterAgent:
    def __init__(self, intent_agent_wrapper, agents_dict):
        self.intent_agent = intent_agent_wrapper  # Should be an AgentWrapper instance
        self.agents_dict = agents_dict  # dict[str, AgentWrapper]

    async def run(self, user_input: str):
        intent_result_raw = await self.intent_agent.run(user_input)

        # Ensure intent_result is a dict (try to parse if string)
        if isinstance(intent_result_raw, str):
            try:
                intent_result = json.loads(intent_result_raw)
            except json.JSONDecodeError:
                return {"responses": [{"agent": "MasterRouterAgent", "content": "Intent agent response not parseable JSON."}]}
        elif isinstance(intent_result_raw, dict):
            intent_result = intent_result_raw
        else:
            return {"responses": [{"agent": "MasterRouterAgent", "content": "Unexpected intent agent response type."}]}

        agents_list = intent_result.get("agents", [])
        if not agents_list:
            return {"responses": [{"agent": "MasterRouterAgent", "content": "No valid agent found for the query."}]}

        selected_agent_key = agents_list[0]
        agent_wrapper = self.agents_dict.get(selected_agent_key)
        if agent_wrapper is None:
            return {"responses": [{"agent": "MasterRouterAgent", "content": f"Agent '{selected_agent_key}' not found."}]}

        response = await agent_wrapper.run(user_input)

        return {
            "responses": [
                {
                    "agent": agent_wrapper.name,
                    "content": response
                }
            ]
        }

