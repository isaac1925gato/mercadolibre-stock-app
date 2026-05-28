from flask import Flask, redirect, request
import os
import requests

app = Flask(__name__)

CLIENT_ID=os.getenv("CLIENT_ID")
CLIENT_SECRET=os.getenv("CLIENT_SECRET")
REDIRECT_URI=os.getenv("REDIRECT_URI")

TOKEN_FILE="token.txt"

ACCESS_TOKEN=None
REFRESH_TOKEN=None

USER_ID=2397796502


def guardar_tokens():

    global ACCESS_TOKEN
    global REFRESH_TOKEN

    with open(

        TOKEN_FILE,

        "w"

    ) as f:

        f.write(

            ACCESS_TOKEN+"\n"+REFRESH_TOKEN

        )


def cargar_tokens():

    global ACCESS_TOKEN
    global REFRESH_TOKEN

    try:

        with open(

            TOKEN_FILE,

            "r"

        ) as f:

            datos=f.read().splitlines()

            ACCESS_TOKEN=datos[0]

            REFRESH_TOKEN=datos[1]

    except:

        pass


def renovar_token():

    global ACCESS_TOKEN
    global REFRESH_TOKEN

    if REFRESH_TOKEN is None:

        return

    r=requests.post(

        "https://api.mercadolibre.com/oauth/token",

        data={

            "grant_type":"refresh_token",

            "client_id":CLIENT_ID,

            "client_secret":CLIENT_SECRET,

            "refresh_token":REFRESH_TOKEN

        }

    )

    if r.status_code==200:

        data=r.json()

        ACCESS_TOKEN=data["access_token"]

        REFRESH_TOKEN=data["refresh_token"]

        guardar_tokens()


def headers():

    renovar_token()

    return {

        "Authorization":

        f"Bearer {ACCESS_TOKEN}"

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


cargar_tokens()


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

    ).strip().lower()

    html="""

    <h1>Buscador MercadoLibre</h1>

    <form>

    <input
    name=q
    style='width:400px;font-size:30px;'>

    <button>

    Buscar

    </button>

    </form>

    <hr>

    """

    if buscar=="":

        html+="Escribe algo para buscar"

        return html

    resultados=[]

    ids=obtener_items()

    for itemid in ids:

        item=requests.get(

            f"https://api.mercadolibre.com/items/{itemid}",

            headers=headers()

        ).json()

        if buscar in item["title"].lower():

            resultados.append(

                item

            )

    html+=f"Coincidencias:{len(resultados)}<hr>"

    for item in resultados:

        itemid=item["id"]

        html+=f"""

        <h3>{item['title']}</h3>

        Stock:{item.get('available_quantity',0)}

        <br>

        Estado:{item.get('status','')}

        <br><br>

        <form action='/stock'>

        <input type=hidden name=id value='{itemid}'>

        <input
        name=stock
        value='{item.get("available_quantity",0)}'>

        <button>

        Cambiar Stock

        </button>

        </form>

        <br>

        <a href='/pause?id={itemid}'>

        PAUSAR

        </a>

        |

        <a href='/activate?id={itemid}'>

        ACTIVAR

        </a>

        <hr>

        """

    return html


@app.route("/stock")

def stock():

    requests.put(

        f"https://api.mercadolibre.com/items/{request.args.get('id')}",

        headers=headers(),

        json={

            "available_quantity":

            int(

                request.args.get(

                    "stock"

                )

            )

        }

    )

    return redirect("/")


@app.route("/pause")

def pause():

    requests.put(

        f"https://api.mercadolibre.com/items/{request.args.get('id')}",

        headers=headers(),

        json={

            "status":"paused"

        }

    )

    return redirect("/")


@app.route("/activate")

def activate():

    requests.put(

        f"https://api.mercadolibre.com/items/{request.args.get('id')}",

        headers=headers(),

        json={

            "status":"active"

        }

    )

    return redirect("/")


@app.route("/login")

def login():

    url=f"https://auth.mercadolibre.cl/authorization?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"

    return redirect(url)


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

    ACCESS_TOKEN=r["access_token"]

    REFRESH_TOKEN=r["refresh_token"]

    guardar_tokens()

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
