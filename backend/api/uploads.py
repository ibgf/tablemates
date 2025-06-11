import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from backend.services.image_utils import generate_thumbnail

router = APIRouter(tags=["Uploads"])

UPLOAD_DIR = "static/uploads"

@router.post("/")
async def upload_images(files: List[UploadFile] = File(...)):
    upload_dir = UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)

    saved_file_urls = []
    thumbnail_urls = []

    for file in files:
        ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(upload_dir, unique_filename)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        saved_file_urls.append(f"/static/uploads/{unique_filename}")

        try:
            thumb_path = generate_thumbnail(file_path, upload_dir)
            thumb_name = os.path.basename(thumb_path)
            thumbnail_urls.append(f"/static/uploads/thumbs/{thumb_name}")
        except Exception as e:
            print(f"❌ 生成缩略图失败: {e}")
            thumbnail_urls.append("")

    return {
        "image_urls": saved_file_urls,
        "thumbnail_urls": thumbnail_urls
    }
