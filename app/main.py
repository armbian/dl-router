from flask import (
        Flask,
        redirect,
        request
)
# from markupsafe import escape
from mirror_list import Mirror

all_mirrors = ["http://mirrors.netix.net/armbian/apt/",
               "https://mirrors.dotsrc.org/armbian-apt/"]

mirror = Mirror(all_mirrors)


app = Flask(__name__)


def get_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']


def get_redirect(path, IP):
    if path == '':
        return mirror.next()
    else:
        return "{}{}".format(mirror.next(), path)


@app.route('/status')
def status():
    return "OK"


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return redirect(get_redirect(path, get_ip()), 302)


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=False, port=80)
