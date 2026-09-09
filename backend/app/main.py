import os,logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers.auth_router import router as auth_router
from app.routers.health_router import router as health_router
from app.routers.ingest_router import router as ingest_router
from app.config.settings import settings
from app.memory.redis_memory import RedisMemoryService
from app import logging_config

#logging_config.configure_uvicorn_logging() #remove comment to see logs in cmd line
logger = logging.getLogger(__name__)

memory_service  = RedisMemoryService(settings.redis_url, settings.redis_ttl_seconds)
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Connecting to Redis...")
    memory_service.connect()

    yield  # FastAPI runs here while app is alive

    logger.info("Disconnecting from Redis...")
    memory_service.disconnect()

app = FastAPI(
    title=settings.app_name,
    version="0.0.1",
    description="Starter multi-agent backend with auth,Redis memory,Elastic Search and router-based modular structure ",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(ingest_router)


logger.info(
    "Application startup configured",
    extra={
        "app_name":settings.app_name,
        "api_prefix":settings.api_prefix,
        "llm_provider":settings.llm_provider,
        "elastic_index":settings.elasticsearch_index
    }
)
