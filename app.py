from flask import Flask, jsonify
from flask_cors import cross_origin, CORS


app = Flask(__name__)
CORS(app)


@cross_origin()
@app.route('/timeseries', methods=['GET', 'POST'])
def timeseries():
    data = {
        "dates": ["2017-08-09", "2017-09-08", "2017-10-11"],
        "line1": [50, 30, 60],
    }
    return jsonify(data)


@cross_origin()
@app.route('/linechart')
def linechart():
    data = {
        "line1": [1, 2, 5, 1],
        "line2": [23, 43, 12, 34],
    }
    return jsonify(data)


if __name__ == '__main__':
    app.run()

