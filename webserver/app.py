from flask import Flask, render_template, request, redirect, session, Response
from werkzeug.routing import BaseConverter
import requests

app = Flask(__name__)
app.secret_key = "very-secret"

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
@app.route("/_dash<regex('.*'):dash_path>")
@app.route("/_dash<regex('.*'):dash_path>/<path:path>")
def dash_proxy(*args, **kwargs):
    return "OK\n"


#  Match any route like /proxy/foo/bar or just /proxy
@app.route("/proxy")
@app.route("/proxy/<path:path>")
def proxy(*args, **kwargs):
    """
    Remove o prefixo /proxy/ da URL e repassa a requisição para o servidor de destino.
    """
    print("Request URL", request.url)
    print("Host URL", request.host_url)
    print("New URL", request.url.replace(request.host_url, "http://localhost:5000/"))
    print("Clean URL", request.url.replace(f"{request.host_url}proxy", 'http://localhost:5000'))
    # new_url = request.url.replace(f"{request.host_url}/proxy", 'http://localhost:5000/')
    # print("New URL", new_url)
    # print("yo")
    resp = requests.request(
        method=request.method,
        # Transforma, por exemplo: http://localhost:5005/proxy/foo/bar em http://localhost:5000/foo/bar
        # url=request.url.replace(f"{request.host_url}proxy", 'http://dash-dashboard:5000'),
        url=request.url.replace(f"{request.host_url}proxy", 'http://localhost:5000'),
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
