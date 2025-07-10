# syntax=docker/dockerfile:1
FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir firebase-admin pandas

COPY . .

CMD ["python", "src/main.py"] 