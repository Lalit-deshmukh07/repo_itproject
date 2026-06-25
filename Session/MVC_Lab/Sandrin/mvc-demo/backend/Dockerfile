FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY alembic.ini .
COPY alembic ./alembic

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["python", "-m", "app.main"]
