from flask import Flask, redirect, request
import os
import requests

app = Flask(__name__)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

ACCESS_TOKEN = None

@app.route("/")
def home():

    global ACCESS_TOKEN

    if ACCESS_TOKEN:

        headers={
            "Authorization":f"Bearer {ACCESS_TOKEN}"
        }

        url="https://api.mercadolibre.com/users/me"

        data=requests.get(
            url,
            headers=headers
        ).json()

        return f"""
        <h1>Conectado</h1>

        Usuario:

        <br><br>

        {data}
        """

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

    global ACCESS_TOKEN

    code=request.args.get("code")

    response=requests.post(

        "https://api.mercadolibre.com/oauth/token",

        data={

            "grant_type":"authorization_code",

            "client_id":CLIENT_ID,

            "client_secret":CLIENT_SECRET,

            "code":code,

            "redirect_uri":REDIRECT_URI

        }

    )

    data=response.json()

    ACCESS_TOKEN=data["access_token"]

    return redirect("/")


if __name__=="__main__":

    app.run(

        host="0.0.0.0",

        port=int(os.environ.get("PORT",5000))

    )
