import asyncio
from openai import AsyncOpenAI
from agents import Agent, Runner, function_tool, OpenAIResponsesModel, set_tracing_disabled
import arxiv
import json
import os
from typing import List, Dict, Union, Any
from dotenv import load_dotenv
PAPER_DIR = "papers"
from pydantic import BaseModel

set_tracing_disabled(True)

# Define expected input format
class SearchPapers(BaseModel):
    topic: str


class ExtractInfo(BaseModel):
    paper_id: str

@function_tool
def search_papers(topic: str) -> List[List]:
    """
    Search for papers on arXiv based on a given topic and store their information.
    
    Args:
        topic (str): The topic to search for.
        
    Returns:
        List[List]: A list of lists containing paper metadata.
    """
    print(f'Calling arXiv API to search for papers with topic: {topic}')

    client = arxiv.Client()

    search = arxiv.Search(
        query=topic,
        max_results=5,
        sort_by=arxiv.SortCriterion.Relevance
    )
    papers = client.results(search)

    # Create directory for this topic
    path = os.path.join(PAPER_DIR, topic.lower().replace(" ", "_"))
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, "papers_info.json")
    try:
        with open(file_path, 'r') as file:
            papers_info = json.load(file)
    except FileNotFoundError:
        papers_info = {}
    
    papers_id =[]
    for paper in papers:
        papers_id.append(paper.get_short_id())
        paper_info ={
            "title": paper.title,
            "authors": [author.name for author in paper.authors],
            "published": paper.published.isoformat(),
            "summary": paper.summary,
            "pdf_url": paper.pdf_url
        }
        papers_info[paper.get_short_id()] = paper_info
    with open(file_path, 'w') as file:
        json.dump(papers_info, file, indent=2)
    
    return papers_id

@function_tool
def extract_info(paper_id: str) -> str:
    """
    Extract information from a specific paper across all topic directories.
    
    Args:
        paper_id (str): The ID of the paper to extract information from.
        
    Returns:
        JSON string with paper information if found, otherwise an error message.
    """
    print(f'Calling extract_info function with paper id: {paper_id}')
    
    for item in os.listdir(PAPER_DIR):
        item_path = os.path.join(PAPER_DIR, item)
        if os.path.isdir(item_path):
            file_path = os.path.join(item_path, "papers_info.json")
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r") as file:
                        papers_info = json.load(file)
                        if paper_id in papers_info:
                            return json.dumps(papers_info[paper_id], indent=2)
                    
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    print(f"Error reading {file_path}: {e}")
                    continue
    return f"There is no saved information for paper ID: {paper_id}"

async def chat_loop(agent):
    """
    Start a chat loop to process user queries.
    """
    print("Welcome to the arXiv paper search tool! Type 'quit' to exit.")
    while True:
        try:
            query = input("Enter your query: ")
            if query.lower() == "quit":
                break
            await main(query, agent)
            print("\n")
        except Exception as e:
            print(f"An error occurred: {e}")


async def main(query: str, agent):
    """Process a single query using the agent."""
    result = await Runner.run(agent, query)  # Assuming this is the correct method
    print(result.final_output)


def init_agent():
    """
    Initialize the agent with the necessary tools and configurations.
    """
    agent = Agent(
        name="Assistant",
        model=OpenAIResponsesModel(
            model="openai/gpt-oss-20b",
            openai_client=AsyncOpenAI(
                base_url="http://localhost:8000/v1",
                api_key="not-needed",
            ),
        ),
        tools=[extract_info, search_papers],  # Make sure these functions are defined
    )
    return agent


def run_chat_loop(agent):
    """Run chat_loop in any environment safely."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No event loop running → safe to use asyncio.run
        asyncio.run(chat_loop(agent))
    else:
        # Already running loop (Jupyter/IPython) → use nest_asyncio
        nest_asyncio.apply()
        loop.run_until_complete(chat_loop(agent))


if __name__ == "__main__":
    agent = init_agent()
    run_chat_loop(agent)
