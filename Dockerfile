# Imagen de producción para Django (Total Living)
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias de sistema (PostgreSQL / compilación si hiciera falta)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Puerto por defecto de Gunicorn (mapear en el host o en orquestador)
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "total_living.wsgi:application"]
