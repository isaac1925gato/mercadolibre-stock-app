from flask import Flask, redirect, request
import os
import requests

app = Flask(__name__)

CLIENT_ID=os.getenv("CLIENT_ID")
CLIENT_SECRET=os.getenv("CLIENT_SECRET")
REDIRECT_URI=os.getenv("REDIRECT_URI")

ACCESS_TOKEN=None
REFRESH_TOKEN=None

USER_ID=2397796502


def headers():

    return {

        "Authorization":f"Bearer {ACCESS_TOKEN}"

    }


def obtener_items():

    r=requests.get(

        f"https://api.mercadolibre.com/users/{USER_ID}/items/search",

        headers=headers(),

        params={

            "limit":200

        }

    ).json()

    return r.get(

        "results",

        []

    )


@app.route("/")

def home():

    global ACCESS_TOKEN

    if ACCESS_TOKEN is None:

        return """

        <h1>MercadoLibre Stock</h1>

        <a href='/login'>

        LOGIN MERCADOLIBRE

        </a>

        """

    buscar=request.args.get(

        "q",

        ""

    ).lower().strip()

    resultados=[]

    ids=obtener_items()

    for itemid in ids:

        item=requests.get(

            f"https://api.mercadolibre.com/items/{itemid}",

            headers=headers()

        ).json()

        titulo=item.get(

            "title",

            ""

        )

        if buscar=="" or buscar in titulo.lower():

            resultados.append(

                item

            )

    html=f"""

    <h1>Buscador MercadoLibre</h1>

    <form>

    <input
    name=q
    value="{buscar}"
    style="width:400px;font-size:30px;">

    <button>

    Buscar

    </button>

    </form>

    <hr>

    Coincidencias:{len(resultados)}

    <hr>

    """

    for item in resultados:

        itemid=item["id"]

        titulo=item["title"]

        stock=item.get(

            "available_quantity",

            0

        )

        estado=item.get(

            "status",

            ""

        )

        html+=f"""

        <h3>

        {titulo}

        </h3>

        Stock:{stock}<br>

        Estado:{estado}

        <br><br>

        <form action="/stock">

        <input
        type=hidden
        name=id
        value="{itemid}">

        <input
        name=stock
        value="{stock}"
        style="width:80px;">

        <button>

        Cambiar Stock

        </button>

        </form>

        <br>

        <a href="/pause?id={itemid}">

        PAUSAR

        </a>

        |

        <a href="/activate?id={itemid}">

        ACTIVAR

        </a>

        <hr>

        """

    return html


@app.route("/stock")

def stock():

    itemid=request.args.get(

        "id"

    )

    stock=request.args.get(

        "stock"

    )

    requests.put(

        f"https://api.mercadolibre.com/items/{itemid}",

        headers=headers(),

        json={

            "available_quantity":int(stock)

        }

    )

    return redirect("/")


@app.route("/pause")

def pause():

    itemid=request.args.get(

        "id"

    )

    requests.put(

        f"https://api.mercadolibre.com/items/{itemid}",

        headers=headers(),

        json={

            "status":"paused"

        }

    )

    return redirect("/")


@app.route("/activate")

def activate():

    itemid=request.args.get(

        "id"

    )

    requests.put(

        f"https://api.mercadolibre.com/items/{itemid}",

        headers=headers(),

        json={

            "status":"active"

        }

    )

    return redirect("/")


@app.route("/login")

def login():

    url=f"https://auth.mercadolibre.cl/authorization?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"

    return redirect(

        url

    )


@app.route("/callback")

def callback():

    global ACCESS_TOKEN

    global REFRESH_TOKEN

    code=request.args.get(

        "code"

    )

    r=requests.post(

        "https://api.mercadolibre.com/oauth/token",

        data={

            "grant_type":"authorization_code",

            "client_id":CLIENT_ID,

            "client_secret":CLIENT_SECRET,

            "code":code,

            "redirect_uri":REDIRECT_URI

        }

    ).json()

    ACCESS_TOKEN=r.get(

        "access_token"

    )

    REFRESH_TOKEN=r.get(

        "refresh_token"

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
