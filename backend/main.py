import uvicorn
from fastapi import FastAPI
from api import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from service import initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Event handler for application startup and shutdown.
    """
    print("Application is starting up...")
    initialize_database()
    print("Database initialized.")
    
    yield 
    print("Application is shutting down...")

app = FastAPI(
    title="Document Q&A Backend (e5-base-v2)",
    description="API for uploading documents and querying them using Qdrant and e5-base-v2.",
    version="1.0.0",
    lifespan=lifespan
)

origins = [
    "*"                     # allow all (only for testing!)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],         # allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],         # allow all headers
)

app.include_router(api_router)

@app.get("/")
def read_root():
    """A simple root endpoint to check if the app is running."""
    return {"message": "Welcome to the Document Q&A API"}
