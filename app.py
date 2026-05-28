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

    encontrados=[]

    if buscar!="":

        resultados=requests.get(

            f"https://api.mercadolibre.com/users/{USER_ID}/items/search",

            headers=headers(),

            params={

                "limit":200

            }

        ).json()

        ids=resultados.get(

            "results",

            []

        )

        for itemid in ids:

            item=requests.get(

                f"https://api.mercadolibre.com/items/{itemid}",

                headers=headers()

            ).json()

            titulo=item.get(

                "title",

                ""

            )

            if buscar in titulo.lower():

                encontrados.append(

                    item

                )

    html=f"""

    <h1>Buscador MercadoLibre</h1>

    <form>

    <input
    name='q'
    value='{buscar}'
    style='width:350px;font-size:30px;'>

    <button>

    Buscar

    </button>

    </form>

    <hr>

    Coincidencias: {len(encontrados)}

    <hr>

    """

    for item in encontrados:

        html+=f"""

        <h3>

        {item['title']}

        </h3>

        Stock: {item.get('available_quantity',0)}

        <hr>

        """

    return html


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
