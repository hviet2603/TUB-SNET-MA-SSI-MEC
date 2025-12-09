##############################################
#           BUILDER STAGE
##############################################
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build tools for the plugin
RUN apt-get update && apt-get install -y curl \
    && pip install --no-cache-dir build

# Copy plugins
COPY ./acapy-plugins ./acapy-plugins

# Build plugin wheel
RUN python -m build ./acapy-plugins/ShortTTLForDIDDocCache


##############################################
#           FINAL RUNTIME STAGE
##############################################
FROM python:3.12-slim

# ---- Environment Config ----
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system tools
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi==0.123.4 \
    acapy_agent==1.4.0 \
    acapy-controller==0.3.0 \
    uvicorn==0.38.0 \
    httpx==0.28.1 \
    docker==7.1.0

# Copy the plugin wheel from builder
COPY --from=builder /build/acapy-plugins/ShortTTLForDIDDocCache/dist/*.whl /tmp/

# Install plugin wheel
RUN pip install --no-cache-dir /tmp/*.whl \
    && rm -rf /tmp/*.whl

# ---- Copy app source ----
COPY ./app /app

# ---- Run server ----
CMD ["uvicorn", "app.app_authorities.main:app", "--host", "0.0.0.0", "--port", "8002"]