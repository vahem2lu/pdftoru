from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.logging_config import logger
import pdfplumber
import shutil
import os
import time

from app.logging_config import logger

APP_VERSION = os.getenv("APP_VERSION", "unknown")
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", 50))
start_time = time.time()

app = FastAPI()

# Mount static folder
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Favicon route
@app.get("/favicon.ico")
async def favicon():
    return FileResponse("app/static/favicon.ico")

# Middleware to log all endpoint hits
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Endpoint {request.method} {request.url.path} called")
    response = await call_next(request)
    logger.info(f"Endpoint {request.method} {request.url.path} completed with status {response.status_code}")
    return response

# Health check
@app.get("/health")
async def health():
    uptime_seconds = int(time.time() - start_time)
    total, used, free = shutil.disk_usage("/")

    health_info = {
        "status": "ok",
        "version": APP_VERSION,
        "uptime_seconds": uptime_seconds,
        "max_upload_MB": MAX_UPLOAD_SIZE_MB,
        "free_disk_MB": free // (1024*1024)
    }

    logger.info(f"Health check called: {health_info}")
    return health_info

# Extract full text
@app.post("/extract/text")
async def extract_text(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        size_kb = len(contents) / 1024
        await file.seek(0)
        logger.info(f"Received file '{file.filename}' ({size_kb:.2f} KB) at /extract/text")

        with pdfplumber.open(file.file) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)

        logger.info(f"Processed file '{file.filename}' successfully")
        return {"text": text}

    except Exception as e:
        logger.error(f"Error processing file '{file.filename}': {e}")
        raise HTTPException(status_code=500, detail="PDF processing failed")

# Extract words with coordinates
@app.post("/extract/words")
async def extract_words(file: UploadFile = File(...)):
    try:
        logger.info(f"Received file '{file.filename}' at /extract/words")
        with pdfplumber.open(file.file) as pdf:
            words = []
            for page in pdf.pages:
                words.extend(page.extract_words())
        logger.info(f"Processed file '{file.filename}' successfully")
        return {"words": words}
    except Exception as e:
        logger.error(f"Error processing file '{file.filename}': {e}")
        raise HTTPException(status_code=500, detail="PDF processing failed")

# Extract tables
@app.post("/extract/tables")
async def extract_tables(file: UploadFile = File(...)):
    try:
        logger.info(f"Received file '{file.filename}' at /extract/tables")
        with pdfplumber.open(file.file) as pdf:
            tables = [page.extract_tables() for page in pdf.pages]
        logger.info(f"Processed file '{file.filename}' successfully")
        return {"tables": tables}
    except Exception as e:
        logger.error(f"Error processing file '{file.filename}': {e}")
        raise HTTPException(status_code=500, detail="PDF processing failed")

# Extract layout objects
@app.post("/extract/layout")
async def extract_layout(file: UploadFile = File(...)):
    try:
        logger.info(f"Received file '{file.filename}' at /extract/layout")
        layout_objects = []
        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages:
                layout_objects.append({
                    "rects": page.rects,
                    "lines": page.lines,
                    "chars": page.chars,
                    "words": page.extract_words()
                })
        logger.info(f"Processed file '{file.filename}' successfully")
        return {"layout": layout_objects}
    except Exception as e:
        logger.error(f"Error processing file '{file.filename}': {e}")
        raise HTTPException(status_code=500, detail="PDF processing failed")