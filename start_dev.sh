#!/bin/bash

# Start the Django backend server in the background
echo "Starting Django backend server..."
gnome-terminal --tab --title="Backend" -- bash -c "python manage.py runserver 8000; exec bash" &

# Wait a moment to ensure the backend starts
sleep 2

# Start React frontend server
echo "Starting React frontend server..."
cd front-end && npm start 