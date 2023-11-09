FROM python:3.12.0-slim-bullseye
#FROM python:3.9-slim-bullseye

# Set environment variables
## for python to not write pyc files
ENV PYTHONDONTWRITEBYTECODE 1
## for logs
ENV PYTHONUNBUFFERED 1

# Set work directory in the container
WORKDIR /usr/src/app

# Install dependencies
COPY requirements.txt .
RUN apt-get update -y && apt-get install gcc -y
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . .

# Run the command to start uWSGI
CMD ["python", "app.py"]