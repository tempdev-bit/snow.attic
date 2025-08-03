try:
    import sys
    from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
    from flask_httpauth import HTTPBasicAuth
    from werkzeug.security import generate_password_hash, check_password_hash
    from werkzeug.utils import secure_filename
    from dotenv import load_dotenv
    import os
except ImportError as e:
    print("Test 1 failed: Import error: {e}")
    import traceback
    traceback.print_exc()
else:
    print(f"Passed Test 1!")

#Try to import pyngrok for public access; PURELY OPTIONAL
try:
    from pyngrok import ngrok
    print(f"Pyngrok Imported!")
except ImportError:
    ngrok = None
    print(f"Couldn't load ngrok; no web access")

#Load from .env
load_dotenv()

#Flask setup
app = Flask(__name__)

#Uploaded files destination
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'mp3', 'mp4', 'gba'}

#Basic Auth setup
auth = HTTPBasicAuth()
user = {
    os.getenv("SNOW_USERNAME"):
    generate_password_hash(os.getenv("SNOW_PASSWORD"))
    }

#Check user creds
@auth.verify_password
def verify_password(username, password):
    print(f"Authenticating user...")
    if username in users and check_password_hash(users[username], password):
        return username
        print(f"User authenticated!")

#Validate safe file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit( '.', 1)[1].lower in ALLOWED_EXTENSIONS

#Homepage
@app.route('/')
@auth.login_required
def index():
    files = sorted(os.listdir(app.config['UPLOAD_FOLDER']))
    return render_template('index.html', files=files) #TODO - index.html

#Handle downloads
@app.route('/download/<filename>')
@auth.login_required
def download(filename):
    safe_name = secure_filename(filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(path):
        print(f"Error")
        abort(404)
    return send_from_directory(app.config['UPLOAD_FOLDER'], safe_name, as_attachment=True)

#Handle Delete
@app.route('/delete/<filename>', methods=['POST'])
@auth.login_required
def delete(filename):
    safe_name = secure_filename(filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    if os.path.exists(path):
        os.remove(path)
    return redirect(url_for('index'))
