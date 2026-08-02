"""
Receipt Image Storage
Allows uploading a receipt photo and attaching it to a transaction.
Serves stored images as static files.
"""
import os
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from app.models import User
from app.services.auth import get_current_user

router = APIRouter(prefix="/receipts", tags=["receipts"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "receipts")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


@router.post("/store")
async def store_receipt_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload and persist a receipt image. Returns the URL path."""
    ext = os.path.splitext(file.filename or "receipt.jpg")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only image files are allowed (jpg, png, webp).")

    filename = f"{current_user.id}_{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    contents = await file.read()
    with open(filepath, "wb") as f:
        f.write(contents)

    return {"url": f"/receipts/image/{filename}", "filename": filename}


@router.get("/image/{filename}")
async def get_receipt_image(filename: str):
    """Serve a stored receipt image by filename."""
    # Sanitize to prevent path traversal
    safe_name = os.path.basename(filename)
    filepath = os.path.join(UPLOAD_DIR, safe_name)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Receipt image not found.")
    return FileResponse(filepath)
