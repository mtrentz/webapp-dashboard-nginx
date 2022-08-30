from flask import Flask, render_template, request, redirect, session, Response
from werkzeug.routing import BaseConverter
import requests

app = Flask(__name__)
app.secret_key = "very-secret"
app.config.update(
    SESSION_COOKIE_SAMESITE=None,
)

username = "admin"
password = "admin"


@app.route("/")
def home():
    if "user" in session:
        user = session["user"]
        return render_template("home.html", username=user)
    else:
        return redirect("/login")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/auth", methods=["POST"])
def auth():
    if request.form["username"] == username and request.form["password"] == password:
        session["user"] = username
        return redirect("/")
    else:
        return redirect("/login")


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app.url_map.converters['regex'] = RegexConverter

# Regex converter to route a path that
# starts with /_dash
@app.route("/_dash<regex('.*'):dash_path>", methods=["GET", "POST"])
@app.route("/_dash<regex('.*'):dash_path>/<path:path>", methods=["GET", "POST"])
def dash_proxy(*args, **kwargs):
    if "user" not in session:
        # Return a msg with error
        return Response("Unauthorized", status=401)

    resp = requests.request(
        method=request.method,
        url=request.url.replace(request.host_url, 'http://dash-dashboard:8050/'),
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    return response


#  Match any route like /proxy/foo/bar or just /proxy
@app.route("/proxy", methods=["GET", "POST"])
@app.route("/proxy/<path:path>", methods=["GET", "POST"])
def proxy(*args, **kwargs):
    """
    Remove o prefixo /proxy/ da URL e repassa a requisição para o servidor de destino.
    """
    if "user" not in session:
        # Return a msg with errorsim
        return Response("Unauthorized", status=401)

    resp = requests.request(
        method=request.method,
        url=request.url.replace(f"{request.host_url}proxy", 'http://dash-dashboard:8050'),
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    return response



app.run(debug=True, host="0.0.0.0", port=5005)
