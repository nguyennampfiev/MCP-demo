import arxiv
import json
import os
from typing import List, Dict, Union, Any
from mcp.server.fastmcp import FastMCP 

mcp = FastMCP()
PAPER_DIR = "papers"

@mcp.tool()
def search_papers(topic: str) -> List:
    """
    Search for papers on arXiv based on a given topic and store their information.
    
    Args:
        topic (str): The topic to search for.
        
    Returns:
        List[List]: A list of lists containing paper metadata.
    """
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

@mcp.tool()
def extract_info(paper_id: str) -> str:
    """
    Extract information from a specific paper across all topic directories.
    
    Args:
        paper_id (str): The ID of the paper to extract information from.
        
    Returns:
        JSON string with paper information if found, otherwise an error message.
    """
    print('Calling extract_info function...') 
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

if __name__ == "__main__":
    mcp.run(transport='stdio')