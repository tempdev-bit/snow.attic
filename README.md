# ❄️ snow.attic

  

A minimalist file server built in Python using Flask.

  

## 🔐 Features

  

- Password login (stored in .env)

- Upload, download, and delete files for anywhere in the world (NGROK)

- EXTREMELY simplistic

- Drag-and-drop web interface

- Optional public URL via ngrok

  

## ⚙️ Setup

  

```bash

git  clone  https://github.com/yourusername/snow-attic.git

cd  snow-attic

pip  install  -r  req.txt

```
  

### Create .env:

  

```

SNOW_USERNAME=(UsernameHere)

SNOW_PASSWORD=(PasswordHere)

NGROK_AUTHTOKEN=(TokenHere)

```

Directly replace the brackets and text. For eg:

  

```

SNOW_USERNAME=Snow

SNOW_PASSWORD=SuperSecurePassword12

NGROK_AUTHTOKEN=ExampleToken12345678

```
<sup> Get NGROK token from https://dashboard.ngrok.com/signup <sup>
  

### Run:

  

```

python3 server.py

```
Click on the link produced by NGROK

  

## GENERAL

  

- All files are saved in uploads/ on your local machine.
- Public Access (via ngrok)
- If NGROK_AUTHTOKEN is set, the server will print a public http URL you can share.

  
  

<center><sup>Built with ❤️ by Solar<sup>


