FROM python:3.11-slim

WORKDIR /app

# Copy metadata first
COPY pyproject.toml .
COPY LICENSE .
COPY README.md .

# Copy source
COPY mqtt_presence/ mqtt_presence/

# Install build system and dependencies
RUN pip install --upgrade pip setuptools wheel \
    && pip install .

EXPOSE 8000

CMD ["python", "-m", "mqtt_presence.main"]
