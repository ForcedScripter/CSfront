from tavily import TavilyClient
from config import TAVILY_API_KEY

client = TavilyClient(api_key=TAVILY_API_KEY)


def search_web(query: str):
    """
    Search internet using Tavily
    """
    response = client.search(query=query, search_depth="advanced", max_results=5)

    results = []

    for r in response["results"]:
        results.append(f"{r['title']}\n{r['content']}\nSource: {r['url']}")

    return results
