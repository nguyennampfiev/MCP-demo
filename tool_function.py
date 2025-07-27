import arxiv
import json
import os
from typing import List, Dict, Union, Any
from dotenv import load_dotenv
from langchain.agents import initialize_agent, Tool, AgentType
api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")
from langchain_community.chat_models import ChatOpenAI
from langchain.tools import StructuredTool
PAPER_DIR = "papers"

from pydantic import BaseModel

# Define expected input format
class SearchPapers(BaseModel):
    topic: str


class ExtractInfo(BaseModel):
    paper_id: str


def search_papers(topic: str) -> List[List]:
    """
    Search for papers on arXiv based on a given topic and store their information.
    
    Args:
        topic (str): The topic to search for.
        
    Returns:
        List[List]: A list of lists containing paper metadata.
    """
    print('Calling arXiv API to search for papers...')
    topic = json.loads(topic)
    print(topic)
    if isinstance(topic, List):
        topic = topic[0]
    elif isinstance(topic, Dict):
        topic = topic.get("topic", "")
    else:
        # If topic is not a list or dict, assume skipping
        print("Invalid topic format. Expected a list or dict.")
        return []
    print('----')
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

def extract_info(paper_id: str) -> str:
    """
    Extract information from a specific paper across all topic directories.
    
    Args:
        paper_id (str): The ID of the paper to extract information from.
        
    Returns:
        JSON string with paper information if found, otherwise an error message.
    """
    print('Calling extract_info function...')
    paper_id = json.loads(paper_id)
    if isinstance(paper_id, List):
        paper_id = paper_id[0]
    elif isinstance(paper_id, Dict):
        paper_id = paper_id.get("paper_id", "")
    else:
        # If topic is not a list or dict, assume skipping
        print("Invalid paper_id format. Expected a list or dict.")
    print('----')   
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


def init_agent():
    """Initialize the agent with the necessary tools and LLM.
    Returns:
        agent: An initialized agent with tools for searching and extracting paper information.
    """
    llm = ChatOpenAI(
        openai_api_key="EMPTY",
        openai_api_base="http://localhost:8000/v1",
        model_name="Qwen/Qwen3-0.6B",
        temperature=0.7,
    )
    # Define the tools
    tools = [
        StructuredTool.from_function(
            name="search_papers",
            func=search_papers,
            description="Search for papers on arXiv based on a given topic and return their metadata",
            args_schema=SearchPapers
        ),
        StructuredTool.from_function(
            name="extract_info",
            func=extract_info,
            description="Extract information from a specific paper using its ID",
            args_schema=ExtractInfo
        )
    ]   

    # Initialize the agent with tools
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent_type= AgentType.OPENAI_FUNCTIONS,
        verbose=True,
    )
    return agent

def process_query(agent: Any, query: str) -> str:
    """
    Process a query and execute the appropriate tool function.
    
    Args:
        query (str): The query to process.
        
    Returns:
        str: The result of the tool function execution.
    """
    # Initialize the HuggingFace model
    process_query =True
    while process_query:
        assistant_content = []
        response = agent.invoke({"input": query})
        output = response['output']
        print(f"Response: {output}")
        if isinstance(output, str):
            process_query = False

def chat_loop(agent):
    """
    Start a chat loop to process user queries.
    """
    print("Welcome to the arXiv paper search tool! Type 'quit' to exit.")
    while True:
        try:
            query = input("Enter your query: ")
            if query.lower() == "quit":
                break
            process_query(agent, query)
            print("\n")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    load_dotenv()
    agent = init_agent()
    chat_loop(agent)