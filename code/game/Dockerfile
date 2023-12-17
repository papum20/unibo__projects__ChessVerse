FROM python:3.12.0-slim-bullseye

EXPOSE 8080

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8080
ENV ENV "production"
ENV DATABASE_HOST "mysql"
ENV DATABASE_PORT 3306
ENV DATABASE_USER "root"
ENV DATABASE_PASSWORD "root"
ENV DATABASE_NAME "users_db"

# Directory per le dipendenze
WORKDIR /usr/src/deps

# Installa le dipendenze
COPY requirements.txt .
RUN apt-get update -y && apt-get install gcc -y && apt-get clean
RUN apt-get install pkg-config python3-dev libmariadb-dev-compat libmariadb-dev build-essential -y && apt-get clean
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Directory per il codice dell'applicazione
WORKDIR /usr/src/app

# Copia il codice dell'applicazione
COPY . .

RUN adduser --system --no-create-home python
USER python

CMD ["python", "server.py"]
