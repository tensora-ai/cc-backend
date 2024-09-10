from fastapi import FastAPI
from app.api.routes import router
from dotenv import load_dotenv

from app.resources import lifespan

load_dotenv()


app = FastAPI(title="Tensora Count Backend", lifespan=lifespan)
app.include_router(router, prefix="/api")
