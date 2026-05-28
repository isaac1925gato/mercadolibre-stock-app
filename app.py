from flask import Flask, redirect, request
import os
import requests

app = Flask(__name__)

CLIENT_ID=os.getenv("CLIENT_ID")
CLIENT_SECRET=os.getenv("CLIENT_SECRET")
REDIRECT_URI=os.getenv("REDIRECT_URI")

ACCESS_TOKEN=None

MAX_ITEMS=200


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

    buscar=request.args.get("q","").lower()

    me=requests.get(

        "https://api.mercadolibre.com/users/me",

        headers=headers()

    ).json()

    user_id=me["id"]

    publicaciones=[]

    offset=0

    while len(publicaciones)<MAX_ITEMS:

        data=requests.get(

            f"https://api.mercadolibre.com/users/{user_id}/items/search?limit=50&offset={offset}",

            headers=headers()

        ).json()

        lote=data.get("results",[])

        if not lote:

            break

        publicaciones.extend(lote)

        offset+=50

    publicaciones=publicaciones[:MAX_ITEMS]

    html=f"""

    <h1>Mis publicaciones</h1>

    Total:{len(publicaciones)}

    <br><br>

    <form>

    Buscar:

    <input name='q' value='{buscar}'>

    <button>

    Buscar

    </button>

    </form>

    <hr>

    """

    encontrados=0

    for item in publicaciones:

        p=requests.get(

            f"https://api.mercadolibre.com/items/{item}",

            headers=headers()

        ).json()

        titulo=p.get("title","")

        if buscar:

            if buscar not in titulo.lower():

                continue

        encontrados+=1

        stock=p.get("available_quantity",0)

        estado=p.get("status","")

        html+=f"""

        <b>{titulo}</b>

        <br>

        Stock:{stock}

        <br>

        Estado:{estado}

        <br>

        <form action='/stock/{item}' method='post'>

        Nuevo stock:

        <input
        type='number'
        name='stock'
        value='{stock}'
        style='width:70px'
        >

        <button>

        Actualizar Stock

        </button>

        </form>

        <br>

        <a href='/pause/{item}'>PAUSAR</a>

        |

        <a href='/activate/{item}'>ACTIVAR</a>

        <hr>

        """

    html+="Mostrando:"+str(encontrados)

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

    ACCESS_TOKEN=r.json()["access_token"]

    return redirect("/")


if __name__=="__main__":

    app.run(

        host="0.0.0.0",

        port=int(os.environ.get("PORT",5000))

    )
