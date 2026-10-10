import time
import wikipedia
from .base import BaseTool
from app.state import ToolResult

class WikipediaTool(BaseTool):
    name = "wikipedia"
    description = "Searches Wikipedia and fetches summaries for given topics."

    def run(self, query: str) -> ToolResult:
        start_time = time.time()
        try:
            if not query or not query.strip():
                return self._create_error_result("ValidationError", "Query cannot be empty.", start_time)

            # Search for pages
            search_results = wikipedia.search(query, results=3)
            if not search_results:
                return self._create_error_result("NoResultsError", "No Wikipedia pages found.", start_time)
                
            results = []
            for title in search_results:
                try:
                    page = wikipedia.page(title, auto_suggest=False)
                    results.append({
                        "title": page.title,
                        "url": page.url,
                        "snippet": page.summary[:500] + "...",
                        "source": "wikipedia"
                    })
                except wikipedia.exceptions.DisambiguationError:
                    continue # Skip disambiguation pages
                except Exception:
                    continue
                    
            if not results:
                return self._create_error_result("FetchError", "Failed to fetch summaries for results.", start_time)

            return self._create_success_result(results, start_time)

        except Exception as e:
            return self._create_error_result("WikipediaError", str(e), start_time)
