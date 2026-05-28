from flask import Flask, redirect, request
import os
import requests

app = Flask(__name__)

CLIENT_ID=os.getenv("CLIENT_ID")
CLIENT_SECRET=os.getenv("CLIENT_SECRET")
REDIRECT_URI=os.getenv("REDIRECT_URI")

ACCESS_TOKEN=None


def headers():

    return {

        "Authorization":f"Bearer {ACCESS_TOKEN}"

    }


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

    buscar=request.args.get(

        "q",

        ""

    ).strip()

    html="""

    <h1>Buscador MercadoLibre</h1>

    <form>

    <input
    name='q'
    value='{}'
    placeholder='Buscar producto'
    style='width:300px;font-size:20px'
    >

    <button>

    Buscar

    </button>

    </form>

    <hr>

    """.format(buscar)

    if buscar=="":

        html+="Escribe algo para buscar"

        return html

    resultados=requests.get(

        "https://api.mercadolibre.com/sites/MLC/search",

        headers=headers(),

        params={

            "seller_id":"2397796502",

            "q":buscar,

            "limit":50

        }

    ).json()

    encontrados=resultados.get(

        "results",

        []

    )

    html+=f"""

    Coincidencias:

    {len(encontrados)}

    <hr>

    """

    for p in encontrados:

        itemid=p["id"]

        titulo=p["title"]

        stock=p.get(

            "available_quantity",

            0

        )

        estado=p.get(

            "status",

            ""

        )

        html+=f"""

        <b>{titulo}</b>

        <br>

        Stock: {stock}

        <br>

        Estado: {estado}

        <br>

        <form action='/stock/{itemid}' method='post'>

        <input
        type='number'
        name='stock'
        value='{stock}'
        style='width:70px'
        >

        <button>

        Cambiar Stock

        </button>

        </form>

        <br>

        <a href='/pause/{itemid}'>

        PAUSAR

        </a>

        |

        <a href='/activate/{itemid}'>

        ACTIVAR

        </a>

        <hr>

        """

    return html


@app.route("/stock/<itemid>",methods=["POST"])
def stock(itemid):

    nuevo=int(

        request.form["stock"]

    )

    requests.put(

        f"https://api.mercadolibre.com/items/{itemid}",

        headers=headers(),

        json={

            "available_quantity":nuevo

        }

    )

    return redirect("/")


@app.route("/pause/<itemid>")
def pause(itemid):

    requests.put(

        f"https://api.mercadolibre.com/items/{itemid}",

        headers=headers(),

        json={

            "status":"paused"

        }

    )

    return redirect("/")


@app.route("/activate/<itemid>")
def activate(itemid):

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

    return redirect(

        f"https://auth.mercadolibre.cl/authorization?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"

    )


@app.route("/callback")
def callback():

    global ACCESS_TOKEN

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

    )

    ACCESS_TOKEN=r.json()[

        "access_token"

    ]

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
