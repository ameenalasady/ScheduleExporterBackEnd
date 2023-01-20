from flask import Flask, request, send_file
from getter import getCSV
import os


app = Flask(__name__)


@app.route("/csv")
def returnCSV():
    username = request.args.get("username")
    password = request.args.get("password")
    print(username, password)
    responseFromMain = getCSV(str(username), str(password))
    return responseFromMain[0]


@app.route("/download")
def downloadFile():
    username = request.args.get("username")
    password = request.args.get("password")
    print(username, password)
    responseFromMain = getCSV(str(username), str(password))
    filename = responseFromMain[1]+".csv"

    return send_file("C:\\GitHubRepos\\ScheduleExporterWebApp\\flask-server\output\\"+filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
