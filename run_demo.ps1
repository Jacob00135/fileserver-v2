.\venv\scripts\activate
$env:FLASK_APP="file_server.py"
$env:FLASK_ENV="production"
$env:FLASK_DEBUG="0"
$env:FLASK_CONFIG="production"
$env:FLASK_ADMIN_PASSWORD="123456"
$env:FLASK_PAGE_MAX="20"
flask.exe run -h 0.0.0.0 -p 5000
