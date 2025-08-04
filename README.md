# ❄️ snow.attic v1.1

A minimalist file server built in Python using Flask.

![snow.attic demo](image.png)

## 🔐 Features

### 🔐 Security Features

#### ✅ CSRF Protection
- Enabled using `flask-wtf`- `CSRFProtect`.

#### ✅ Secure HTTP Headers
- Enforced via `Flask-Talisman`.
- CSP (Content Security Policy) set to `'self'`.
- Sets:
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `X-XSS-Protection: 1; mode=block`
  - Secure cookies (`Secure`, `HttpOnly`, `SameSite=Lax`)

#### ✅ MIME Type Validation
- Uses `python-magic` to inspect the **actual MIME type** of uploaded files (not just extensions).
- Rejects unsafe or unsupported MIME types.

#### ✅ Path Traversal Protection
- File paths are sanitized using `secure_filename` and `os.path.abspath`.
- Rejects requests where resolved path is outside the uploads directory.

#### ✅ CSRF-Resistant Deletion
- File deletions are Post-only and CSRF-protected.

#### ✅ Upload Size Limit
- Max upload limit: **2 GB** (`MAX_CONTENT_LENGTH`).

---

### 🔒 Authentication

#### ✅ Basic Authentication with Flask-HTTPAuth
- Authentication is handled using `Flask-HTTPAuth`
- User credentials are securely hashed using `Werkzeug` - `generate_password_hash`.
- Credentials are loaded from environment variables for security
- The `.env` file is used in conjunction with `python-dotenv` to avoid hardcoding sensitive data.

#### 🔐 Password Verification
- Incoming login attempts are validated with `check_password_hash`.
- All login events (successful or failed) are logged to the console for visibility.

#### ✅ Access Control Enforcement
- **Every critical route** is protected with `@auth.login_required`, ensuring that no unauthenticated access is allowed:
  - `/` – File listing homepage.
  - `/upload` – Handles secure file uploads.
  - `/download/<filename>` – Serves downloads with path sanitization.
  - `/delete/<filename>` – Deletes uploaded files via POST request.
- Any request without valid credentials receives a `401 Unauthorized` response.

#### 🔐 Environment-Based Secrets
- Secrets are externalized to the environment:
  ```env
  SNOW_USERNAME=your_username
  SNOW_PASSWORD=your_password
  ```
---

### 📁 File Upload & Management

#### ✅ Uploads
- Validates:
  - File extension (`ALLOWED_EXTENSIONS`)
  - MIME type via `magic.from_buffer`
- Prevents filename collisions via UUID prefixing.
- Stores files in `uploads/` (auto-created if missing).

#### ✅ Downloads
- Serves files securely with `send_from_directory`.
- Prevents path traversal and serves only if file exists.

#### ✅ Deletion
- Files can be deleted only via authenticated POST request.
- Filename is sanitized and deletion path verified.

---

### 🛡️ Rate Limiting

- Uses `Flask-Limiter` to throttle abuse:
  - **64 requests / minute**
  - **1024 requests / day**
- Applied globally and to `/upload`.

---

### 🌍 Public Access via Ngrok (Optional)

#### ✅ Ngrok Tunneling (Optional)
- If `NGROK_AUTHTOKEN` is present in `.env`, opens public URL via ngrok.
- Auto-kills any stale ngrok processes using `psutil`.
- Prints generated public URL on startup.
- Sets custom response header to avoid ngrok browser warnings:
  - `ngrok-skip-browser-warning: true`

#### ❌ Notes on Ngrok
- Not required for local usage.
- Adds convenience for temporary web access.
- Ngrok usage can be disabled by omitting its import or token.

---

## ⚙️ Setup

### Should Work On:

    Ubuntu/Debian based distro (via apt)

    Fedora/RHEL based distro (via dnf)

    Arch Linux based distro (via pacman)

### Setup Guide:

Get NGROK token from https://dashboard.ngrok.com/signup

```bash
wget https://github.com/tempdev-bit/snow.attic/archive/refs/heads/main.zip -O snow-attic.zip
unzip snow-attic.zip
cd snow.attic-main
chmod +x setup_script.sh
./setup_script.sh
```
  
After running setup_script it will automaticallly ask you if you want to run the server.
If you want to run it later:

```
cd snow.attic-main
source venv/bin/activate
python3 server.py
```

Click on the link produced by NGROK

## General
This is a 'permanent' server; i.e. once you 'upload' the files (/uploads), they will stay there and creating a new server later will still show the files.
  

<p align=center><sup>Built with ❤️ by Solar<sup><p align=center>

