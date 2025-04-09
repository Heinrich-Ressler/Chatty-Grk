from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Subscription, Post
from schemas import SubscriptionCreate
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Chatty Subscription Service")
Instrumentator().instrument(app).expose(app)


@app.post("/subscribe/{following_id}")
async def subscribe(following_id: int, db: Session = Depends(get_db)):
    user_id = 1
    existing_subscription = db.query(Subscription).filter(
        Subscription.follower_id == user_id,
        Subscription.following_id == following_id
    ).first()
    if existing_subscription:
        raise HTTPException(status_code=400, detail="Already subscribed")
    db_subscription = Subscription(follower_id=user_id, following_id=following_id)
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return {"message": f"Subscribed to user {following_id}"}


@app.delete("/unsubscribe/{following_id}")
async def unsubscribe(following_id: int, db: Session = Depends(get_db)):
    user_id = 1
    db_subscription = db.query(Subscription).filter(
        Subscription.follower_id == user_id,
        Subscription.following_id == following_id
    ).first()
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    db.delete(db_subscription)
    db.commit()
    return {"message": f"Unsubscribed from user {following_id}"}


@app.get("/feed")
async def get_feed(db: Session = Depends(get_db)):
    user_id = 1
    following_ids = db.query(Subscription.following_id).filter(
        Subscription.follower_id == user_id
    ).all()
    following_ids = [id[0] for id in following_ids]
    if not following_ids:
        return {"message": "No subscriptions yet", "posts": []}
    posts = db.query(Post).filter(Post.user_id.in_(following_ids)).all()
    return {"message": "Your feed", "posts": posts}
