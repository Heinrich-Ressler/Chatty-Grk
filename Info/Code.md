chatty_auth_service/main.py
python

Свернуть

Перенос

Копировать
from fastapi import FastAPI, HTTPException, Depends
# Импортируем FastAPI для создания веб-приложения, HTTPException для обработки ошибок,
# Depends для внедрения зависимостей.

from sqlalchemy.orm import Session
# Импортируем Session из SQLAlchemy для работы с базой данных.

from database import get_db
# Импортируем функцию get_db из database.py, которая предоставляет сессию БД.

from models import User
# Импортируем модель User из models.py, которая описывает таблицу users.

from schemas import UserCreate, UserLogin
# Импортируем Pydantic-модели UserCreate и UserLogin из schemas.py для валидации данных.

from passlib.context import CryptContext
# Импортируем CryptContext из passlib для хеширования паролей.

import smtplib
# Импортируем smtplib для отправки email-сообщений.

from prometheus_fastapi_instrumentator import Instrumentator
# Импортируем Instrumentator из prometheus_fastapi_instrumentator для мониторинга метрик.

app = FastAPI(title="Chatty Auth Service")
# Создаём экземпляр FastAPI с названием "Chatty Auth Service".

Instrumentator().instrument(app).expose(app)
# Инициализируем мониторинг Prometheus для приложения и добавляем эндпоинт /metrics.

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Создаём объект для хеширования паролей с использованием алгоритма bcrypt.


@app.post("/register")
# Определяем POST-эндпоинт /register для регистрации пользователя.
async def register(user: UserCreate, db: Session = Depends(get_db)):
# Асинхронная функция принимает данные пользователя (UserCreate) и сессию БД через Depends.
    db_user = db.query(User).filter(User.username == user.username).first()
    # Запрашиваем из БД пользователя с таким же именем. .first() возвращает первый результат или None.
    if db_user:
    # Если пользователь уже существует (db_user не None),
        raise HTTPException(status_code=400, detail="Username already registered")
        # Выбрасываем исключение с кодом 400 и сообщением об ошибке.
    hashed_password = pwd_context.hash(user.password)
    # Хешируем пароль пользователя с помощью bcrypt.
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password, is_active=False)
    # Создаём новый объект User с данными из запроса, хешированным паролем и is_active=False.
    db.add(new_user)
    # Добавляем нового пользователя в сессию БД (ещё не сохранено в БД).
    db.commit()
    # Фиксируем изменения в БД, сохраняя пользователя.
    db.refresh(new_user)
    # Обновляем объект new_user данными из БД (например, получаем его ID).
    try:
    # Начинаем блок обработки исключений для отправки email.
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
        # Открываем соединение с SMTP-сервером Gmail на порту 587.
            server.starttls()
            # Включаем шифрование TLS для безопасной отправки.
            server.login("chatty@example.com", "password")
            # Авторизуемся на сервере с фиктивными логином и паролем (нужно заменить на реальные).
            message = f"Subject: Подтверждение\n\nПодтвердите: http://localhost/auth/verify/{new_user.id}"
            # Формируем текстовое сообщение с ссылкой для верификации.
            server.sendmail("chatty@example.com", user.email, message)
            # Отправляем email от "chatty@example.com" на email пользователя.
    except Exception:
    # Если произошла ошибка (например, SMTP-сервер недоступен),
        raise HTTPException(status_code=500, detail="Email error")
        # Выбрасываем исключение с кодом 500 и сообщением об ошибке.
    return {"message": f"User {user.username} registered, check your email"}
    # Возвращаем успешный ответ с сообщением о регистрации.


@app.post("/login")
# Определяем POST-эндпоинт /login для входа пользователя.
async def login(user: UserLogin, db: Session = Depends(get_db)):
# Асинхронная функция принимает данные для входа (UserLogin) и сессию БД.
    db_user = db.query(User).filter(User.username == user.username).first()
    # Ищем пользователя в БД по имени.
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
    # Если пользователя нет или пароль не совпадает (проверяем через pwd_context.verify),
        raise HTTPException(status_code=400, detail="Invalid credentials")
        # Выбрасываем исключение с кодом 400 и сообщением об ошибке.
    if not db_user.is_active:
    # Если аккаунт не верифицирован (is_active=False),
        raise HTTPException(status_code=400, detail="Account not verified")
        # Выбрасываем исключение с кодом 400 и сообщением об ошибке.
    return {"message": "Login successful", "token": "fake-jwt-token", "user_id": db_user.id}
    # Возвращаем успешный ответ с фиктивным токеном и ID пользователя.


