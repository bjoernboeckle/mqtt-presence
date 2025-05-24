# 1. Basis-Image mit Python 3.11
FROM python:3.11-slim

# 2. Arbeitsverzeichnis im Container
WORKDIR /app

# 3. Poetry installieren (empfohlen von Poetry-Doku)
RUN pip install poetry

# 4. Kopiere nur die notwendigen Dateien zuerst (für Cache)
COPY pyproject.toml poetry.lock* /app/

# 5. Abhängigkeiten (inkl. dev) installieren
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --with dev

# 6. Projektcode kopieren
COPY . /app

# 7. Expose falls dein Service einen Port verwendet (optional)
EXPOSE 8100

# 8. Standardkommando (hier startest du deinen Service)
CMD ["poetry", "run", "mqtt-presence"]
