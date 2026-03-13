# PDFToru
Uses pdfplumber python module to parse PDFs.

Creates API to parse PDFs and response is given back.

# Configure

You can change port in your docker settings.

`MAX_UPLOAD_MB` can be changed via ENV values. Default is `50`. Unit is `MB`.

# API endpoints

Uses API in port 8000.

Health check: /health

Endpoints:
- /extract/text
- /extract/words
- /extract/tables
- /extract/layout