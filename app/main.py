from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
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

# Define your secret token
SECRET_TOKEN = ""

RESTRICT_PATHS = ['']
RESTRICT_METHODS = ['DELETE']

# Define the middleware function
async def check_secret_token(request, call_next):
    # Get the value of the "Authorization" header
    token = request.headers.get("Authorization")

    # Check if the token matches the secret token and the request method is DELETE
    if request.method in RESTRICT_METHODS and token != SECRET_TOKEN:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": "Invalid Token"})

    # Call the next middleware or the route handler
    response = await call_next(request)
    return response

# Add the middleware to the app
app.middleware("http")(check_secret_token)

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