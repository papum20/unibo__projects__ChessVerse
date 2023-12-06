FROM python:3.12.0-slim-bullseye

EXPOSE 8000

# Set environment variables
## for python to not write pyc files
ENV PYTHONDONTWRITEBYTECODE 1
## for logs
ENV PYTHONUNBUFFERED 1

# Set work directory in the container
WORKDIR /usr/src/app

# Install dependencies
COPY requirements.txt .
RUN apt-get update -y && apt-get install gcc pkg-config -y && apt-get clean 
RUN apt-get install python3-dev default-libmysqlclient-dev build-essential -y && apt-get clean
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


# Copy the current directory contents into the container
COPY . .

RUN adduser --system --no-create-home python
USER python
COPY runserver.sh /usr/local/bin/runserver.sh

# Run the command to start uWSGI
CMD ["/usr/local/bin/runserver.sh"]
