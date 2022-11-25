g:
cd g:\FileServer
venv\scripts\activate
set FLASK_APP=file_server.py
set FLASK_ENV=development
set FLASK_DEBUG=1
set FLASK_CONFIG=development
set FLASK_ADMIN_PASSWORD=123456
flask run -h 0.0.0.0 -p 2333
