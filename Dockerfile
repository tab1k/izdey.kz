FROM python:3.10

# Установка зависимостей
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean && rm -rf /var/lib/apt/lists/*

# Установка рабочего каталога
WORKDIR /code

# Переменные окружения
ENV PYTHONUNBUFFERED 1

# Копирование зависимостей и установка
COPY requirements.txt /code/requirements.txt
RUN pip install --upgrade pip && pip install -r /code/requirements.txt

# Установка Gunicorn
RUN pip install --no-cache-dir gunicorn

# Копирование проекта в контейнер
COPY ./src /code/

# Копирование и установка прав для entrypoint
COPY ./docker-entrypoint.sh /code/docker-entrypoint.sh
RUN chmod +x /code/docker-entrypoint.sh

# Установка прав на статику и медиа
RUN mkdir -p /code/staticfiles /code/media

# Исправление кодировки entrypoint
RUN sed -i 's/\r$//' /code/docker-entrypoint.sh


CMD ["gunicorn", "work.wsgi:application", "--bind", "0.0.0.0:8000"]
