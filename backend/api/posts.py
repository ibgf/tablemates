from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from fastapi.responses import JSONResponse
from uuid import UUID
from backend.core.database import get_db
from backend.models.post import Post
from backend.models.social import PostLike, PostFavorite, UserFollow
from backend.schemas.post import PostCreate, PostOut
import uuid as uuid_lib
import json
from datetime import datetime
from backend.schemas.post import PostUpdate
from backend.core.dependencies import get_current_user
from fastapi import Depends

router = APIRouter(tags=["Posts"])


@router.post("/", response_model=PostOut)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    post_id = uuid_lib.uuid4()

    post_data = Post(
        id=post_id,
        title=post.title,
        content=post.content,
        post_type=post.post_type,
        image_urls=json.dumps(post.image_urls),
        user_id=post.user_id,
        location=post.location or "未知地址",
        max_participants=post.max_participants or 0,
        start_date=post.start_date,
        end_date=post.end_date,
        price=post.price or 0.0,
        city=post.city or "未知城市",
        country=post.country or "未知国家",
        is_active=post.is_active
    )

    db.add(post_data)
    db.commit()
    db.refresh(post_data)

    return post_data

@router.get("/{post_id}")
def get_post(
    post_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
# def get_post(post_id: str, request: Request, db: Session = Depends(get_db)):
    """获取单个帖子详情，并返回互动状态"""
    query = text("""
    SELECT 
        posts.id, posts.title, posts.content, posts.post_type, posts.created_at, 
        posts.image_urls, posts.likes, posts.comments_count, posts.user_id, posts.clicks,
        posts.location, posts.max_participants, posts.start_date, posts.end_date, 
        posts.price, posts.status, posts.city, posts.country, posts.is_active
    FROM posts
    WHERE posts.id = :post_id;
    """)

    result = db.execute(query, {"post_id": post_id}).fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Post not found")

    author_id = str(result[8])
    is_active = result[18]

    #user_id = request.headers.get("X-User-Id")
    user_id = current_user.get("user_id")  # ✅ 来自 JWT

    # 权限检查
    if user_id and str(user_id).strip() == str(author_id).strip():
        pass  # 作者本人，允许查看
    elif not is_active:
        raise HTTPException(status_code=403, detail="该帖子尚未发布，仅作者可查看")

    # 获取互动状态
    if not user_id:
        liked = False
        favorited = False
        followed = False
    else:
        liked = db.query(PostLike).filter_by(user_id=user_id, post_id=post_id).first() is not None
        favorited = db.query(PostFavorite).filter_by(user_id=user_id, post_id=post_id).first() is not None
        followed = db.query(UserFollow).filter_by(follower_id=user_id, followed_id=author_id).first() is not None

    like_count = db.query(PostLike).filter_by(post_id=post_id).count()
    favorite_count = db.query(PostFavorite).filter_by(post_id=post_id).count()
    follower_count = db.query(UserFollow).filter_by(followed_id=author_id).count()

    # 处理 image_urls 字段
    image_urls = result[5]
    if isinstance(image_urls, str):
        try:
            image_urls = json.loads(image_urls)
        except Exception:
            image_urls = []
    elif image_urls is None:
        image_urls = []

    return JSONResponse(
        content=json.loads(json.dumps({
            "id": str(result[0]),
            "title": result[1],
            "content": result[2],
            "post_type": result[3],
            "created_at": result[4],
            "image_urls": image_urls,
            "likes": result[6],
            "comments_count": result[7],
            "user_id": str(result[8]),
            "clicks": result[9],
            "location": result[10],
            "max_participants": result[11],
            "start_date": result[12],
            "end_date": result[13],
            "price": result[14],
            "status": result[15],
            "city": result[16],
            "country": result[17],
            "is_active": is_active,
            "liked_by_current_user": liked,
            "favorited_by_current_user": favorited,
            "followed_by_current_user": followed,
            "like_count": like_count,
            "favorite_count": favorite_count,
            "follower_count": follower_count,
        }, default=str)),
        media_type="application/json; charset=utf-8"
    )


@router.put("/{post_id}", response_model=PostOut)
def update_post(post_id: UUID, updated_post: PostUpdate, db: Session = Depends(get_db), request: Request = None):
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        raise HTTPException(status_code=401, detail="缺少 X-User-Id 请求头")

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if str(post.user_id) != user_id:
        raise HTTPException(status_code=403, detail="只有作者本人可以编辑")

    # 更新字段
    post.title = updated_post.title
    post.content = updated_post.content
    post.post_type = updated_post.post_type
    post.image_urls = json.dumps(updated_post.image_urls)
    post.location = updated_post.location
    post.max_participants = updated_post.max_participants
    post.start_date = updated_post.start_date
    post.end_date = updated_post.end_date
    post.price = updated_post.price
    post.city = updated_post.city
    post.country = updated_post.country
    post.is_active = updated_post.is_active

    db.commit()
    db.refresh(post)
    return post

@router.put("/{post_id}/activate")
def activate_post(post_id: UUID, request: Request, db: Session = Depends(get_db)):
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        raise HTTPException(status_code=401, detail="缺少 X-User-Id 请求头")

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if str(post.user_id) != user_id:
        raise HTTPException(status_code=403, detail="只有作者本人可以激活")

    post.is_active = True
    db.commit()
    return {"message": "已成功激活"}

@router.delete("/{post_id}")
def delete_post(post_id: UUID, request: Request, db: Session = Depends(get_db)):
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        raise HTTPException(status_code=401, detail="缺少 X-User-Id 请求头")

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    if str(post.user_id) != user_id:
        raise HTTPException(status_code=403, detail="只有作者本人可以删除帖子")

    if post.is_active:
        raise HTTPException(status_code=400, detail="帖子已激活，无法删除")

    db.delete(post)
    db.commit()
    return {"message": "帖子已删除"}
