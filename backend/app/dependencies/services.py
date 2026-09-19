from app.config.settings import settings
from app.memory.redis_memory import RedisMemoryService
from app.services.auth_service import AuthService
from app.services.token_service import TokenService

memory_service = RedisMemoryService(settings.redis_url, settings.redis_ttl_seconds)
auth_service = AuthService(memory_service)
token_service = TokenService()