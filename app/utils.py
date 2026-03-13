from app.app_config import MAX_UPLOAD_SIZE_MB

# ---------------------------
# Utility functions
# ---------------------------

def validate_file_size(contents: bytes):
    max_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    size_mb = len(contents) / (1024 * 1024)

    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large: {size_mb:.2f} MB. Max size is {MAX_UPLOAD_SIZE_MB} MB"
        )