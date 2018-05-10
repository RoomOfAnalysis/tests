from flask import Flask, request, after_this_request, g
import os
import pytz
from tzlocal import get_localzone


app = Flask(__name__)
app.secret_key = os.urandom(16)

local_tz = get_localzone()


@app.before_request
def detect_user_timzone():
    tz = request.cookies.get('user_tz')

    if tz is None:
        tz = str(local_tz)
        # print(tz)

        @after_this_request
        def remeber_timezone(response):
            response.set_cookie('user_tz', tz)
            return response
    g.timezone = tz

@app.route('/', methods=['GET', 'POST'])
def index():
    tz = request.cookies.get('user_tz')
    # print(tz)
    print(g.timezone)
    return 'Hello!'


if __name__ == '__main__':
    app.run(debug=True)

