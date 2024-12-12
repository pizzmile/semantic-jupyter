import pandas as pd

# Process and Store Results
def process_results(data, fields: list = ['paperId', 'title']) -> pd.DataFrame:
    papers = []
    for paper in data.get("data", []):
        if fields is not None:
            paper = {key: paper.get(key) for key in fields}
            papers.append(paper)
        else:
            paper = {
                "paperId": paper.get("paperId"),
                "title": paper.get("title")
            }
            papers.append(paper)
    return pd.DataFrame(papers)
