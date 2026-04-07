FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

COPY . /app

EXPOSE 8000

CMD ["sh", "-c", "if [ \"$DJANGO_ENV\" = \"development\" ]; then python manage.py migrate && python manage.py runserver 0.0.0.0:8000; else python manage.py migrate && gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120; fi"]