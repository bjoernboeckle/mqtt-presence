# 1. Verwende ein schlankes Python-Image mit Version 3.11
FROM python:3.11-slim

# 2. Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# 3. Installiere Poetry
RUN pip install poetry

# 4. Kopiere nur die Abhängigkeitsdateien zuerst für Caching
COPY pyproject.toml poetry.lock* /app/

# 5. Kopiere den gesamten Projektcode
COPY . /app

# 6. Installiere Abhängigkeiten ohne virtuelle Umgebung
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi



# 7. Optional: öffne Port 8100 (nur relevant, wenn die App HTTP anbietet)
EXPOSE 8100

# 8. Starte immer mit dem festen Config-Pfad
ENTRYPOINT ["poetry", "run", "mqtt-presence", "--config", "/config", "--log", "/log"]