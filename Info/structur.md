ChattyMicroservices/
├── chatty_auth_service/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── tests/
│       └── test_main.py
├── chatty_post_service/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── tests/
│       └── test_main.py
├── chatty_subscription_service/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── tests/
│       └── test_main.py
├── chatty_admin_service/
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── tests/
│       └── test_main.py
├── chatty_recommendation_service/
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── tests/
│       └── test_main.py
├── docker-compose.yml
├── nginx.conf
├── prometheus.yml
├── locustfile.py
└── .github/
    └── workflows/
        └── ci-cd.yml