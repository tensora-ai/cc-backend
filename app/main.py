import os
from fastapi import FastAPI, Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from app.api.routes import router
from dotenv import load_dotenv

from app.resources import lifespan

load_dotenv()

api_key_header = APIKeyHeader(name="api-key", auto_error=True)


# ------------------------------------------------------------------------------
def validate_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.environ["API_KEY"]:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key


# ------------------------------------------------------------------------------
app = FastAPI(
    title="Heute AT - AI Article Utilities",
    version="0.1.0",
    dependencies=[Depends(validate_api_key)],
    lifespan=lifespan,
)


app = FastAPI(title="Tensora Count Backend", lifespan=lifespan)
app.include_router(router, prefix="/api")
