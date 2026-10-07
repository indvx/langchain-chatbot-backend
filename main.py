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

load_dotenv()
ingestion_service = DocumentIngestionService()


app = FastAPI(
    title="chat-bot",
    version="1.0",
    description="A backend service for managing document, employees, and chat integrations."
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure local documents folder exists and mount static route
os.makedirs("documents", exist_ok=True)
app.mount("/files", StaticFiles(directory="documents"), name="files")

app.add_middleware(AuthMiddleware)

# Register endpoint routers
app.include_router(whatsapp.router)
app.include_router(telegram.router)
app.include_router(employees.router)
app.include_router(document.router)
app.include_router(chat_bot.router)
app.include_router(address.router)

scheduler = BackgroundScheduler()


@app.on_event("startup")
def start_scheduler():
    logger.info("Scheduler starting...")
    # Poll for new document uploads every 10s
    scheduler.add_job(ingestion_service.main_loop, 'interval',
                      id='main_loop_job', seconds=10)
    scheduler.start()
    logger.info("Scheduler started successfully.")


@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()
    logger.info("Scheduler stopped.")


@app.get("/")
async def root():
    logger.info("Root endpoint accessed.")
    return {"message": "FastAPI Running "}

