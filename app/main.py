import io
import time
import pdfplumber

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.logging_config import setup_logging
from app.utils import validate_file_size
from app.app_config import APP_VERSION, MAX_UPLOAD_SIZE_MB

# ---------------------------
# Initialization
# ---------------------------

start_time = time.time()
app = FastAPI()
logger = setup_logging()

# ---------------------------
# Static files
# ---------------------------

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def index() -> FileResponse:
    """Serve main HTML page."""
    return FileResponse("app/static/index.html")

@app.get("/favicon.ico")
async def favicon() -> FileResponse:
    """Serve favicon."""
    return FileResponse("app/static/favicon.ico")


# ---------------------------
# Middleware logging
# ---------------------------

@app.middleware("http")
async def request_logger(request: Request, call_next):
    start = time.time()
    method = request.method
    path = request.url.path

    response = await call_next(request)

    duration = int((time.time() - start) * 1000)
    logger.info(f"{method} {path} status={response.status_code} time={duration}ms")

    return response


# ---------------------------
# Startup and shutdown events
# ---------------------------

@app.on_event("startup")
async def startup_event():
    logger.info(f"PDFToru started version={APP_VERSION}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"PDFToru shutting down version={APP_VERSION}")


# ---------------------------
# Health endpoint
# ---------------------------

@app.get("/health")
async def health() -> dict:
    """Return health, uptime, version and max upload size."""
    uptime_seconds = int(time.time() - start_time)

    return {
        "status": "ok",
        "version": APP_VERSION,
        "uptime_seconds": uptime_seconds,
        "max_upload_MB": MAX_UPLOAD_SIZE_MB,
    }


# ---------------------------
# Helper function for PDF processing
# ---------------------------

async def process_pdf(request: Request, file: UploadFile, processor):
    """
    Generic PDF processing function.

    - Reads and validates the file.
    - Applies the given processor function to pdfplumber PDF object.
    - Handles logging and errors.
    """
    try:
        contents = await file.read()
        validate_file_size(contents)

        logger.info(f"Uploaded '{file.filename}' endpoint={request.url.path}")

        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            result = processor(pdf)

        logger.info(f"Processed '{file.filename}' successfully")
        return result

    except Exception as e:
        logger.error(f"Error processing '{file.filename}': {e}")
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")


# ---------------------------
# PDF extraction endpoints
# ---------------------------

@app.post("/extract/text")
async def extract_text(request: Request, file: UploadFile = File(...)) -> dict:
    """Extract full text from PDF."""
    return await process_pdf(
        request, file,
        processor=lambda pdf: {"text": "\n".join(page.extract_text() or "" for page in pdf.pages)}
    )


@app.post("/extract/words")
async def extract_words(request: Request, file: UploadFile = File(...)) -> dict:
    """Extract all words from PDF."""
    return await process_pdf(
        request, file,
        processor=lambda pdf: {"words": [word for page in pdf.pages for word in page.extract_words()]}
    )


@app.post("/extract/tables")
async def extract_tables(request: Request, file: UploadFile = File(...)) -> dict:
    """Extract all tables from PDF."""
    return await process_pdf(
        request, file,
        processor=lambda pdf: {"tables": [table for page in pdf.pages for table in page.extract_tables()]}
    )


@app.post("/extract/layout")
async def extract_layout(request: Request, file: UploadFile = File(...)) -> dict:
    """Extract layout objects (rects, lines, chars, words) from PDF."""
    def layout_processor(pdf):
        return {
            "layout": [
                {
                    "rects": page.rects,
                    "lines": page.lines,
                    "chars": page.chars,
                    "words": page.extract_words()
                } for page in pdf.pages
            ]
        }

    return await process_pdf(request, file, layout_processor)