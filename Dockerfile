FROM mcr.microsoft.com/playwright/python:v1.55.0-jammy

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1
ENV HEADLESS=true

COPY requirements.txt .

RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements.txt

COPY . .

CMD ["python3", "app.py"]