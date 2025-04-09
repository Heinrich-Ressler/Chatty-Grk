from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, Post, Like, Subscription
import numpy as np
from typing import List
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Chatty Recommendation Service")
Instrumentator().instrument(app).expose(app)


def get_recommendations(user_id: int, db: Session) -> List[int]:
    all_users = db.query(User).all()
    all_likes = db.query(Like).all()
    user_ids = [user.id for user in all_users]
    post_ids = [post.id for post in db.query(Post).all()]
    matrix = np.zeros((len(user_ids), len(post_ids)))
    for like in all_likes:
        user_idx = user_ids.index(like.user_id)
        post_idx = post_ids.index(like.post_id)
        matrix[user_idx, post_idx] = 1
    try:
        target_idx = user_ids.index(user_id)
    except ValueError:
        return []
    similarities = []
    target_vector = matrix[target_idx]
    for i, vector in enumerate(matrix):
        if i != target_idx:
            dot_product = np.dot(target_vector, vector)
            norm_a = np.linalg.norm(target_vector)
            norm_b = np.linalg.norm(vector)
            similarity = dot_product / (norm_a * norm_b) if norm_a * norm_b > 0 else 0
            similarities.append((user_ids[i], similarity))
    similarities.sort(key=lambda x: x[1], reverse=True)
    similar_users = [user_id for user_id, _ in similarities[:3]]
    user_liked_posts = set(db.query(Like.post_id).filter(Like.user_id == user_id).all())
    recommended_posts = (
        db.query(Like.post_id)
        .filter(Like.user_id.in_(similar_users))
        .filter(Like.post_id.notin_(user_liked_posts))
        .distinct()
        .limit(5)
        .all()
    )
    return [post_id[0] for post_id in recommended_posts]


@app.get("/recommendations")
async def get_user_recommendations(db: Session = Depends(get_db)):
    user_id = 1
    recommended_post_ids = get_recommendations(user_id, db)
    if not recommended_post_ids:
        return {"message": "No recommendations available", "posts": []}
    posts = db.query(Post).filter(Post.id.in_(recommended_post_ids)).all()
    return {"message": "Recommended posts", "posts": posts}

