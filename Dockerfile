# Imagen de Azmuth para CI/CD: corre las pruebas y levanta la API
# FastAPI (servidor.py) sin necesidad de micrófono ni pantalla.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/estado')" || exit 1

CMD ["uvicorn", "servidor:app", "--host", "0.0.0.0", "--port", "8080"]
