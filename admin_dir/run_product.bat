g:
cd g:\FileServer
venv\scripts\activate
set FLASK_APP=file_server.py
set FLASK_ENV=production
set FLASK_DEBUG=0
set FLASK_CONFIG=production
set FLASK_ADMIN_PASSWORD=123456
flask run -h 0.0.0.0 -p 2333

cd g:\FileServer
.\venv\scripts\activate
$env:FLASK_APP="file_server.py"
$env:FLASK_ENV="production"
$env:FLASK_DEBUG="0"
$env:FLASK_CONFIG="production"
$env:FLASK_ADMIN_PASSWORD="123456"
flask.exe run -h 0.0.0.0 -p 2333