@app.get("/verify/{user_id}")
# Определяем GET-эндпоинт /verify/{user_id} для верификации аккаунта.
async def verify_account(user_id: int, db: Session = Depends(get_db)):
# Асинхронная функция принимает user_id из URL и сессию БД.
    db_user = db.query(User).filter(User.id == user_id).first()
    # Ищем пользователя в БД по ID.
    if not db_user:
    # Если пользователь не найден,
        raise HTTPException(status_code=404, detail="User not found")
        # Выбрасываем исключение с кодом 404 и сообщением об ошибке.
    db_user.is_active = True
    # Устанавливаем флаг is_active в True, чтобы верифицировать аккаунт.
    db.commit()
    # Фиксируем изменения в БД.
    return {"message": "Account verified"}
    # Возвращаем успешный ответ с сообщением о верификации.
Как работает:

Запускается FastAPI-приложение, подключается к PostgreSQL через get_db.
При POST-запросе на /register создаётся новый пользователь, хешируется пароль, отправляется email.
При POST-запросе на /login проверяются учетные данные, возвращается токен (пока фиктивный).
При GET-запросе на /verify/{user_id} активируется аккаунт.
chatty_post_service/main.py
python

Свернуть

Перенос

Копировать
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
# Импортируем FastAPI, HTTPException, Depends, а также UploadFile и File для загрузки файлов.

from sqlalchemy.orm import Session
# Импортируем Session для работы с БД.

from database import get_db
# Импортируем get_db для получения сессии БД.

from models import Post, Comment, Like
# Импортируем модели Post, Comment, Like из models.py.

from schemas import PostCreate, PostUpdate, CommentCreate
# Импортируем Pydantic-модели для валидации данных.

from prometheus_fastapi_instrumentator import Instrumentator
# Импортируем Instrumentator для мониторинга.

app = FastAPI(title="Chatty Post Service")
# Создаём FastAPI-приложение с названием "Chatty Post Service".

Instrumentator().instrument(app).expose(app)
# Настраиваем мониторинг Prometheus.


@app.post("/posts")
# Определяем POST-эндпоинт /posts для создания поста.
async def create_post(post: PostCreate, image: UploadFile = File(None), db: Session = Depends(get_db)):
# Функция принимает данные поста (PostCreate), необязательный файл изображения и сессию БД.
    db_post = Post(title=post.title, content=post.content, image_filename=image.filename if image else None, user_id=1)
    # Создаём объект Post с данными из запроса, именем файла (если есть) и фиктивным user_id=1.
    db.add(db_post)
    # Добавляем пост в сессию БД.
    db.commit()
    # Фиксируем изменения в БД.
    db.refresh(db_post)
    # Обновляем объект db_post данными из БД (например, ID).
    return {"message": "Post created", "post": db_post}
    # Возвращаем сообщение об успехе и данные поста.


@app.get("/posts/{post_id}")
# Определяем GET-эндпоинт /posts/{post_id} для получения поста.
async def get_post(post_id: int, db: Session = Depends(get_db)):
# Функция принимает ID поста из URL и сессию БД.
    post = db.query(Post).filter(Post.id == post_id).first()
    # Ищем пост в БД по ID.
    if not post:
    # Если пост не найден,
        raise HTTPException(status_code=404, detail="Post not found")
        # Выбрасываем исключение с кодом 404.
    return post
    # Возвращаем данные поста.


