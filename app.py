from flask import Flask, request, jsonify
import pickle  # Vulnerable module (deserialization risk)
import os
import subprocess  # Command injection risk
from werkzeug.utils import secure_filename
from prometheus_client import make_wsgi_app, Counter
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)

# Hardcoded secret (for secrets scanning demo)
DB_PASSWORD = "admin123"

# Prometheus metrics
REQUEST_COUNT = Counter('flask_http_request_total', 'Total HTTP Requests')

# Health check (required for tests)
@app.route('/')
def health_check():
    REQUEST_COUNT.inc()
    return jsonify({"status": "OK"}), 200

# Prometheus metrics endpoint (required for tests)
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

# --- VULNERABLE ROUTES (KEPT FOR DEMO) ---
@app.route('/execute')
def execute():
    cmd = request.args.get('cmd')
    return subprocess.check_output(cmd, shell=True)  # UNSAFE!

@app.route('/deserialize')
def deserialize():
    data = request.args.get('data')
    return pickle.loads(data.encode())  # UNSAFE!

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(f"/tmp/{filename}")  # No validation!
    return "File uploaded!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)