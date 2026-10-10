import time
from duckduckgo_search import DDGS
from .base import BaseTool
from app.state import ToolResult
from app.utils.llm import call_llm

class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Searches the web for information based on a query using DuckDuckGo."

    def run(self, query: str, max_results: int = 5) -> ToolResult:
        start_time = time.time()
        try:
            if not query or not query.strip():
                return self._create_error_result("ValidationError", "Query cannot be empty.", start_time)

            results = []
            
            with DDGS() as ddgs:
                ddg_results = list(ddgs.text(query, max_results=max_results))
                for res in ddg_results:
                    results.append({
                        "title": res.get("title", ""),
                        "url": res.get("href", ""),
                        "snippet": res.get("body", ""),
                        "source": "duckduckgo"
                    })

            if not results:
                return self._create_error_result("NoResultsError", "No search results found.", start_time)

            return self._create_success_result(results, start_time)

        except Exception as e:
            return self._create_error_result("SearchError", str(e), start_time)
