Microsoft Windows [Version 10.0.22000.2538]
(c) Microsoft Corporation. All rights reserved.

C:\Users\dhira\Downloads\MEDFLOW_starter> pip install flask flask-cors
Requirement already satisfied: flask in C:\Users\dhira\AppData\Local\Programs\Python\Python314\Lib\site-packages (3.1.3)
Requirement already satisfied: flask-cors in C:\Users\dhira\AppData\Local\Programs\Python\Python314\Lib\site-packages (6.0.5)
Requirement already satisfied: blinker>=1.9.0 in C:\Users\dhira\AppData\Local\Programs\Python\Python314\Lib\site-packages (from flask) (1.9.0)
Requirement already satisfied: click>=8.1.3 in C:\Users\dhira\AppData\Local\Programs\Python\Python314\Lib\site-packages (from flask) (8.5.0)
Requirement already satisfied: itsdangerous>=2.2.0 in C:\Users\dhira\AppData\Local\Programs\Python\Python314\Lib\site-packages (from flask) (2.2.0)
Requirement already satisfied: jinja2>=3.1.2 in C:\Users\dhira\AppData\Local\Programs\Python\Python314\Lib\site-packages (from flask) (3.1.6)
Requirement already satisfied: markupsafe>=2.1.1 in C:\Users\dhira\AppData\Local\Programs\Python\Python314\Lib\site-packages (from flask) (3.0.3)
Requirement already satisfied: werkzeug>=3.1.0 in C:\Users\dhira\AppData\Local\Programs\Python\Python314\Lib\site-packages (from flask) (3.1.8)

C:\Users\dhira\Downloads\MEDFLOW_starter>python backend\app.py
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 401-495-714
127.0.0.1 - - [20/Sep/2026 08:17:24] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [20/Sep/2026 08:17:24] "GET /style.css HTTP/1.1" 200 -
127.0.0.1 - - [20/Sep/2026 08:17:24] "GET /app.js HTTP/1.1" 200 -
127.0.0.1 - - [20/Sep/2026 08:17:24] "GET /api/hospital HTTP/1.1" 200 -
127.0.0.1 - - [20/Sep/2026 08:17:24] "GET /favicon.ico HTTP/1.1" 404 -
127.0.0.1 - - [20/Sep/2026 08:17:24] "GET /api/patients HTTP/1.1" 200 -

