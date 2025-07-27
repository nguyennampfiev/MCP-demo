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


## Running with Local vLLMs

This project supports running with local vLLMs (e.g., [vLLM](https://github.com/vllm-project/vllm)) for fast, efficient inference on your own hardware.

### Install vLLM

Follow the [official vLLM installation guide](https://github.com/vllm-project/vllm#installation), or install via pip:

```sh
pip install vllm
```

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

- The agent uses a local LLM endpoint by default (`Qwen/Qwen3-0.6B`). You can change this in `init_agent()`.
- Paper metadata is saved in the `papers/` directory, organized by topic.
