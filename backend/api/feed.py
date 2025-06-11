#  ✅ 文件路径：api/feed.py

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from uuid import UUID
import json
from backend.core.database import get_db
from backend.models.post import Post
from backend.services.image_utils import to_thumbnail_urls
from fastapi.encoders import jsonable_encoder

router = APIRouter(tags=["Feed"])

@router.get("/feed")
def get_feed(db: Session = Depends(get_db)):
    try:
        posts_query = (
            db.query(Post)
            .order_by(Post.created_at.desc())
            .limit(60)
            .all()
        )

        result = []
        for post in posts_query:
            try:
                image_urls = json.loads(post.image_urls) if isinstance(post.image_urls, str) else (post.image_urls or [])
            except Exception:
                image_urls = []

            thumbnail_urls = to_thumbnail_urls(image_urls)

            result.append({
                "id": str(post.id),
                "title": post.title,
                "user_id": str(post.user_id), 
                "image_urls": thumbnail_urls,
                "start_date": post.start_date.isoformat() if post.start_date else None,
                "end_date": post.end_date.isoformat() if post.end_date else None,
                "city": post.city or "未知城市",
                "country": post.country or "未知国家",
                "clicks": post.clicks or 0
            })

        return JSONResponse(content=jsonable_encoder({"feed": result}), media_type="application/json; charset=utf-8")

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, media_type="application/json; charset=utf-8")


@router.get("/feed/followed/{user_id}")
def get_followed_posts(user_id: UUID, db: Session = Depends(get_db)):
    followed_ids = db.execute(
        text("SELECT followed_id FROM user_follows WHERE follower_id = :user_id"),
        {"user_id": str(user_id)}
    ).fetchall()

    ids = [str(row[0]) for row in followed_ids]
    if not ids:
        return {"feed": []}

    result = db.execute(
        text("SELECT * FROM posts WHERE user_id = ANY(:ids) ORDER BY created_at DESC"),
        {"ids": ids}
    )

    posts = []
    for row in result.fetchall():
        post = dict(row._mapping)
        post["id"] = str(post["id"])
        post["user_id"] = str(post["user_id"])
        posts.append(post)

    return JSONResponse(content=jsonable_encoder({"feed": posts}), media_type="application/json; charset=utf-8")


@router.get("/feed/favorites/{user_id}")
def get_favorited_posts(user_id: UUID, db: Session = Depends(get_db)):
    favorite_post_ids = db.execute(
        text("SELECT post_id FROM post_favorites WHERE user_id = :user_id"),
        {"user_id": str(user_id)}
    ).fetchall()

    favorited_ids = [UUID(str(row[0])) for row in favorite_post_ids]
    if not favorited_ids:
        return {"feed": []}

    result = db.execute(
        text("SELECT * FROM posts WHERE id = ANY(:ids) ORDER BY created_at DESC"),
        {"ids": favorited_ids}
    )

    posts = []
    for row in result.fetchall():
        post = dict(row._mapping)
        post["id"] = str(post["id"])
        post["user_id"] = str(post["user_id"])
        posts.append(post)

    return JSONResponse(content=jsonable_encoder({"feed": posts}), media_type="application/json; charset=utf-8")
