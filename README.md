# MCP Integration

This is a ** sampleproject** demonstrating how to connect an OpenAI Agent or other LLMs (with tool-calling capability) to an [MCP server](https://github.com/modelcontextprotocol) through langchain or openai-agent framework for enhanced paper search and chat functionality.  
It includes:

- Creating and running an MCP server
- Connecting an LLM (local or remote) to the MCP server
- Running an interactive chatbot that can search arXiv papers and store results

---

## Usage

Below are usage examples for each file script.  

---

### `tool_function.py`
It use arxiv lib to search and extract info from query of user. 
There are two function calling search and extract information.
#### Run the test tool function

```sh
poetry run python tool_function.py
```

### `research_server.py`
An example of creating a local MCP server with stdio connection.

#### Run the test tool function

```sh
npx @modelcontextprotocol/inspector run research_server.py
```

## Serving Locally with vLLMs

You can run this project with a local [vLLM](https://github.com/vllm-project/vllm) for faster inference.  
For GPT-OSS-20B, see [GPT-OSS instructions](https://docs.vllm.ai/projects/recipes/en/latest/OpenAI/GPT-OSS.html#installation).

**Important:** The LLM you choose must have **tool-calling capability** to work with the MCP server.

---
### Start a Local vLLM Server
Open new terminal then run.

```sh
vllm serve openai/gpt-oss-20b
```

Then update `init_agent()` to point to your vLLM endpoint (default: `http://localhost:8000/v1`).

---
### `chatbot_mcp.py`
```sh
python chatbot_mcp.py
```
Initializes an agent and connects to the MCP server. Each agent maintains its own session.