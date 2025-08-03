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

if __name__ == '__main__':
    print(f"snow.attic running on http://127.0.0.1:500")

if ngrok:
    try:
        token = os.getenv("NGROK_AUTHTOKEN")
        if not token:
            print("Ngrok token not found in .env")
            return

        ngrok.set_auth_token(token)

        # Close existing tunnels
        for tunnel in ngrok.get_tunnels():
            print(f"Closing existing tunnel: {tunnel.public_url}")
            ngrok.disconnect(tunnel.public_url)

        # Open new tunnel
        public_url = ngrok.connect(5000)
        print(f"Public URL for access from anywhere: {public_url}")

    except Exception as e:
        print(f"Ngrok error: {e}")


app.run(debug=True)
