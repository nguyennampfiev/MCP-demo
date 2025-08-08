## Usage

### Run the Tool

```sh
poetry run python tool_function.py
```

You will see:
```
Welcome to the arXiv paper search tool! Type 'quit' to exit.
Enter your query:
```
Type your queries (e.g., "Search for papers about quantum computing") or type `quit` to exit.


## Serving Local with vLLMs

This project supports running with local vLLMs (e.g., [vLLM](https://github.com/vllm-project/vllm)) for fast, efficient inference on your own hardware. For using with GPT-OSS-20B please refers to [GPT-OSS](https://docs.vllm.ai/projects/recipes/en/latest/OpenAI/GPT-OSS.html#installation)


### Start a Local vLLM Server

You can launch a vLLM OpenAI-compatible server with your chosen model, for example:

```vllm serve "your model"
```

Update the `init_agent()` function in `tool_function.py` to point to your local vLLM server (default is `http://localhost:8000/v1`).

**Now, when you run the tool, it will use your local vLLM for LLM-powered features.**

---

## Project Structure

- `tool_function.py` — Main logic for searching and extracting paper info, and the chat loop.
- `papers/` — Directory where paper metadata is saved as JSON.

## Notes

- The agent uses a local LLM endpoint by default (`Qwen/Qwen3-0.6B`/`GPT-OSS=20B`). You can change this in `init_agent()`.
- Paper metadata is saved in the `papers/` directory, organized by topic.
