from flask import Flask, request, send_file
from flask_cors import CORS
from getter import getCSV
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, asymmetric, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import os
import csv
from io import StringIO
from datetime import datetime


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

        # Decode the base64 encoded username and password
        decoded_username = base64.b64decode(username)
        decoded_password = base64.b64decode(password)

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
        # The decrypted credentials are in "binary string"

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

        # Decode the base64 encoded username and password
        decoded_username = base64.b64decode(username)
        decoded_password = base64.b64decode(password)

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

        # The decrypted credentials are in "binary string"

        responseFromMain = getCSV(
            decrypted_username.decode('ascii'), decrypted_password.decode('ascii'))

        filename = responseFromMain[1]+".csv"

        filecontents = responseFromMain[0]
        f = open(filename, "w")
        f.write(filecontents)
        f.close()

        return send_file(filename, as_attachment=True)
    except Exception as e:
        print(e)
        return "An error occurred while downloading the schedule"


@app.route("/calendarview")
def calenderView():

    username = request.args.get("username")
    password = request.args.get("password")

    # Decode the base64 encoded username and password
    decoded_username = base64.b64decode(username)
    decoded_password = base64.b64decode(password)

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
    # The decrypted credentials are in "binary string"

    responseFromMain = getCSV(
        decrypted_username.decode('ascii'), decrypted_password.decode('ascii'))

    csvString = responseFromMain[0]

    file = StringIO(csvString)

    # Use the DictReader class to read the contents of the file
    reader = csv.DictReader(file)

    # Initialize an empty list to store the events
    events = []

    # Iterate over each row in the CSV file
    for row in reader:
        # Create a datetime object for the start and end time
        start_time = datetime.strptime(
            row['Start Date'] + " " + row['Start Time'], '%Y-%m-%d %I:%M %p')
        end_time = datetime.strptime(
            row['End Date'] + " " + row['End Time'], '%Y-%m-%d %I:%M %p')
        # Create a dictionary to represent the event
        event = {
            'title': row['Subject'],
            'start': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'description': row['Location']
        }
        # Append the event to the list of events
        events.append(event)

    return (events)

# The 'events' variable now contains the list of events in the desired format


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
