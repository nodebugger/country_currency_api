from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routes import router as main_router
from .database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown

app = FastAPI(title="Currency & Exchange API", lifespan=lifespan)

# Include routers
app.include_router(main_router)

@app.get("/")
def root():
    return {"message": "Welcome to the Currency & Exchange API!"}
