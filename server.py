try:
    import sys
    from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
    from flask_httpauth import HTTPBasicAuth
    from pyngrok.exception import PyngrokNgrokError
    from pyngrok import conf, process
    from werkzeug.security import generate_password_hash, check_password_hash
    from werkzeug.utils import secure_filename
    from dotenv import load_dotenv
    import os
    import subprocess
except ImportError as e:
    print("Test 1 failed: Import error: {e}")
    import traceback
    traceback.print_exc()
else:
    print(f"Imported all modules succesfully!")

#Try to import pyngrok for public access; PURELY OPTIONAL
try:
    from pyngrok import ngrok
    print(f"Web access module imported!")
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
    if username in user and check_password_hash(user[username], password):
        print(f"User authenticated!")
        return username
    else:
        print(f"User not authenticated! (Wrong username or password)")
        return None

#Validate safe file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit( '.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Homepage
@app.route('/')
@auth.login_required
def index():
    files = sorted(os.listdir(app.config['UPLOAD_FOLDER']))
    return render_template('index.html', files=files)

#Upload
@app.route('/upload', methods=['POST'])
@auth.login_required
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for('index'))

#Handle downloads
@app.route('/download/<filename>')
@auth.login_required
def download(filename):
    safe_name = secure_filename(filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(path):
        print(f"Error")
        abort(404)
        print(f"Downloading... {safe_name}")
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