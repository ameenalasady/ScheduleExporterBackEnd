from flask import Flask, request, send_file
from flask_cors import CORS
from getter import getCSV
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, asymmetric, hashes
from cryptography.hazmat.primitives.asymmetric import padding
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

        print(str(username), str(password))

        # Decode the base64 encoded username and password
        decoded_username = base64.b64decode(username)
        decoded_password = base64.b64decode(password)

        print(str(decoded_username), str(decoded_password))

        # Decrypt the username and password
        decrypted_username = private_key.decrypt(
            decoded_username,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        decrypted_password = private_key.decrypt(
            decoded_password,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        print(decrypted_username.decode('ascii'),
              decrypted_password.decode('ascii'))

        responseFromMain = getCSV(
            decrypted_username.decode('ascii'), decrypted_password.decode('ascii'))
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
