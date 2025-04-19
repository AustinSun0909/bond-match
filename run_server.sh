#!/bin/bash

# Install requirements
echo "Installing required packages..."
pip install -r requirements.txt

# Make migrations
echo "Creating database migrations..."
python manage.py makemigrations

# Apply migrations
echo "Applying migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create a superuser if it doesn't exist
echo "Would you like to create a superuser? (y/n)"
read create_superuser

if [ "$create_superuser" = "y" ]; then
    python manage.py createsuperuser
fi

# Run the server
echo "Starting the Django server..."
python manage.py runserver 