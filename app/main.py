from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app import config
from app.core import auth
from app.routes import views
# from app.services.repository import get_mongo_meta
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

app.include_router(auth.router)
app.include_router(views.router)

@app.on_event("startup")
async def startup_event():
    app.state.logger = get_logger(__name__)
    app.state.logger.info("STARTING INIT APPLICATION")
    app.state.mongo_client, app.state.mongo_db, app.state.mongo_collection = await init_mongo(
        global_settings.db_name, global_settings.db_url, global_settings.collection
    )


# @app.on_event("shutdown")
# async def shutdown_event():
#     app.state.logger.info("Parking tractors in garage...")


# @app.get("/health-check")
# async def health_check():
#     # # TODO: check settings dependencies passing as args and kwargs
#     # a = 5
#     # try:
#     #     assert 5 / 0
#     # except Exception:
#     #     app.state.logger.exception("My way or highway...")
#     return await get_mongo_meta()