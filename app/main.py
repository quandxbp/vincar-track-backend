from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app import config
from app.core import auth
from app.routers import router as v1

from app.services.repository import get_mongo_meta
from app.utils import get_logger, init_mongo

app = FastAPI()

global_settings = config.get_settings()

if global_settings.environment == "local":
    get_logger("uvicorn")

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth")
app.include_router(v1, prefix="/api")


@app.on_event("startup")
async def startup_event():
    app.state.logger = get_logger(__name__)
    app.state.logger.info("STARTING INIT APPLICATION")
    app.state.mongo_client, app.state.mongo_db, app.state.mongo_collections = await init_mongo(
        global_settings.db_name, global_settings.db_url, global_settings.collections
    )


@app.on_event("shutdown")
async def shutdown_event():
    app.state.logger.info("SHUTDOWN APPLICATION")


@app.get("/health-check")
async def health_check():
    return await get_mongo_meta()