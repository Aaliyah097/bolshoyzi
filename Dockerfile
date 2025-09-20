# .devcontainer/Dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
ffmpeg \
curl \
privoxy

RUN pip install --no-cache-dir pipenv

WORKDIR /app

COPY Pipfile Pipfile.lock ./

RUN pipenv requirements > requirements.txt \
    && pip install -r requirements.txt

COPY . .

ENV PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LANG=C.UTF-8 LC_ALL=C.UTF-8

CMD ["tail -f /dev/null"]