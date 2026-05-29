from flask import Flask, redirect, request
import os
import requests
import json

app = Flask(__name__)

CLIENT_ID=os.getenv("CLIENT_ID")
CLIENT_SECRET=os.getenv("CLIENT_SECRET")
REDIRECT_URI=os.getenv("REDIRECT_URI")

TOKEN_FILE="token.txt"


def guardar_token(data):

    with open(TOKEN_FILE,"w") as f:
        json.dump(data,f)


def cargar_token():

    if not os.path.exists(TOKEN_FILE):
        return None

    with open(TOKEN_FILE,"r") as f:
        return json.load(f)


def get_access_token():

    data=cargar_token()

    if not data:
        return None

    return data["access_token"]


@app.route("/")
def home():

    q=request.args.get("q","").strip()

    html="""
    <h1>Buscador MercadoLibre</h1>

    <form>

    <input name='q' value='{0}'>

    <button>Buscar</button>

    </form>

    <hr>
    """.format(q)

    if q=="":

        return html+"Escribe algo para buscar"

    access_token=get_access_token()

    if not access_token:

        return html+"<a href='/login'>LOGIN MERCADOLIBRE</a>"

    headers={
        "Authorization":f"Bearer {access_token}"
    }

    me=requests.get(
        "https://api.mercadolibre.com/users/me",
        headers=headers
    ).json()

    user_id=me["id"]

    search=requests.get(

        f"https://api.mercadolibre.com/users/{user_id}/items/search?limit=200",

        headers=headers

    ).json()

    ids=search.get("results",[])

    coincidencias=[]

    for item_id in ids:

        detalle=requests.get(

            f"https://api.mercadolibre.com/items/{item_id}",

            headers=headers

        ).json()

        titulo=detalle.get("title","")

        if q.lower() in titulo.lower():

            coincidencias.append(detalle)

    html+=f"<p>Coincidencias:{len(coincidencias)}</p><hr>"

    for item in coincidencias:

        item_id=item.get("id","")

        titulo=item.get("title","Sin titulo")

        stock=item.get("available_quantity",0)

        estado=item.get("status","")

        html+=f"""

        <h2>{titulo}</h2>

        Stock:{stock}<br>

        Estado:{estado}<br><br>

        <form action='/stock' method='post'>

        <input type='hidden' name='item_id' value='{item_id}'>

        <input name='stock' value='{stock}'>

        <button>Cambiar Stock</button>

        </form>

        <br>

        <a href='/pause/{item_id}'>PAUSAR</a>

        |

        <a href='/activate/{item_id}'>ACTIVAR</a>

        <hr>

        """

    return html


@app.route("/login")
def login():

    url=f"https://auth.mercadolibre.cl/authorization?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"

    return redirect(url)


@app.route("/callback")
def callback():

    code=request.args.get("code")

    response=requests.post(

        "https://api.mercadolibre.com/oauth/token",

        json={

            "grant_type":"authorization_code",
            "client_id":CLIENT_ID,
            "client_secret":CLIENT_SECRET,
            "code":code,
            "redirect_uri":REDIRECT_URI

        }

    ).json()

    guardar_token(response)

    return redirect("/")


@app.route("/pause/<item_id>")
def pause(item_id):

    token=get_access_token()

    headers={

        "Authorization":f"Bearer {token}"

    }

    requests.put(

        f"https://api.mercadolibre.com/items/{item_id}",

        headers=headers,

        json={

            "status":"paused"

        }

    )

    return redirect("/")


@app.route("/activate/<item_id>")
def activate(item_id):

    token=get_access_token()

    headers={

        "Authorization":f"Bearer {token}"

    }

    requests.put(

        f"https://api.mercadolibre.com/items/{item_id}",

        headers=headers,

        json={

            "status":"active"

        }

    )

    return redirect("/")


@app.route("/stock",methods=["POST"])
def stock():

    token=get_access_token()

    item_id=request.form["item_id"]

    stock=int(request.form["stock"])

    headers={

        "Authorization":f"Bearer {token}"

    }

    requests.put(

        f"https://api.mercadolibre.com/items/{item_id}",

        headers=headers,

        json={

            "available_quantity":stock

        }

    )

    return redirect("/")


if __name__=="__main__":

    app.run(

        host="0.0.0.0",

        port=int(os.environ.get("PORT",5000))

    )
