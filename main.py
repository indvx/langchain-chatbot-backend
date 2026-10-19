from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
from routers import employees, whatsapp, telegram, document, chat_bot, address
from middleware.auth_middleware import AuthMiddleware
from services.document_ingestion_service import DocumentIngestionService
from utils.logger import logger
import os
from dotenv import load_dotenv

# Primary application entry point. Configures middleware, mounts static assets,
# registers API routes, and starts the background document ingestion worker.
load_dotenv()
ingestion_service = DocumentIngestionService()


app = FastAPI(
    title="chat-bot",
    version="1.0",
    description="A backend service for managing document, employees, and chat integrations."
)

# CORS setup: allow all origins in development so frontend clients (React/Vue/mobile) can connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Local document storage: documents are saved here on upload and later served directly at /files/<filename>
os.makedirs("documents", exist_ok=True)
app.mount("/files", StaticFiles(directory="documents"), name="files")

# Custom auth middleware to inspect Authorization header on incoming requests
app.add_middleware(AuthMiddleware)

# API route modules
app.include_router(whatsapp.router)
app.include_router(telegram.router)
app.include_router(employees.router)
app.include_router(document.router)
app.include_router(chat_bot.router)
app.include_router(address.router)

# Background scheduler runs asynchronous maintenance tasks independently of HTTP worker threads
scheduler = BackgroundScheduler()


@app.on_event("startup")
def start_scheduler():
    """
    On application boot, launch the background scheduler to periodically poll
    the 'documents' directory and ingest newly uploaded files into ChromaDB.
    """
    logger.info("Scheduler starting...")
    # Poll for new unprocessed documents every 10 seconds
    scheduler.add_job(
        ingestion_service.main_loop,
        'interval',
        id='main_loop_job',
        seconds=10
    )
    scheduler.start()
    logger.info("Scheduler started successfully.")


@app.on_event("shutdown")
def shutdown_scheduler():
    """Cleanly stop background worker threads when FastAPI shuts down."""
    scheduler.shutdown()
    logger.info("Scheduler stopped.")


@app.get("/")
async def root():
    """Simple liveness probe to verify FastAPI server is running."""
    logger.info("Root endpoint accessed.")
    return {"message": "FastAPI Running "}

