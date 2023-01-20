from flask import Flask, request, send_file
from flask_cors import CORS
from getter import getCSV
import os


app = Flask(__name__)
CORS(app)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response


@app.route("/csv")
def returnCSV():
    try:
        username = request.args.get("username")
        password = request.args.get("password")
        responseFromMain = getCSV(str(username), str(password))
        return responseFromMain[0]
    except:
        return


@app.route("/download")
def downloadFile():
    try:
        username = request.args.get("username")
        password = request.args.get("password")
        responseFromMain = getCSV(str(username), str(password))
        filename = responseFromMain[1]+".csv"

        return send_file("C:\\GitHubRepos\\ScheduleExporterWebApp\\flask-server\output\\"+filename, as_attachment=True)
    except:
        return


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
