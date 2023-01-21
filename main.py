from flask import Flask, request, send_file
from flask_cors import CORS
from getter import getCSV
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, asymmetric
import os


# generate private key
private_key = asymmetric.rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)


# generate public key
public_key = private_key.public_key()

# convert private key to pem format
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)


# convert public key to pem format
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)


app = Flask(__name__)
CORS(app)


@app.route('/public_key', methods=['GET'])
def get_public_key():
    return public_pem


@app.route("/csv")
def returnCSV():
    try:
        username = request.args.get("username")
        password = request.args.get("password")
        responseFromMain = getCSV(str(username), str(password))
        return responseFromMain[0]
    except Exception as e:
        print(e)
        return "An error occurred while retrieving the schedule"


@app.route("/download")
def downloadFile():
    try:
        username = request.args.get("username")
        password = request.args.get("password")
        responseFromMain = getCSV(str(username), str(password))
        filename = responseFromMain[1]+".csv"

        filecontents = responseFromMain[0]
        f = open(filename, "w")
        f.write(filecontents)
        f.close()

        print(filename)

        return send_file(filename, as_attachment=True)
    except Exception as e:
        print(e)
        return "An error occurred while downloading the schedule"


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
