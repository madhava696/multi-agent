import logging

from app.config.settings import settings
from app.models.chat_models import AgentResult
from app.services.search_service import SearchService
from app.state.graph_state import GraphState

if settings.langfuse_enabled:
    try:
        from langfuse import observe
    except ImportError:
        #if langfuse failed to import a dummy observe function is used
        def observe(*args,**kwargs):
            def decorator(func):
                return func
            return decorator if args and callable(args[0]) else decorator
else:
    def observe(*args,**kwargs):
        def decorator(func):
            return func
        return decorator if args and callable(args[0]) else decorator

logger  = logging.getLogger(__name__)

class SearchAgent:
    def __init__(self,search_service:SearchService):

        self.search_service = search_service

        @observe(name="search_agent")
        async def run(self,state:GraphState)->AgentResult:
            logger.info(
                "Search agent started",
                extra={"route":state.route,"message_previe":state.user_message[:120]},
            )

            results = await self.search_service.search(state.user_message)
            state.search_result = results

            lines = [
                f"{index+1},{item.title} (score={item.score:.2f})-{item.snippet}"
                for index,item in enumerate(results)
            ]

            output = "Search results for ElasticSearch:\n"+"\n".join(lines)

            state.search_output=output
            logger.info(
                "search agent completed",
                extra = {"results_count":len(results),"index_name":self.search_sevice.index_name},
            )

            return AgentResult(
                agent="search",
                output=output,
                metadata={
                    "results_count":len(results),
                    "index_name":self.search_sevice.index_name
                }
            )
"""
                 USER
                  │
                  │ "What is LangChain?"
                  ▼
             GraphState
                  │
                  │ user_message
                  ▼
           ┌──────────────┐
           │ SearchAgent  │
           └──────┬───────┘
                  │
                  │ state.user_message
                  ▼
          SearchService.search()
                  │
                  ▼
            Elasticsearch
                  │
                  │ matching documents
                  ▼
            SearchResults
                  │
                  ▼
       state.search_results
                  │
                  ▼
        Format result strings
                  │
                  ▼
       state.search_output
                  │
                  ▼
            AgentResult
                  │
                  ▼
          Next graph node
"""