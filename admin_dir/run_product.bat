g:
cd g:\FileServer
venv\scripts\activate
set FLASK_APP=file_server.py
set FLASK_ENV=production
set FLASK_DEBUG=0
set FLASK_CONFIG=production
set FLASK_ADMIN_PASSWORD=197011
flask run -h 0.0.0.0 -p 80