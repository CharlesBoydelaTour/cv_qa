# Use the official Python image from the Docker Hub
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the Docker container
WORKDIR /code

# Install the dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the working directory
COPY . /code/

WORKDIR /code/cv_qa_website
# Collect static files
RUN python manage.py collectstatic --noinput

# Run the application on port 8000
CMD gunicorn cv_qa_website.wsgi:application --bind 0.0.0.0:8000
