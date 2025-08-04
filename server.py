import sys
import os
import subprocess
import uuid
import traceback

try:
    from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
    from flask_httpauth import HTTPBasicAuth
    from pyngrok.exception import PyngrokNgrokError
    from pyngrok import conf, process
    from werkzeug.security import generate_password_hash, check_password_hash
    from werkzeug.utils import secure_filename
    from dotenv import load_dotenv
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    from flask_talisman import Talisman
    from flask_wtf.csrf import CSRFProtect
    import magic
    import psutil
    import secrets

except ImportError as e:
    print("Failed to import modules: Import error: {e}")
    traceback.print_exc()
else:
    print(f"Imported all modules succesfully!")


#Try to import pyngrok for public access; PURELY OPTIONAL
try:
    from pyngrok import ngrok
    ngrok_enabled == True
    print(f"Web access module imported!")
except ImportError:
    ngrok = None
    ngrok_enabled = False
    print(f"Couldn't load ngrok; no web access")


#Load from .env
load_dotenv()


#Flask setup + CSRF setup + Upload cap
app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.config['DEBUG'] = False
# Secure headers (prevents clickjacking, sniffing, XSS)
Talisman(app, content_security_policy={
    'default-src': "'self'"
})
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'  # Or 'Strict'
)
csrf = CSRFProtect(app)
app.secret_key = os.getenv("SECRET_KEY")
limiter = Limiter(get_remote_address, app=app, default_limits=["1024/day", "64/minute"])
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB upload cap; temporary af


#Uploaded files destination
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#Allowed file extensions
ALLOWED_EXTENSIONS = {
    'txt', 
    'pdf', 
    'png', 
    'jpg', 
    'jpeg', 
    'gif', 
    'zip', 
    '7z',
    'rar',
    'mp3', 
    'wav', 
    'gif', 
    'pdf', 
    'mp4', 
    'mpv',
    'gba'
    }

#Kills any stupid previous ngrok sessions
def kill_existing_ngrok():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = proc.info.get('name', '').lower()
            cmdline = ' '.join(str(arg).lower() for arg in proc.info.get('cmdline', []))
            if 'ngrok' in name or 'ngrok' in cmdline:
                print(f"[Ngrok] Killing stale process (PID {proc.pid})")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

if ngrok_enabled == True:
    kill_existing_ngrok()

#Basic Auth setup
auth = HTTPBasicAuth()
user = {
    os.getenv("SNOW_USERNAME"):
    generate_password_hash(os.getenv("SNOW_PASSWORD"))
    }

# Load creds
USERNAME = os.getenv("SNOW_USERNAME")
PASSWORD = os.getenv("SNOW_PASSWORD")
if not USERNAME or not PASSWORD:
    raise EnvironmentError(" Missing SNOW_USERNAME or SNOW_PASSWORD in .env")


#Check user creds
@auth.verify_password
def verify_password(username, password):
    print(f"Authenticating user...")
    if username in user and check_password_hash(user[username], password):
        print(f"User authenticated!")
        return username
    else:
        print(f"User not authenticated!")
        return None


#Validate safe file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit( '.', 1)[1].lower() in ALLOWED_EXTENSIONS

#MIME CHECK ALERT
def allowed_filetype(file):
    mime = magic.from_buffer(file.read(2048), mime=True)
    file.seek(0)
    return mime in [
        'image/png',
        'image/jpeg',
        'application/pdf',
        'text/plain',
        'application/zip',
        'video/mp4',
        'audio/wav',
        'video/mpv',
        'video/x-matroska', #mpv and x-matroska both point to .mpv
        'application/octet-stream', #.gba, unknown binaries
        'application/x-rar-compressed',
        'application/vnd.rar', #vnd.rar and x-rar-compressed both point to .rar, but they can show up differently in different OS's
        'application/x-7z-compressed',
        'image/gif',
        'image/bmp',
        'application/x-msdownload',  # .exe
    ]


#Homepage
@app.route('/')
@auth.login_required
def index():
    files = sorted(os.listdir(app.config['UPLOAD_FOLDER']))
    return render_template('index.html', files=files)


#Upload
@app.route('/upload', methods=['POST'])
@auth.login_required
@limiter.limit("64/minute")
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file and allowed_file(file.filename) and allowed_filetype(file):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            filename = f"{uuid.uuid4().hex}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for('index'))


#Handle downloads
@app.route('/download/<filename>')
@auth.login_required
def download(filename):
    safe_name = secure_filename(filename)

    if not safe_name:
        print(f"[Download] Rejected: Empty or invalid filename")
        abort(400)  # Bad Request
    
    upload_dir = os.path.abspath(app.config['UPLOAD_FOLDER'])
    file_path = os.path.abspath(os.path.join(upload_dir, safe_name))
    print(f"[Download] Resolved path: {file_path}")

    # Block path traversal attempts
    if not file_path.startswith(upload_dir):
        print(f"[Download] Forbidden: Path outside upload dir")
        abort(403)

    if not os.path.exists(file_path):
        print(f"[Download] Not found: {file_path}")
        abort(404)
    return send_from_directory(upload_dir, safe_name, as_attachment=True)


#Handle Delete
@app.route('/delete/<filename>', methods=['POST'])
@auth.login_required
def delete(filename):
    safe_name = secure_filename(filename)
    path = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], safe_name))
    uploads_dir = os.path.abspath(app.config['UPLOAD_FOLDER'])

    if not path.startswith(uploads_dir):
        abort(403)

    if os.path.exists(path):
        os.remove(path)

    return redirect(url_for('index'))

#I hate Ngrok
#I wasted 1.5 hrs setting it up, and the names it generated are not efficient to tell
#It is still the easiest one there, sooooo enjoy Ngrok
if __name__ == '__main__':
    print(f"snow.attic running...")

    if ngrok:
        try:
            token = os.getenv("NGROK_AUTHTOKEN")
            if token:
                ngrok.set_auth_token(token)
                public_url = ngrok.connect(5000)
                print(f"🌍 Public URL: {public_url}")
            else:
                print("No NGROK_AUTHTOKEN in .env — skipping tunnel.")
        except Exception as e:
            print(f"Ngrok error: {e}")

    app.run(debug=False)


#TRIES to remove Ngrok headers
#This doesn't work if you type the domain out
#This is a jank implemetation only to remove the headers from 
#the device this script is running in
@app.after_request
def skip_ngrok_warning(response):
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response