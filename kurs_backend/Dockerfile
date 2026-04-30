FROM python:3.12-slim

# Install build dependencies for psycopg2 etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app

# Install python dependencies using a direct PyPI index and short timeout
COPY requirements.txt .
RUN pip install --no-cache-dir \
    --default-timeout=30 \
    -i https://pypi.org/simple \
    -r requirements.txt
# Copy project files
COPY . .

# Expose Django default port
EXPOSE 8000

# Apply migrations and create a default superuser (if env vars are set)
# then start the development server
ENV DJANGO_SUPERUSER_USERNAME=admin
ENV DJANGO_SUPERUSER_PASSWORD=admin
ENV DJANGO_SUPERUSER_EMAIL=admin@example.com

CMD python manage.py migrate && \
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); "\
    "User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists() or "\
    "User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')" | python manage.py shell && \
    python manage.py runserver 0.0.0.0:8000

