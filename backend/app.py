from flask import Flask
from flask import Flask, request, jsonify, send_file, Response, stream_with_context
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Adjust the origin to your React app's URL
cors = CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST", "OPTIONS"])
app.app_context().push()

@app.route("/", methods=["get"])
def welcome():
    return "welcome"