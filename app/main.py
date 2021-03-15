""" flask app to redirect request to appropriate armbian mirror and image """

import json

try:
    import uwsgi
except:
    print("not running under uwsgi")

from flask import (
        Flask,
        redirect,
        request,
        Response,
)
from geolite2 import geolite2
from download_image_map import Parser
from mirror_list import Mirror

import os
mirror_path="mirrors.yaml"
if "ARMBIAN_MIRROR_CONF" in os.environ:
    mirror_path=os.environ["ARMBIAN_MIRROR_CONF"]

#print("Mirrors conf file:",mirror_path)

mirror = Mirror(mirror_path)
if mirror.mode == "dl_map":
    parser = Parser('userdata.csv')
    DL_MAP = parser.parsed_data
else:
    DL_MAP = None

geolite_reader = geolite2.reader()
app = Flask(__name__)

# def reload_all():
#     """ reload mirror and redirect map files """
#     mirror = Mirror()
#     if mirror.mode == "dl_map":
#         global dl_map
#         dl_map = parser.reload()
#     return mirror

def get_ip():
    """ returns client IP by parsing proxy headers
        if they don't exist, return the actual client IP address """
    return request.environ.get('HTTP_X_FORWARDED_FOR',
                               request.environ.get('REMOTE_ADDR'),
                              )


def get_region(client_ip, reader=geolite_reader, continents=mirror.continents):
    """ this is where we geoip and return region code """
    if client_ip.startswith(("192.168.", "10.")):
        print(f"Local IP address: {client_ip}")
        return None
    try:
        match = reader.get(client_ip)
        if not match:
            print(f"match failure for IP: {client_ip}")
            return None
        # matches are a dict where we want match["continent"]["code"] = "EU"
        conti = match.get("continent", {}).get("code")
        if conti in continents:
            print(f"Match {client_ip} to continent {conti}")
            return conti
    # pylint: disable=broad-except
    except Exception as error_message:
        print(f"match failure for IP: {client_ip} (Error: {error_message}")
        print(json.dumps(match))
    else:
        return None

def get_redirect(path, client_ip, mirror_class=mirror, dl_map=DL_MAP):
    """ get redirect based on path and IP """
    region = get_region(client_ip)
    split_path = path.split('/')

    if split_path[0] == "region":
        if split_path[1] in mirror_class.all_regions():
            region = split_path[1]
        del split_path[0:2]
        path = "{}".format("/".join(split_path))

    if mirror_class.mode == "dl_map" and len(split_path) == 2:
        key = "{}/{}".format(split_path[0], split_path[1])
        new_path = dl_map.get(key, path)
        return "{}{}".format(mirror_class.next(region), new_path)

    if path == '':
        return mirror_class.next(region)

    return "{}{}".format(mirror_class.next(region), path)


@app.route('/status')
def status():
    """ return health check status """
    resp = Response("OK")
    resp.headers['X-Client-IP'] = get_ip()
    return resp


@app.route('/reload')
def signal_reload():
    """ trigger graceful reload via uWSGI """
    uwsgi.reload()
    return "reloading"


@app.route('/mirrors')
def show_mirrors():
    """ return all_mirrors in json format to requestor """
    return json.dumps(mirror.all_mirrors())


@app.route('/regions')
def show_regions():
    """ return all_regions in json format to requestor """
    return json.dumps(mirror.all_regions())


@app.route('/dl_map')
def show_dl_map(mirror_mode=mirror.mode, dl_map=DL_MAP):
    """ returns a direct-download map """
    if mirror_mode == "dl_map":
        return json.dumps(dl_map)
    return "no map. in direct mode"


@app.route('/geoip')
def show_geoip(reader=geolite_reader):
    """ returns the geoip location of the client IP """
    return json.dumps(reader.get(get_ip()))


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """ default app route for redirect """
    return redirect(get_redirect(path, get_ip()), 302)


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=False, port=80)
