try:
    import sys
    from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
    from flask_httpauth import HTTPBasicAuth
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
except ImportError:
    ngrok = None
    print(f"Couldn't load ngrok; no web access")