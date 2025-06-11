from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from backend.core.database import get_db
from backend.models.social import PostLike, PostFavorite, UserFollow
from backend.models.post import Post
from backend.schemas.post import FeedPostOut
from backend.schemas.common import LikeStatus, FavoriteStatus, ToggleResponse

router = APIRouter(tags=["Social"])


@router.post("/posts/{post_id}/like", response_model=ToggleResponse)
def toggle_like(post_id: UUID, request: Request, db: Session = Depends(get_db)):
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        raise HTTPException(status_code=401, detail="请先登录")

    existing = db.query(PostLike).filter_by(user_id=user_id, post_id=post_id).first()
    if existing:
        db.delete(existing)
        db.commit()
        count = db.query(PostLike).filter_by(post_id=post_id).count()
        return ToggleResponse(status="success", action="unliked", count=count)
    else:
        db.add(PostLike(user_id=user_id, post_id=post_id, created_at=datetime.utcnow()))
        db.commit()
        count = db.query(PostLike).filter_by(post_id=post_id).count()
        return ToggleResponse(status="success", action="liked", count=count)


@router.post("/posts/{post_id}/favorite", response_model=ToggleResponse)
def toggle_favorite(post_id: UUID, request: Request, db: Session = Depends(get_db)):
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        raise HTTPException(status_code=401, detail="请先登录")

    favorite = db.query(PostFavorite).filter_by(user_id=user_id, post_id=post_id).first()
    if favorite:
        db.delete(favorite)
        db.commit()
        count = db.query(PostFavorite).filter_by(post_id=post_id).count()
        return ToggleResponse(status="success", action="unfavorited", count=count)
    else:
        db.add(PostFavorite(user_id=user_id, post_id=post_id, created_at=datetime.utcnow()))
        db.commit()
        count = db.query(PostFavorite).filter_by(post_id=post_id).count()
        return ToggleResponse(status="success", action="favorited", count=count)


@router.post("/users/{target_user_id}/follow")
def toggle_follow(target_user_id: UUID, request: Request, db: Session = Depends(get_db)):
    user_id = request.headers.get("X-User-Id")
    if not user_id or user_id == str(target_user_id):
        raise HTTPException(status_code=400, detail="无效用户")

    existing = db.query(UserFollow).filter_by(follower_id=user_id, followed_id=target_user_id).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"following": False, "message": "已取消关注"}
    else:
        db.add(UserFollow(follower_id=user_id, followed_id=target_user_id, created_at=datetime.utcnow()))
        db.commit()
        return {"following": True, "message": "已关注"}


@router.get("/posts/{post_id}/like-status", response_model=LikeStatus)
def get_like_status(post_id: UUID, request: Request, db: Session = Depends(get_db)):
    user_id = request.headers.get("X-User-Id")
    liked = False
    if user_id:
        liked = db.query(PostLike).filter_by(user_id=user_id, post_id=post_id).first() is not None
    return LikeStatus(liked=liked)


@router.get("/posts/{post_id}/favorite-status", response_model=FavoriteStatus)
def get_favorite_status(post_id: UUID, request: Request, db: Session = Depends(get_db)):
    user_id = request.headers.get("X-User-Id")
    favorited = False
    if user_id:
        favorited = db.query(PostFavorite).filter_by(user_id=user_id, post_id=post_id).first() is not None
    return FavoriteStatus(favorited=favorited)


@router.get("/user/feed", response_model=list[FeedPostOut])
def get_followed_feed(
    user_id: UUID,
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db)
):
    followed_ids = db.query(UserFollow.followed_id).filter(UserFollow.follower_id == str(user_id)).subquery()

    query = db.query(Post).filter(
        Post.user_id.in_(followed_ids),
        Post.post_type == "event",
        Post.is_active == True
    )

    posts = query.order_by(Post.created_at.desc()).offset((page - 1) * size).limit(size).all()
    return posts


@router.get("/user/favorites", response_model=list[FeedPostOut])
def get_favorite_events(
    user_id: UUID,
    type: str = Query("current", enum=["current", "past"]),
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db)
):
    favorite_post_ids = db.query(PostFavorite.post_id).filter(PostFavorite.user_id == str(user_id)).subquery()
    now = datetime.utcnow()

    query = db.query(Post).filter(
        Post.id.in_(favorite_post_ids),
        Post.post_type == "event",
        Post.is_active == True
    )

    if type == "current":
        query = query.filter(Post.end_date >= now)
    else:
        query = query.filter(Post.end_date < now)

    events = query.order_by(Post.start_date).offset((page - 1) * size).limit(size).all()
    return events
