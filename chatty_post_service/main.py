from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models import Post, Comment, Like
from schemas import PostCreate, PostUpdate, CommentCreate
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Chatty Post Service")
Instrumentator().instrument(app).expose(app)


@app.post("/posts")
async def create_post(
    post: PostCreate,
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    db_post = Post(
        title=post.title,
        content=post.content,
        image_filename=image.filename if image else None,
        user_id=1
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return {"message": "Post created", "post": db_post}


@app.get("/posts/{post_id}")
async def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.patch("/posts/{post_id}")
async def update_post(post_id: int, post: PostUpdate, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.title:
        db_post.title = post.title
    if post.content:
        db_post.content = post.content
    db.commit()
    db.refresh(db_post)
    return {"message": "Post updated", "post": db_post}


@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted"}


@app.post("/posts/{post_id}/comments")
async def create_comment(post_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    db_comment = Comment(content=comment.content, post_id=post_id, user_id=1)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return {"message": "Comment added", "comment": db_comment}


@app.get("/posts/{post_id}/comments")
async def get_comments(post_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    return comments


@app.post("/posts/{post_id}/likes")
async def like_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    db_like = Like(post_id=post_id, user_id=1)
    db.add(db_like)
    db.commit()
    return {"message": "Post liked"}


@app.delete("/posts/{post_id}/likes")
async def unlike_post(post_id: int, db: Session = Depends(get_db)):
    db_like = db.query(Like).filter(Like.post_id == post_id, Like.user_id == 1).first()
    if not db_like:
        raise HTTPException(status_code=404, detail="Like not found")
    db.delete(db_like)
    db.commit()
    return {"message": "Like removed"}