@app.patch("/posts/{post_id}")
# Определяем PATCH-эндпоинт /posts/{post_id} для обновления поста.
async def update_post(post_id: int, post: PostUpdate, db: Session = Depends(get_db)):
# Функция принимает ID поста, данные для обновления (PostUpdate) и сессию БД.
    db_post = db.query(Post).filter(Post.id == post_id).first()
    # Ищем пост в БД по ID.
    if not db_post:
    # Если пост не найден,
        raise HTTPException(status_code=404, detail="Post not found")
        # Выбрасываем исключение с кодом 404.
    if post.title:
    # Если в запросе есть заголовок,
        db_post.title = post.title
        # Обновляем заголовок поста.
    if post.content:
    # Если в запросе есть контент,
        db_post.content = post.content
        # Обновляем контент поста.
    db.commit()
    # Фиксируем изменения в БД.
    db.refresh(db_post)
    # Обновляем объект db_post.
    return {"message": "Post updated", "post": db_post}
    # Возвращаем сообщение и обновлённые данные поста.


@app.delete("/posts/{post_id}")
# Определяем DELETE-эндпоинт /posts/{post_id} для удаления поста.
async def delete_post(post_id: int, db: Session = Depends(get_db)):
# Функция принимает ID поста и сессию БД.
    db_post = db.query(Post).filter(Post.id == post_id).first()
    # Ищем пост в БД по ID.
    if not db_post:
    # Если пост не найден,
        raise HTTPException(status_code=404, detail="Post not found")
        # Выбрасываем исключение с кодом 404.
    db.delete(db_post)
    # Удаляем пост из БД.
    db.commit()
    # Фиксируем изменения.
    return {"message": "Post deleted"}
    # Возвращаем сообщение об успехе.


