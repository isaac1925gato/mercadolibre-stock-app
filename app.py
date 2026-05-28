from flask import Flask, redirect, request
import os
import requests

app = Flask(__name__)

CLIENT_ID=os.getenv("CLIENT_ID")
CLIENT_SECRET=os.getenv("CLIENT_SECRET")
REDIRECT_URI=os.getenv("REDIRECT_URI")

ACCESS_TOKEN=None


@app.route("/")
def home():

    global ACCESS_TOKEN

    if not ACCESS_TOKEN:

        return """

        <h1>MercadoLibre Stock</h1>

        <a href='/login'>

        LOGIN MERCADOLIBRE

        </a>

        """

    headers={

        "Authorization":f"Bearer {ACCESS_TOKEN}"

    }

    me=requests.get(

        "https://api.mercadolibre.com/users/me",

        headers=headers

    ).json()

    user_id=me["id"]

    items=requests.get(

        f"https://api.mercadolibre.com/users/{user_id}/items/search",

        headers=headers

    ).json()

    publicaciones=items["results"]

    html="<h1>Mis publicaciones</h1>"

    html+="<br>Total:"+str(len(publicaciones))

    html+="<hr>"

    for item in publicaciones[:100]:

        producto=requests.get(

            f"https://api.mercadolibre.com/items/{item}",

            headers=headers

        ).json()

        titulo=producto["title"]

        stock=producto["available_quantity"]

        html+=f"""

        <b>{titulo}</b>

        <br>

        Stock: {stock}

        <br><br>

        """

    return html


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
