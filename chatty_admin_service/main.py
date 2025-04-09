from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, Post, Comment
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from prometheus_fastapi_instrumentator import Instrumentator

sentry_sdk.init(
    dsn="https://example@sentry.io/123",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0
)

app = FastAPI(title="Chatty Admin Service")
Instrumentator().instrument(app).expose(app)


@app.post("/users/{user_id}/block")
async def block_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        sentry_sdk.capture_message(f"Attempt to block non-existent user {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    db_user.is_active = False
    db.commit()
    sentry_sdk.capture_message(f"User {user_id} blocked by admin")
    return {"message": f"User {user_id} blocked"}


@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        sentry_sdk.capture_message(f"Attempt to delete non-existent post {post_id}")
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()
    sentry_sdk.capture_message(f"Post {post_id} deleted by admin")
    return {"message": f"Post {post_id} deleted"}


@app.delete("/comments/{comment_id}")
async def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not db_comment:
        sentry_sdk.capture_message(f"Attempt to delete non-existent comment {comment_id}")
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(db_comment)
    db.commit()
    sentry_sdk.capture_message(f"Comment {comment_id} deleted by admin")
    return {"message": f"Comment {comment_id} deleted"}


@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_posts = db.query(Post).count()
    total_comments = db.query(Comment).count()
    stats = {
        "total_users": total_users,
        "active_users": active_users,
        "total_posts": total_posts,
        "total_comments": total_comments
    }
    sentry_sdk.capture_message("Admin requested activity stats")
    return {"message": "Activity stats", "stats": stats}