@app.post("/posts/{post_id}/comments")
# Определяем POST-эндпоинт /posts/{post_id}/comments для добавления комментария.
async def create_comment(post_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
# Функция принимает ID поста, данные комментария (CommentCreate) и сессию БД.
    db_post = db.query(Post).filter(Post.id == post_id).first()
    # Ищем пост в БД по ID.
    if not db_post:
    # Если пост не найден,
        raise HTTPException(status_code=404, detail="Post not found")
        # Выбрасываем исключение с кодом 404.
    db_comment = Comment(content=comment.content, post_id=post_id, user_id=1)
    # Создаём объект Comment с контентом, ID поста и фиктивным user_id=1.
    db.add(db_comment)
    # Добавляем комментарий в сессию БД.
    db.commit()
    # Фиксируем изменения.
    db.refresh(db_comment)
    # Обновляем объект db_comment.
    return {"message": "Comment added", "comment": db_comment}
    # Возвращаем сообщение и данные комментария.


@app.get("/posts/{post_id}/comments")
# Определяем GET-эндпоинт /posts/{post_id}/comments для получения комментариев.
async def get_comments(post_id: int, db: Session = Depends(get_db)):
# Функция принимает ID поста и сессию БД.
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    # Получаем все комментарии для данного поста из БД.
    return comments
    # Возвращаем список комментариев.


@app.post("/posts/{post_id}/likes")
# Определяем POST-эндпоинт /posts/{post_id}/likes для добавления лайка.
async def like_post(post_id: int, db: Session = Depends(get_db)):
# Функция принимает ID поста и сессию БД.
    db_post = db.query(Post).filter(Post.id == post_id).first()
    # Ищем пост в БД по ID.
    if not db_post:
    # Если пост не найден,
        raise HTTPException(status_code=404, detail="Post not found")
        # Выбрасываем исключение с кодом 404.
    db_like = Like(post_id=post_id, user_id=1)
    # Создаём объект Like с ID поста и фиктивным user_id=1.
    db.add(db_like)
    # Добавляем лайк в сессию БД.
    db.commit()
    # Фиксируем изменения.
    return {"message": "Post liked"}
    # Возвращаем сообщение об успехе.


@app.delete("/posts/{post_id}/likes")
# Определяем DELETE-эндпоинт /posts/{post_id}/likes для удаления лайка.
async def unlike_post(post_id: int, db: Session = Depends(get_db)):
# Функция принимает ID поста и сессию БД.
    db_like = db.query(Like).filter(Like.post_id == post_id, Like.user_id == 1).first()
    # Ищем лайк в БД по ID поста и фиктивному user_id=1.
    if not db_like:
    # Если лайк не найден,
        raise HTTPException(status_code=404, detail="Like not found")
        # Выбрасываем исключение с кодом 404.
    db.delete(db_like)
    # Удаляем лайк из БД.
    db.commit()
    # Фиксируем изменения.
    return {"message": "Like removed"}
    # Возвращаем сообщение об успехе.
Как работает:

Приложение предоставляет CRUD-операции для постов, комментариев и лайков.
Все операции используют общую базу данных через get_db.
user_id захардкожен как 1 (нужно доработать для реальной аутентификации).
chatty_subscription_service/main.py
python

Свернуть

Перенос

Копировать
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
    # Задаём фиктивный user_id=1 (нужно заменить на реальный из токена).
    existing_subscription = db.query(Subscription).filter(Subscription.follower_id == user_id, Subscription.following_id == following_id).first()
    # Проверяем, есть ли уже подписка от user_id на following_id.
    if existing_subscription:
        raise HTTPException(status_code=400, detail="Already subscribed")
    db_subscription = Subscription(follower_id=user_id, following_id=following_id)
    # Создаём новую подписку.
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return {"message": f"Subscribed to user {following_id}"}


@app.delete("/unsubscribe/{following_id}")
async def unsubscribe(following_id: int, db: Session = Depends(get_db)):
    user_id = 1
    db_subscription = db.query(Subscription).filter(Subscription.follower_id == user_id, Subscription.following_id == following_id).first()
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    db.delete(db_subscription)
    db.commit()
    return {"message": f"Unsubscribed from user {following_id}"}


@app.get("/feed")
async def get_feed(db: Session = Depends(get_db)):
    user_id = 1
    following_ids = db.query(Subscription.following_id).filter(Subscription.follower_id == user_id).all()
    # Получаем список ID пользователей, на которых подписан user_id.
    following_ids = [id[0] for id in following_ids]
    # Преобразуем результат в список чисел.
    if not following_ids:
        return {"message": "No subscriptions yet", "posts": []}
    posts = db.query(Post).filter(Post.user_id.in_(following_ids)).all()
    # Получаем все посты от пользователей из following_ids.
    return {"message": "Your feed", "posts": posts}
Как работает:

Управляет подписками и лентой пользователя.
/subscribe/{id} добавляет подписку, /unsubscribe/{id} удаляет, /feed возвращает посты подписанных пользователей.



# **chatty_admin_service/main.py**


from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, Post, Comment
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from prometheus_fastapi_instrumentator import Instrumentator

sentry_sdk.init(dsn="https://example@sentry.io/123", integrations=[FastApiIntegration()], traces_sample_rate=1.0)
# Инициализируем Sentry для логирования ошибок и событий.

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
    # Считаем общее количество пользователей.
    active_users = db.query(User).filter(User.is_active == True).count()
    # Считаем активных пользователей.
    total_posts = db.query(Post).count()
    # Считаем общее количество постов.
    total_comments = db.query(Comment).count()
    # Считаем общее количество комментариев.
    stats = {"total_users": total_users, "active_users": active_users, "total_posts": total_posts, "total_comments": total_comments}
    # Формируем словарь со статистикой.
    sentry_sdk.capture_message("Admin requested activity stats")
    # Логируем запрос статистики в Sentry.
    return {"message": "Activity stats", "stats": stats}


Как работает:
Админский сервис для блокировки пользователей, удаления контента и получения статистики.
Использует Sentry для логирования действий.



# **chatty_recommendation_service/main.py**

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
    # Получаем всех пользователей.
    all_likes = db.query(Like).all()
    # Получаем все лайки.
    user_ids = [user.id for user in all_users]
    # Формируем список ID пользователей.
    post_ids = [post.id for post in db.query(Post).all()]
    # Формируем список ID постов.
    matrix = np.zeros((len(user_ids), len(post_ids)))
    # Создаём матрицу нулей размером пользователи × посты.
    for like in all_likes:
        user_idx = user_ids.index(like.user_id)
        post_idx = post_ids.index(like.post_id)
        matrix[user_idx, post_idx] = 1
        # Заполняем матрицу: 1, если пользователь лайкнул пост.
    try:
        target_idx = user_ids.index(user_id)
    except ValueError:
        return []
    similarities = []
    target_vector = matrix[target_idx]
    # Вектор лайков целевого пользователя.
    for i, vector in enumerate(matrix):
        if i != target_idx:
            dot_product = np.dot(target_vector, vector)
            norm_a = np.linalg.norm(target_vector)
            norm_b = np.linalg.norm(vector)
            similarity = dot_product / (norm_a * norm_b) if norm_a * norm_b > 0 else 0
            similarities.append((user_ids[i], similarity))
            # Считаем косинусное сходство между пользователями.
    similarities.sort(key=lambda x: x[1], reverse=True)
    # Сортируем по убыванию сходства.
    similar_users = [user_id for user_id, _ in similarities[:3]]
    # Берём 3 самых похожих пользователей.
    user_liked_posts = set(db.query(Like.post_id).filter(Like.user_id == user_id).all())
    # Получаем посты, которые уже лайкнул пользователь.
    recommended_posts = db.query(Like.post_id).filter(Like.user_id.in_(similar_users)).filter(Like.post_id.notin_(user_liked_posts)).distinct().limit(5).all()
    # Получаем до 5 уникальных постов от похожих пользователей, которые целевой не лайкал.
    return [post_id[0] for post_id in recommended_posts]
    # Возвращаем список ID постов.


@app.get("/recommendations")
async def get_user_recommendations(db: Session = Depends(get_db)):
    user_id = 1
    recommended_post_ids = get_recommendations(user_id, db)
    if not recommended_post_ids:
        return {"message": "No recommendations available", "posts": []}
    posts = db.query(Post).filter(Post.id.in_(recommended_post_ids)).all()
    return {"message": "Recommended posts", "posts": posts}
Как работает:

Использует коллаборативную фильтрацию для рекомендаций.
Сравнивает лайки пользователей через косинусное сходство.



# **docker-compose.yml**

version: "3.9"
# Указываем версию Docker Compose.

services:
  auth_service:
    build:
      context: ./chatty_auth_service
    # Собираем образ из директории chatty_auth_service.
    expose:
      - "8000"
    # Открываем порт 8000 внутри контейнера.
    volumes:
      - ./chatty_auth_service:/app
    # Монтируем локальную директорию в контейнер.
    environment:
      - PYTHONUNBUFFERED=1
    # Отключаем буферизацию вывода Python.
    depends_on:
      - postgres
    # Зависит от сервиса postgres.

  # Аналогично для других сервисов: post_service, subscription_service, admin_service, recommendation_service.
  # Отличаются порты (8001, 8002, 8003, 8004) и пути сборки.

  postgres:
    image: postgres:13
    # Используем образ PostgreSQL 13.
    environment:
      - POSTGRES_USER=chatty_user
      - POSTGRES_PASSWORD=chatty_pass
      - POSTGRES_DB=chatty_db
    # Устанавливаем имя пользователя, пароль и БД.
    volumes:
      - postgres_data:/var/lib/postgresql/data
    # Сохраняем данные БД в томе.
    ports:
      - "5432:5432"
    # Пробрасываем порт 5432 на хост.

  locust:
    image: locustio/locust
    ports:
      - "8089:8089"
    volumes:
      - ./locustfile.py:/mnt/locust/locustfile.py
    command: -f /mnt/locust/locustfile.py --host http://nginx:80
    depends_on:
      - nginx

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
    depends_on:
      - nginx

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    depends_on:
      - prometheus

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - auth_service
      - post_service
      - subscription_service
      - admin_service
      - recommendation_service

volumes:
  postgres_data:
    # Определяем том для хранения данных PostgreSQL.

-------------------------------------------------------------
Теория: От монолита к микросервисам
Монолитное приложение
В монолитном приложении у тебя есть одно приложение и одна база данных. Например:

Приложение: Соцсеть с пользователями, постами, комментариями и подписками.
База данных: Одна PostgreSQL БД с таблицами users, posts, comments, subscriptions, likes.
Всё приложение (логика авторизации, постов, подписок) живёт в одном коде и обращается к этой единой базе. Это удобно для простоты разработки, но становится проблемой при масштабировании или изменении отдельных частей.

Переход к микросервисам
Когда ты делишь монолит на микросервисы, ты разбиваешь логику на отдельные приложения (сервисы), каждый из которых отвечает за свою задачу. В нашем проекте:

chatty_auth_service — авторизация и регистрация.
chatty_post_service — посты, комментарии, лайки.
chatty_subscription_service — подписки и лента.
chatty_admin_service — админские функции.
chatty_recommendation_service — рекомендации.


Но что делать с базой данных? Есть два основных подхода:

Общая база данных (Shared Database):
Все микросервисы используют одну базу данных.
Таблицы остаются теми же, но каждый сервис обращается только к "своим" данным.
Плюсы: Простота миграции, данные остаются связанными.
Минусы: Тесная связь между сервисами, проблемы с масштабированием БД.
Отдельные базы данных (Database per Service):
Каждый сервис получает свою собственную базу данных.
Данные дублируются или разделяются между базами, а сервисы обмениваются информацией через API.
Плюсы: Независимость сервисов, лучшее масштабирование.
Минусы: Сложность синхронизации данных, дублирование.
В нашем проекте мы используем общую базу данных, но я объясню оба подхода, чтобы ты понял, как можно было бы сделать несколько баз и сохранить данные.

На примере проекта
1. Общая база данных (как у нас сейчас)
В ChattyMicroservices все сервисы подключены к одной PostgreSQL базе данных, которая описана в docker-compose.yml:


postgres:
  image: postgres:13
  environment:
    - POSTGRES_USER=chatty_user
    - POSTGRES_PASSWORD=chatty_pass
    - POSTGRES_DB=chatty_db
  volumes:
    - postgres_data:/var/lib/postgresql/data
  ports:
    - "5432:5432"
Каждый сервис в своём database.py использует одну и ту же строку подключения:

SQLALCHEMY_DATABASE_URL = "postgresql://chatty_user:chatty_pass@postgres:5432/chatty_db"
Таблицы:

users (для авторизации, админки, рекомендаций).
posts (для постов, подписок, рекомендаций).
comments (для постов, админки).
likes (для постов, рекомендаций).
subscriptions (для подписок, рекомендаций).
Как работает:

chatty_auth_service создаёт пользователя в таблице users.
chatty_post_service добавляет пост в posts, используя user_id из users.
chatty_subscription_service читает subscriptions и posts для формирования ленты.
Все сервисы обращаются к одной БД, но работают с "своими" таблицами или их частями.
Плюсы:

Данные хранятся в одном месте, ничего не теряется.
Связность (например, user_id в posts ссылается на users) сохраняется автоматически.
Минусы:

Если БД упадёт, все сервисы пострадают.
Тяжело масштабировать, если один сервис сильно нагружает БД.


# 2. Отдельные базы данных

Предположим, мы хотим разделить одну базу на несколько, чтобы каждый сервис имел свою БД. Как это сделать?

Шаг 1: Разделение таблиц
chatty_auth_service → БД auth_db:
Таблица users (id, username, email, hashed_password, is_active).
chatty_post_service → БД post_db:
Таблицы posts (id, title, content, user_id, image_filename), comments (id, content, post_id, user_id), likes (id, post_id, user_id).
chatty_subscription_service → БД subscription_db:
Таблица subscriptions (id, follower_id, following_id).
Копия posts (id, title, content, user_id) для ленты.
chatty_admin_service → БД admin_db:
Копии users, posts, comments для управления.
chatty_recommendation_service → БД recommendation_db:
Копии users, posts, likes для рекомендаций.

Шаг 2: Изменение docker-compose.yml
Добавляем отдельные экземпляры PostgreSQL:


services:
  auth_db:
    image: postgres:13
    environment:
      - POSTGRES_USER=auth_user
      - POSTGRES_PASSWORD=auth_pass
      - POSTGRES_DB=auth_db
    ports:
      - "5432:5432"
  post_db:
    image: postgres:13
    environment:
      - POSTGRES_USER=post_user
      - POSTGRES_PASSWORD=post_pass
      - POSTGRES_DB=post_db
    ports:
      - "5433:5432"
  # И так далее для subscription_db, admin_db, recommendation_db с разными портами.
Шаг 3: Обновление database.py
Каждый сервис подключается к своей БД:

chatty_auth_service/database.py:

SQLALCHEMY_DATABASE_URL = "postgresql://auth_user:auth_pass@auth_db:5432/auth_db"
chatty_post_service/database.py:


SQLALCHEMY_DATABASE_URL = "postgresql://post_user:post_pass@post_db:5432/post_db"
Шаг 4: Синхронизация данных
Проблема: Данные теперь разрознены. Например:

chatty_post_service создаёт пост с user_id, но этот user_id должен быть в auth_db.
chatty_subscription_service нужен доступ к posts для ленты, но они в post_db.
Решение — событийная синхронизация:

События: Когда chatty_auth_service создаёт пользователя, он отправляет событие (например, через очередь сообщений Kafka или RabbitMQ) в другие сервисы: "Создан пользователь с id=1, username=test".
API: Сервисы запрашивают данные друг у друга. Например, chatty_post_service перед созданием поста делает GET-запрос к chatty_auth_service для проверки user_id.
Дублирование: Копируем минимально необходимые данные. Например, subscription_db хранит копию posts с полями id, title, content, user_id.
Пример в коде (chatty_post_service/main.py):


import aiohttp

async def create_post(post: PostCreate, db: Session = Depends(get_db)):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://auth_service:8000/verify_user/{user_id}") as resp:
            if resp.status != 200:
                raise HTTPException(status_code=400, detail="Invalid user")
    db_post = Post(title=post.title, content=post.content, user_id=user_id)
    db.add(db_post)
    db.commit()
    # Отправляем событие в очередь для subscription_service и recommendation_service.
Шаг 5: Сохранение данных
Данные не теряются, если настроена синхронизация.
Например, если пользователь заблокирован в auth_db, admin_service уведомляет post_db и subscription_db через API или события.
Плюсы:

Каждый сервис независим, можно масштабировать отдельно.
Если одна БД упадёт, другие сервисы могут продолжать работать.
Минусы:

Сложность синхронизации.
Дублирование данных увеличивает объём хранения.
Как это работает в нашем проекте
Сейчас у нас общая база, и это упрощает работу:

chatty_auth_service пишет в users, а chatty_post_service читает user_id оттуда же.
Данные не дублируются, всё хранится в одном месте (chatty_db).
Если бы мы перешли к отдельным базам:

Нужно было бы переписать database.py для каждой БД.
Добавить механизм синхронизации (API или очереди).
Обновить модели (models.py), чтобы они работали только со "своими" таблицами.
Итог
Сейчас: Одна БД (chatty_db) с общей схемой, все сервисы работают с ней через SQLAlchemy. Данные не теряются, так как они в одном месте.
Разделение: Делим таблицы по сервисам, добавляем синхронизацию через API/события, чтобы данные оставались консистентными.



Измени Dockerfile для каждого сервиса (например, chatty_auth_service/Dockerfile):
dockerfile

Свернуть

Перенос

Копировать
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn
# Добавляем wait-for-it
RUN apt-get update && apt-get install -y wait-for-it
COPY . .
CMD ["wait-for-it", "postgres:5432", "--", "gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]
Пересобери и запусти:
bash

Свернуть

Перенос

Копировать
docker-compose down
docker-compose up --build
wait-for-it будет ждать, пока postgres:5432 не станет доступен, прежде чем запустить Gunicorn.
3. Увеличить таймаут подключения
Если не хочешь добавлять wait-for-it, можно настроить SQLAlchemy ждать дольше:

В database.py добавь параметры в create_engine:
python

Свернуть

Перенос

Копировать
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"connect_timeout": 10})
Это даст PostgreSQL 10 секунд на старт.



# 4. Проверить порядок запуска

## Убедись, что postgres запускается первым:

### Останови всё:
docker-compose down

### Запусти только PostgreSQL:
docker-compose up -d postgres

### Проверь логи:
docker-compose logs postgres

### Должно быть что-то вроде:
postgresql 13: LOG:  database system is ready to accept connections

### Затем запусти остальное:
docker-compose up --build