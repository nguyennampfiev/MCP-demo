from typing import List
import asyncio
import nest_asyncio
import json
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIResponsesModel, set_tracing_disabled, SQLiteSession
from agents.mcp import MCPServerStdio
from aiohttp import ClientSession  # For type hints

nest_asyncio.apply()
set_tracing_disabled(True)

def init_agent(mcp_servers):
    """
    Initialize the agent with the necessary tools and configurations.
    """
    return Agent(
        name="Assistant",
        model=OpenAIResponsesModel(
            model="openai/gpt-oss-20b",
            openai_client=AsyncOpenAI(
                base_url="http://localhost:8000/v1",
                api_key="not-needed",
            ),
        ),
        mcp_servers=mcp_servers
    )

class MCP_ChatBot:
    def __init__(self, config_path: str):
        self.mcpserver: List[] = []
        self.session = SQLiteSession("conversation_123")
        self.config_path = config_path
        self._initialized = False

    async def _load_and_connect_servers(self):
        """Load MCP config from file and connect to all servers."""
        with open(self.config_path, "r") as f:
            mcp_config = json.load(f)

        for name, params in mcp_config.get("mcpServers", {}).items():
            server = MCPServerStdio(params=params, name=name)
            await server.connect()
            self.mcpserver.append(server)

        self._initialized = True
        print(f"Connected to {len(self.mcpserver)} MCP servers.")

    async def process_query(self, query: str) -> None:
        if not self._initialized or not self.mcpserver:
            print("MCP servers not initialized. Connecting now...")
            await self._load_and_connect_servers()

        agent = init_agent(self.mcpserver)
        result = await Runner.run(
            agent,
            query,
            session=self.session
        )
        print(result)

    async def chat_loop(self) -> None:
        if not self._initialized:
            await self._load_and_connect_servers()

        print("Welcome to the MCP Chatbot! Type 'quit' to exit.")
        while True:
            try:
                query = input("Enter your query: ")
                if query.lower() == "quit":
                    break
                await self.process_query(query)
            except Exception as e:
                print(f"An error occurred: {e}")

    #async def cleanup(self):
    #    """Disconnect MCP servers."""
    #    for server in self.mcpserver:
    #        await server.disconnect()
    #    print("All MCP servers disconnected.")

async def main():
    chatbot = MCP_ChatBot("server_config.json")
    #try:
    await chatbot.chat_loop()
    #finally:
    #    await chatbot.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
