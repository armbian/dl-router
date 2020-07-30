from flask import (
        Flask,
        redirect,
        request
)
# from markupsafe import escape
from download_image_map import Parser
from mirror_list import Mirror


def load_mirrors():
    with open('mirrors.conf', 'r') as f:
        all_mirrors = f.read().splitlines()
        return all_mirrors


def get_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']


def get_redirect(path, IP):
    split_path = path.split('/')
    if len(split_path) == 2:
        key = "{}/{}".format(split_path[0], split_path[1])
        new_path = dl_map.get(key, path)
        return "{}{}".format(mirror.next(), new_path)
    if path == '':
        return mirror.next()
    else:
        print("path: {}".format(path))
        return "{}{}".format(mirror.next(), path)


mirror = Mirror(load_mirrors())
parser = Parser('userdata.csv')
dl_map = parser.parsed_data


app = Flask(__name__)


@app.route('/status')
def status():
    return "OK"


@app.route('/reload')
def reload():
    load_mirrors()
    global mirror
    mirror = Mirror(load_mirrors())
    global dl_map
    dl_map = parser.reload()
    return dl_map


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return redirect(get_redirect(path, get_ip()), 302)


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=False, port=80)
