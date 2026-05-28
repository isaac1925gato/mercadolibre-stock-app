from flask import Flask, redirect, request
import os
import requests

app = Flask(__name__)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

@app.route("/")

def home():

    return """
    <h1>MercadoLibre Stock</h1>

    <a href='/login'>
    LOGIN MERCADOLIBRE
    </a>
    """

@app.route("/login")

def login():

    url=f"https://auth.mercadolibre.cl/authorization?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"

    return redirect(url)

@app.route("/callback")

def callback():

    code=request.args.get("code")

    return f"Codigo recibido correctamente:<br><br>{code}"

if __name__=="__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT",5000))
    )
