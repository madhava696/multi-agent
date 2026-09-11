import logging

from app.config.settings import settings
from app.models.chat_models import AgentResult
from app.services.llm_service import LLMService
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