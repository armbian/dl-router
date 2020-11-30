""" flask app to redirect request to appropriate armbian mirror and image """

import uwsgi
import json
import logging

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
    global mode
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.preserve_quotes = True

    with open('mirrors.yaml', 'r') as f:
        config = yaml.load(f)
    mode = config['mode']
    print("using mode: {}".format(mode))
    return config['mirrors']


def reload_all():
    """ reload mirror and redirect map files """
    global mode
    mirror = Mirror(load_mirrors())
    if mode == "dl_map":
        global dl_map
        dl_map = parser.reload()
    return mirror


def get_ip():
    """ returns requestor's IP by parsersing proxy  headers """
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    return request.environ['HTTP_X_FORWARDED_FOR']


def get_region(IP):
    """ this is where we geoip and return region code """
    return None


def get_redirect(path, IP):
    """ get redirect based on path and IP(future) """
    global mode
    global dl_map
    region = get_region(IP)
    split_path = path.split('/')
    if split_path[0] == "region":
        if split_path[1] in mirror.all_regions():
            region = split_path[1]
        del split_path[0:2]
        path = "/{}".format("/".join(split_path))
    print("path: {}".format(path))
    if mode == "dl_map" and len(split_path) == 2:
        key = "{}/{}".format(split_path[0], split_path[1])
        new_path = dl_map.get(key, path)
        return "{}{}".format(mirror.next(region), new_path)
    if path == '':
        return mirror.next(region)
    print("path: {}".format(path))
    return "{}{}".format(mirror.next(region), path)


mirror = Mirror(load_mirrors())
if mode == "dl_map":
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
    return "reloded"


@ app.route('/mirrors')
def show_mirrors():
    """ return all_mirrors in json format to requestor """
    return json.dumps(mirror.all_mirrors())


@ app.route('/regions')
def show_regions():
    """ return all_regions in json format to requestor """
    return json.dumps(mirror.all_regions())


@ app.route('/dl_map')
def show_dl_map():
    global mode
    global dl_map
    if mode == "dl_map":
        return json.dumps(dl_map)
    return "no map. in direct mode"


@ app.route('/', defaults={'path': ''})
@ app.route('/<path:path>')
def catch_all(path):
    return redirect(get_redirect(path, get_ip()), 302)


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=False, port=80)
