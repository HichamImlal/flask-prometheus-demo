from flask import Flask, request
import pickle  # Vulnerable module (deserialization risk)
import os
import subprocess  # Command injection risk
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Hardcoded secret (for secrets scanning demo)
DB_PASSWORD = "admin123"

# Vulnerable route: Command injection
@app.route('/execute')
def execute():
    cmd = request.args.get('cmd')
    return subprocess.check_output(cmd, shell=True)  # UNSAFE!

# Vulnerable route: Insecure deserialization
@app.route('/deserialize')
def deserialize():
    data = request.args.get('data')
    return pickle.loads(data.encode())  # UNSAFE!

# Vulnerable route: Path traversal
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(f"/tmp/{filename}")  # No validation!
    return "File uploaded!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)