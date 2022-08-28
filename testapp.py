from flask import Flask, request


# Simple Flask app that just prints the requests
app = Flask(__name__)

# Route that prints request info
@app.route("/testroute")
def index():
    print("Request:")
    print("  Method: {}".format(request.method))
    print("  Path: {}".format(request.path))
    print("  Headers: {}".format(request.headers))
    print("  Body: {}".format(request.get_data()))
    return "OK"

# Run the app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
