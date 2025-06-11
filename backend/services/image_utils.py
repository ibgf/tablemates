import os
import uuid
from PIL import Image


def generate_thumbnail(original_path: str, base_dir: str, size=(400, 400)) -> str:
    """
    生成 WebP 缩略图（支持透明 PNG），返回缩略图路径
    - base_dir: 原图和 thumbs 文件夹的共同父目录（如 static/uploads）
    """
    thumb_dir = os.path.join(base_dir, "thumbs")
    os.makedirs(thumb_dir, exist_ok=True)

    base_name = os.path.basename(original_path)
    base_name_no_ext = os.path.splitext(base_name)[0]
    thumb_name = f"{base_name_no_ext}.webp"
    thumb_path = os.path.join(thumb_dir, thumb_name)

    with Image.open(original_path) as img:
        img.thumbnail(size)

        # 处理 RGBA/透明 PNG 转白底
        if img.mode in ("RGBA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
            background.save(thumb_path, "WEBP", quality=85)
        else:
            img.convert("RGB").save(thumb_path, "WEBP", quality=85)

    return thumb_path


def to_thumbnail_urls(image_urls: list[str]) -> list[str]:
    """
    将原图 URL 批量转换为缩略图 URL（统一转为 .webp 后缀）
    """
    return [
        url.replace("/static/uploads/", "/static/uploads/thumbs/").rsplit(".", 1)[0] + ".webp"
        for url in image_urls
    ]


def attach_thumbnail_urls(posts: list[dict]) -> list[dict]:
    """
    给帖子数据批量添加 thumbnail_urls 字段（基于 image_urls）
    - 用于 feed 流返回中展示缩略图列表
    """
    for post in posts:
        image_urls = post.get("image_urls", [])
        if isinstance(image_urls, str):
            import json
            image_urls = json.loads(image_urls)
        post["thumbnail_urls"] = to_thumbnail_urls(image_urls)
    return posts
