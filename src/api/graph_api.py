import requests
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import re
import time
from tqdm import tqdm

from src.utils.parser import process_results

RATE_LIMIT_DELAY = 1.3

graph_endpoint = "http://api.semanticscholar.org/graph/v1"
relevance_search_path = "/paper/search"
bulk_search_path = "/paper/search/bulk"
details_path = "/paper"
batch_path = "/paper/batch"

# Query Functions
def relevance_search(query: str, num_results: int = 10, fields: list = None, offset: int = None) -> dict:
    url = graph_endpoint + relevance_search_path
    params = {
        "query": query,
        "num_results": num_results
    }
    if fields is not None and len(fields) > 0:
        fields_str = ",".join(fields)
        params["fields"] = fields_str
    if offset is not None:
        params["offset"] = offset
    
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(response.url)
        print(response.json())
        raise ValueError(f"Failed to query the API. Status code: {response.status_code}")

    return response.json()

def bulk_search(query: str, num_results: int = 10, token: str = None) -> dict:
    url = graph_endpoint + bulk_search_path
    params = {
        "query": query,
        "num_results": num_results
    }
    if token is not None:
        params["token"] = token
    
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(response.url)
        print(response.json())
        raise ValueError(f"Failed to query the API. Status code: {response.status_code}")

    return response.json()

def fetch_relevance_serach(query: str, num_results: int = 10, fields: list = None) -> pd.DataFrame:
    has_next = True
    next = None
    df = pd.DataFrame()
    total_results = None

    # First query
    response = relevance_search(query, num_results, fields, next)
    next = response.get("next", None)
    has_next = next is not None
    total_results = response.get("total", 0)

    tmp_df = process_results(response, fields)
    df = pd.concat([df, tmp_df], ignore_index=True)

    # Initialize progress bar
    pbar = tqdm(total=total_results, desc="Fetching Results", unit="result")
    pbar.update(len(response.get("data", [])))

    while has_next:
        response = relevance_search(query, num_results, fields, next)
        next = response.get("next", None)
        has_next = next is not None

        tmp_df = process_results(response, fields)
        df = pd.concat([df, tmp_df], ignore_index=True)

        # Add progress bar
        pbar.update(len(response.get("data", [])))

        # Wait for 1 second to avoid rate limiting
        time.sleep(RATE_LIMIT_DELAY)     

    pbar.close()
    return df

def fetch_details(paper_ids: list, fields: list = None) -> dict:
    url = graph_endpoint + batch_path
    params = {}
    if fields is not None and len(fields) > 0:
        fields_str = ",".join(fields)
        params["fields"] = fields_str
    data = {
        "ids": paper_ids
    }

    response = requests.post(url, params=params, json=data)

    if response.status_code != 200:
        print(response.url)
        print(response.json())
        raise ValueError(f"Failed to query the API. Status code: {response.status_code}")
    
    return response.json()

def fetch_bulk_search(query: str, num_results: int = 10, fields: list = None, detailed: bool = False) -> pd.DataFrame:
    has_next = True
    token = None
    df = pd.DataFrame()

    while has_next:
        response = bulk_search(query, num_results, token)
        token = response.get("token", None)
        has_next = token is not None

        if detailed:
            paper_ids = []
            for paper in response.get("data", []):
                paper_ids.append(paper.get("paperId"))

            # Split the batch into chunks of 500
            chunk_size = 500
            for i in range(0, len(paper_ids), chunk_size):
                papers = fetch_details(paper_ids[i:i+chunk_size], fields)
                tmp_df = pd.DataFrame(papers)
                df = pd.concat([df, tmp_df], ignore_index=True)

                # Wait for 1 second to avoid rate limiting
                time.sleep(RATE_LIMIT_DELAY)
        else:
            tmp_df = process_results(response, fields)
            df = pd.concat([df, tmp_df], ignore_index=True)
        
        # Wait for 1 second to avoid rate limiting
        time.sleep(RATE_LIMIT_DELAY)     

    return df