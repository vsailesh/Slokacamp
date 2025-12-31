FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy project
COPY backend /app

# Make directories for mounted media/static
RUN mkdir -p /vol/web/static /vol/web/media

ENV DJANGO_SETTINGS_MODULE=slokcamp.settings
ENV PORT=8000

# Collect static (if configured) — don't fail build if collectstatic needs DB
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "slokcamp.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
