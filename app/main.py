from fastapi import FastAPI, UploadFile, File, HTTPException
import pdfplumber
import io
import os

app = FastAPI(title="PDFPlumber API", version="1.0")

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))

@app.get("/health")
def health():
    return {"status": "ok"}

def validate_size(data: bytes):
    if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")

@app.post("/extract/text")
async def extract_text(file: UploadFile = File(...)):
    data = await file.read()
    validate_size(data)
    text = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            text.append(page.extract_text() or "")
    return {"pages": len(text), "text": "\n".join(text)}

@app.post("/extract/words")
async def extract_words(file: UploadFile = File(...)):
    data = await file.read()
    validate_size(data)
    pages = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page_index, page in enumerate(pdf.pages):
            pages.append({
                "page": page_index + 1,
                "width": page.width,
                "height": page.height,
                "words": page.extract_words()
            })
    return {"pages": pages}

@app.post("/extract/tables")
async def extract_tables(file: UploadFile = File(...)):
    data = await file.read()
    validate_size(data)
    tables = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page_index, page in enumerate(pdf.pages):
            t = page.extract_tables()
            if t:
                tables.append({"page": page_index + 1, "tables": t})
    return {"tables": tables}

@app.post("/extract/layout")
async def extract_layout(file: UploadFile = File(...)):
    data = await file.read()
    validate_size(data)
    pages = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page_index, page in enumerate(pdf.pages):
            pages.append({
                "page": page_index + 1,
                "width": page.width,
                "height": page.height,
                "words": page.extract_words(),
                "lines": page.lines,
                "rects": page.rects
            })
    return {"pages": pages}