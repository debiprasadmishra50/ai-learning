# Python Servers Guide

This guide covers different ways to create servers in Python, from basic HTTP servers to advanced web frameworks.

## Table of Contents

1. [Basic HTTP Server](#1-basic-http-server)
2. [Simple TCP Server](#2-simple-tcp-server)
3. [Flask Web Server](#3-flask-web-server)
4. [FastAPI Server](#4-fastapi-server)
5. [Django Server](#5-django-server)
6. [Socket.IO Server](#6-socketio-server)

## 1. Basic HTTP Server

### Using Python's Built-in HTTP Server

The simplest way to create an HTTP server in Python:

```python
# simple_http_server.py
import http.server
import socketserver
from http.server import SimpleHTTPRequestHandler

PORT = 8000

class MyHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Hello, World!</h1><p>This is a simple HTTP server.</p>')
        elif self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"message": "Hello from API", "status": "success"}')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>404 - Page Not Found</h1>')

# Create and start the server
with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"Server running at http://localhost:{PORT}")
    httpd.serve_forever()
```

### One-liner HTTP Server

```bash
# Serve current directory on port 8000
python -m http.server 8000

# Serve specific directory
python -m http.server 8000 --directory /path/to/directory
```

## 2. Simple TCP Server

For low-level network communication:

```python
# tcp_server.py
import socket
import threading

class TCPServer:
    def __init__(self, host='localhost', port=9999):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def handle_client(self, client_socket, address):
        """Handle individual client connections"""
        print(f"Connection from {address}")

        try:
            while True:
                # Receive data from client
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break

                print(f"Received: {data}")

                # Echo the data back to client
                response = f"Server received: {data}"
                client_socket.send(response.encode('utf-8'))

        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()
            print(f"Connection with {address} closed")

    def start(self):
        """Start the TCP server"""
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            print(f"TCP Server listening on {self.host}:{self.port}")

            while True:
                client_socket, address = self.socket.accept()

                # Handle each client in a separate thread
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()

        except KeyboardInterrupt:
            print("\nShutting down server...")
        finally:
            self.socket.close()

if __name__ == "__main__":
    server = TCPServer()
    server.start()
```

## 3. Flask Web Server

Flask is a lightweight web framework perfect for small to medium applications:

```python
# flask_server.py
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)

# In-memory data store
users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}
]

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .user { background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Flask Server Demo</h1>
    <h2>Users:</h2>
    {% for user in users %}
    <div class="user">
        <strong>{{ user.name }}</strong> - {{ user.email }}
    </div>
    {% endfor %}

    <h2>API Endpoints:</h2>
    <ul>
        <li>GET /api/users - Get all users</li>
        <li>POST /api/users - Create new user</li>
        <li>GET /api/users/&lt;id&gt; - Get specific user</li>
    </ul>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, users=users)

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(users)

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()

    if not data or 'name' not in data or 'email' not in data:
        return jsonify({"error": "Name and email are required"}), 400

    new_user = {
        "id": len(users) + 1,
        "name": data['name'],
        "email": data['email']
    }
    users.append(new_user)

    return jsonify(new_user), 201

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "message": "Server is running"})

if __name__ == '__main__':
    print("Starting Flask server...")
    print("Visit: http://localhost:5000")
    print("API: http://localhost:5000/api/users")
    app.run(debug=True, host='0.0.0.0', port=5000)
```

## 4. FastAPI Server

FastAPI is a modern, fast web framework with automatic API documentation:

```python
# fastapi_server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="FastAPI Server Demo", version="1.0.0")

# Pydantic models for request/response validation
class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    age: Optional[int] = None

class UserCreate(BaseModel):
    name: str
    email: str
    age: Optional[int] = None

# In-memory database
users_db = [
    User(id=1, name="Alice", email="alice@example.com", age=30),
    User(id=2, name="Bob", email="bob@example.com", age=25)
]

@app.get("/")
async def root():
    return {
        "message": "Welcome to FastAPI Server",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/api/users", response_model=List[User])
async def get_users():
    return users_db

@app.post("/api/users", response_model=User)
async def create_user(user: UserCreate):
    new_user = User(
        id=len(users_db) + 1,
        name=user.name,
        email=user.email,
        age=user.age
    )
    users_db.append(new_user)
    return new_user

@app.get("/api/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/api/users/{user_id}", response_model=User)
async def update_user(user_id: int, user_update: UserCreate):
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = user_update.name
    user.email = user_update.email
    user.age = user_update.age
    return user

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int):
    global users_db
    users_db = [u for u in users_db if u.id != user_id]
    return {"message": "User deleted successfully"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("Starting FastAPI server...")
    print("Visit: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("ReDoc: http://localhost:8000/redoc")
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 5. Django Server

Django is a full-featured web framework for larger applications:

```python
# django_server.py
# This is a minimal Django setup in a single file

import os
import sys
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.http import JsonResponse, HttpResponse
from django.urls import path
from django.core.management import execute_from_command_line

# Configure Django settings
settings.configure(
    DEBUG=True,
    SECRET_KEY='your-secret-key-here',
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=['*'],
    MIDDLEWARE=[
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
    ],
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'django.contrib.auth',
    ],
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
)

# Views
def home(request):
    html = """
    <html>
    <head><title>Django Server</title></head>
    <body>
        <h1>Django Server Demo</h1>
        <p>This is a minimal Django server.</p>
        <ul>
            <li><a href="/api/users/">API Users</a></li>
            <li><a href="/health/">Health Check</a></li>
        </ul>
    </body>
    </html>
    """
    return HttpResponse(html)

def api_users(request):
    users = [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"}
    ]
    return JsonResponse({"users": users})

def health_check(request):
    return JsonResponse({"status": "healthy", "framework": "Django"})

# URL patterns
urlpatterns = [
    path('', home, name='home'),
    path('api/users/', api_users, name='api_users'),
    path('health/', health_check, name='health'),
]

# WSGI application
application = get_wsgi_application()

if __name__ == '__main__':
    print("Starting Django server...")
    print("Visit: http://localhost:8000")
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
```

## 6. Socket.IO Server

For real-time communication with WebSockets:

```python
# socketio_server.py
import socketio
import eventlet
from flask import Flask

# Create Flask app
app = Flask(__name__)

# Create Socket.IO server
sio = socketio.Server(cors_allowed_origins="*")
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

# Store connected clients
connected_clients = {}

@app.route('/')
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Socket.IO Server</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    </head>
    <body>
        <h1>Socket.IO Real-time Chat</h1>
        <div id="messages"></div>
        <input type="text" id="messageInput" placeholder="Type a message...">
        <button onclick="sendMessage()">Send</button>

        <script>
            const socket = io();

            socket.on('connect', function() {
                console.log('Connected to server');
                document.getElementById('messages').innerHTML += '<p>Connected to server</p>';
            });

            socket.on('message', function(data) {
                document.getElementById('messages').innerHTML +=
                    '<p><strong>' + data.user + ':</strong> ' + data.message + '</p>';
            });

            function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value;
                if (message) {
                    socket.emit('message', {message: message});
                    input.value = '';
                }
            }

            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    """
    return html

@sio.event
def connect(sid, environ):
    print(f'Client {sid} connected')
    connected_clients[sid] = {'id': sid}
    sio.emit('message', {
        'user': 'System',
        'message': f'User {sid[:8]} joined the chat'
    })

@sio.event
def disconnect(sid):
    print(f'Client {sid} disconnected')
    if sid in connected_clients:
        del connected_clients[sid]
    sio.emit('message', {
        'user': 'System',
        'message': f'User {sid[:8]} left the chat'
    })

@sio.event
def message(sid, data):
    print(f'Message from {sid}: {data}')
    sio.emit('message', {
        'user': sid[:8],
        'message': data['message']
    })

if __name__ == '__main__':
    print("Starting Socket.IO server...")
    print("Visit: http://localhost:5000")
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
```

## Installation Requirements

Create a `requirements.txt` file for the dependencies:

```txt
# requirements.txt
flask==2.3.3
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
django==4.2.7
python-socketio==5.10.0
eventlet==0.33.3
```

Install with:

```bash
pip install -r requirements.txt
```

## Running the Servers

1. **Basic HTTP Server**: `python simple_http_server.py`
2. **TCP Server**: `python tcp_server.py`
3. **Flask Server**: `python flask_server.py`
4. **FastAPI Server**: `python fastapi_server.py`
5. **Django Server**: `python django_server.py`
6. **Socket.IO Server**: `python socketio_server.py`

## Key Concepts

### HTTP vs TCP

- **HTTP**: Application layer protocol, stateless, request-response model
- **TCP**: Transport layer protocol, connection-oriented, persistent connections

### Synchronous vs Asynchronous

- **Synchronous**: Traditional blocking I/O (Flask, Django)
- **Asynchronous**: Non-blocking I/O (FastAPI with async/await)

### WSGI vs ASGI

- **WSGI**: Web Server Gateway Interface (Flask, Django)
- **ASGI**: Asynchronous Server Gateway Interface (FastAPI, modern Django)

### Production Deployment

For production, use proper WSGI/ASGI servers:

- **Gunicorn**: `gunicorn app:app`
- **Uvicorn**: `uvicorn app:app --host 0.0.0.0 --port 8000`
- **uWSGI**: `uwsgi --http :8000 --wsgi-file app.py`

## Best Practices

1. **Error Handling**: Always implement proper error handling
2. **Logging**: Use Python's logging module for debugging
3. **Security**: Implement authentication, HTTPS, input validation
4. **Configuration**: Use environment variables for settings
5. **Testing**: Write unit tests for your server endpoints
6. **Documentation**: Document your API endpoints
7. **Monitoring**: Implement health checks and metrics

This guide covers the fundamentals of creating servers in Python. Choose the approach that best fits your project requirements!
