from flask import Flask, redirect, request
import os
import requests
import json

app = Flask(__name__)

CLIENT_ID=os.getenv("CLIENT_ID")
CLIENT_SECRET=os.getenv("CLIENT_SECRET")
REDIRECT_URI=os.getenv("REDIRECT_URI")

ACCESS_TOKEN=None
REFRESH_TOKEN=None


def guardar_tokens():

    data={

        "access_token":ACCESS_TOKEN,
        "refresh_token":REFRESH_TOKEN

    }

    with open("token.txt","w") as f:

        json.dump(data,f)


def cargar_tokens():

    global ACCESS_TOKEN
    global REFRESH_TOKEN

    try:

        with open("token.txt","r") as f:

            data=json.load(f)

            ACCESS_TOKEN=data.get("access_token")

            REFRESH_TOKEN=data.get("refresh_token")

    except:

        pass


def renovar_token():

    global ACCESS_TOKEN
    global REFRESH_TOKEN

    if REFRESH_TOKEN is None:

        return

    try:

        r=requests.post(

            "https://api.mercadolibre.com/oauth/token",

            data={

                "grant_type":"refresh_token",
                "client_id":CLIENT_ID,
                "client_secret":CLIENT_SECRET,
                "refresh_token":REFRESH_TOKEN

            }

        )

        if r.status_code!=200:

            return

        data=r.json()

        ACCESS_TOKEN=data.get(

            "access_token",
            ACCESS_TOKEN

        )

        REFRESH_TOKEN=data.get(

            "refresh_token",
            REFRESH_TOKEN

        )

        guardar_tokens()

    except:

        pass


cargar_tokens()


@app.route("/")

def home():

    q=request.args.get("q","").strip()

    html="""

<h1>Buscador MercadoLibre</h1>

<form>

<input name='q' value='%s'>

<button>Buscar</button>

</form>

<hr>

"""%q

    if q=="":

        html+="Escribe algo para buscar"

        return html

    renovar_token()

    headers={

        "Authorization":f"Bearer {ACCESS_TOKEN}"

    }

    r=requests.get(

        "https://api.mercadolibre.com/users/me",

        headers=headers

    )

    user=r.json()

    user_id=user["id"]

    publicaciones=[]

    offset=0

    limit=50

    while True:

        rr=requests.get(

            f"https://api.mercadolibre.com/users/{user_id}/items/search?limit={limit}&offset={offset}",

            headers=headers

        )

        data=rr.json()

        ids=data["results"]

        publicaciones.extend(ids)

        offset+=limit

        if len(ids)<limit:

            break

    coincidencias=[]

    q=q.lower()

    for item_id in publicaciones:

        rr=requests.get(

            f"https://api.mercadolibre.com/items/{item_id}",

            headers=headers

        )

        item=rr.json()

        titulo=item["title"]

        if q in titulo.lower():

            coincidencias.append(item)

    html+=f"Coincidencias:{len(coincidencias)}<hr>"

    for item in coincidencias:

        html+=f"""

<h2>{item['title']}</h2>

Stock:{item['available_quantity']}<br>

Estado:{item['status']}<br><br>

<form action='/stock' method='post'>

<input hidden name='id' value='{item["id"]}'>

<input name='stock'

value='{item["available_quantity"]}'>

<button>

Cambiar Stock

</button>

</form>

<br>

<a href='/pause?id={item["id"]}'>

PAUSAR

</a>

|

<a href='/activate?id={item["id"]}'>

ACTIVAR

</a>

<hr>

"""

    return html


@app.route("/login")

def login():

    url=f"https://auth.mercadolibre.cl/authorization?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"

    return redirect(url)


@app.route("/callback")

def callback():

    global ACCESS_TOKEN
    global REFRESH_TOKEN

    code=request.args.get("code")

    r=requests.post(

        "https://api.mercadolibre.com/oauth/token",

        data={

            "grant_type":"authorization_code",
            "client_id":CLIENT_ID,
            "client_secret":CLIENT_SECRET,
            "code":code,
            "redirect_uri":REDIRECT_URI

        }

    )

    data=r.json()

    ACCESS_TOKEN=data["access_token"]

    REFRESH_TOKEN=data["refresh_token"]

    guardar_tokens()

    return """

Conectado correctamente

<br><br>

<a href='/'>Ir inicio</a>

"""


@app.route("/pause")

def pause():

    renovar_token()

    item=request.args.get("id")

    headers={

        "Authorization":f"Bearer {ACCESS_TOKEN}"

    }

    requests.put(

        f"https://api.mercadolibre.com/items/{item}",

        headers=headers,

        json={

            "status":"paused"

        }

    )

    return redirect("/")


@app.route("/activate")

def activate():

    renovar_token()

    item=request.args.get("id")

    headers={

        "Authorization":f"Bearer {ACCESS_TOKEN}"

    }

    requests.put(

        f"https://api.mercadolibre.com/items/{item}",

        headers=headers,

        json={

            "status":"active"

        }

    )

    return redirect("/")


@app.route("/stock",methods=["POST"])

def stock():

    renovar_token()

    item=request.form["id"]

    cantidad=int(

        request.form["stock"]

    )

    headers={

        "Authorization":f"Bearer {ACCESS_TOKEN}"

    }

    requests.put(

        f"https://api.mercadolibre.com/items/{item}",

        headers=headers,

        json={

            "available_quantity":cantidad

        }

    )

    return redirect("/")


if __name__=="__main__":

    app.run(

        host="0.0.0.0",

        port=int(

            os.environ.get(

                "PORT",

                5000

            )

        )

    )
