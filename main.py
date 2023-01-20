from flask import Flask, request, send_file
from flask_cors import CORS
from getter import getCSV
import os


app = Flask(__name__)
CORS(app)


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
