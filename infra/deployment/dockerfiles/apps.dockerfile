# ---- Base Image ----
FROM python:3.12-slim

# ---- Environment Config ----
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ---- Set working directory ----
WORKDIR /app

# ---- Install system dependencies ----
RUN apt-get update 
RUN apt-get install -y curl

# ---- Install packages -----
RUN pip install fastapi acapy_agent acapy-controller uvicorn httpx

# ---- Copy app source  ---- 

COPY ./app .

WORKDIR /

# Run the authoriries app by default
CMD ["uvicorn", "app.app_authorities.main:app", "--host", "0.0.0.0", "--port", "8002"]