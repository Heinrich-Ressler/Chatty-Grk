import pytest
from fastapi.testclient import TestClient
from chatty_post_service.main import app
from chatty_post_service.database import get_db, Base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db_session():
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def override_get_db():
    db = next(db_session())
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def test_create_post(client: TestClient):
    response = client.post("/posts", json={
        "title": "Test Post",
        "content": "Test Content"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Post created"
