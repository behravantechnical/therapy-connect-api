# Use an official Python runtime as the base image
FROM python:3.11-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install the project dependencies
RUN apt-get -o Acquire::Check-Valid-Until="false" update && apt-get install -y libpq-dev

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements/ ./
RUN pip install --upgrade pip && pip install -r production.txt

# Copy the project code into the container
COPY ./ ./

# Expose the port on which the Django application will run
EXPOSE 8000

# Run the Django development server
CMD python therapy_connect/manage.py migrate && \
    gunicorn --config deployment/production/django/gunicorn.conf.py --bind 0.0.0.0:8000 --workers=1 "therapy_connect.wsgi:application"

# # Run the Django application with Gunicorn
# CMD python therapy_connect/manage.py migrate && \
#     gunicorn --bind 0.0.0.0:8000 --workers=1 "therapy_connect.wsgi:application"