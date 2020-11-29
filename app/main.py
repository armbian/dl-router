""" flask app to redirect request to appropriate armbian mirror and image """

import uwsgi
import json

from flask import (
        Flask,
        redirect,
        request
)
# from markupsafe import escape
from download_image_map import Parser
from mirror_list import Mirror
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import (
    FoldedScalarString,
    LiteralScalarString,
)


def load_mirrors():
    """ open mirrors file and return contents """
#    with open('mirrors.conf', 'r') as row:
#        all_mirrors=row.read().splitlines()
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.preserve_quotes = True

    with open('mirrors.yaml', 'r') as f:
        config = yaml.load(f)
    return config['apt']


def reload_all():
    """ reload mirror and redirect map files """
    load_mirrors()
    global mirror
    mirror = Mirror(load_mirrors())
    global dl_map
    dl_map = parser.reload()
    return dl_map


def get_ip():
    """ returns requestor's IP by parsersing proxy  headers """
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    return request.environ['HTTP_X_FORWARDED_FOR']


def get_redirect(path, IP, region=None):
    """ get redirect based on path and IP(future) """
    split_path = path.split('/')
    if len(split_path) == 2:
        key = "{}/{}".format(split_path[0], split_path[1])
        new_path = dl_map.get(key, path)
        return "{}{}".format(mirror.next(), new_path)
    if path == '':
        return mirror.next()
    print("path: {}".format(path))
    return "{}{}".format(mirror.next(), path)


mirror = Mirror(load_mirrors())
parser = Parser('userdata.csv')
dl_map = parser.parsed_data


app = Flask(__name__)


@ app.route('/status')
def status():
    """ return health check status """
    return "OK"


@ app.route('/reload')
def signal_reload():
    """ trigger graceful reload via uWSGI """
    uwsgi.reload()
    return dl_map


@ app.route('/mirrors')
def show_mirrors():
    """ return all_mirrors in json format to requestor """
    return json.dumps(mirror.all_mirrors())


@ app.route('/', defaults={'path': ''})
@ app.route('/<path:path>')
def catch_all(path):
    return redirect(get_redirect(path, get_ip()), 302)


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=False, port=80)
