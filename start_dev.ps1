# Start the Django backend server in a new PowerShell window
Write-Host "Starting Django backend server..."
Start-Process powershell -ArgumentList "-Command", "python manage.py runserver 8000; Read-Host 'Press Enter to exit...'"

# Wait a moment to ensure the backend starts
Start-Sleep -Seconds 2

# Start React frontend server
Write-Host "Starting React frontend server..."
Set-Location -Path .\front-end
npm start 