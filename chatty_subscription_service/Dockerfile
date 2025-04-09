#FROM python:3.9-slim
#WORKDIR /app
#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt gunicorn
#COPY . .
#CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8002"]

FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn
# Добавляем wait-for-it
RUN apt-get update && apt-get install -y wait-for-it
COPY . .
CMD ["wait-for-it", "postgres:5432", "--", "gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8002"]