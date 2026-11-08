from tavily import TavilyClient

class TavilyService:
    def __init__(self):
        self.client = TavilyClient()

    def search(self, query):
        return self.client.search(query=query, max_results=5)