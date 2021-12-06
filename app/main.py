""" flask app to redirect request to appropriate armbian mirror and image """

from json import dumps

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

from os import environ
if "ARMBIAN_MIRROR_CONF" in environ:
    mirror_path=environ["ARMBIAN_MIRROR_CONF"]
else:
    mirror_path="mirrors.yaml"
print("Mirrors conf file:",mirror_path)
mirror = Mirror(mirror_path)

if mirror.mode == "dl_map":
    if "ARMBIAN_USERDATA_CONF" in environ:
        userdata_path=environ["ARMBIAN_USERDATA_CONF"]
    else:
        userdata_path="userdata.csv"
    print("userdata conf file:",userdata_path)
    parser = Parser(userdata_path)
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
    """ returns client IP by parsing proxy header
        if it doesn't exist, returns the actual client IP address """
    return request.environ.get('HTTP_X_FORWARDED_FOR',
                               request.environ.get('REMOTE_ADDR'),
                              )

def get_scheme():
    """ returns request scheme by parsing proxy header
        if it doesn't exist, returns the actual request scheme """
    return request.environ.get('HTTP_X_FORWARDED_PROTO',
                               request.scheme,
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
        print(dumps(match))
    else:
        return None

def get_redirect(path, client_ip, scheme, mirror_class=mirror, dl_map=DL_MAP):
    """ get redirect based on path and IP """
    region = get_region(client_ip)
    split_path = path.split('/')

    if split_path[0] == "region":
        if split_path[1] in mirror_class.all_regions():
            region = split_path[1]
        del split_path[0:2]
        path = "{}".format("/".join(split_path))

    """ prepend scheme from client request if not given by mirror url
        assume scheme is valid if provided in url """
    mirror_url = mirror_class.next(region)
    if mirror_url.count('://', 2, 8) == 0:
        mirror_url = scheme + '://' + mirror_url

    if mirror_class.mode == "dl_map" and len(split_path) == 2:
        key = "{}/{}".format(split_path[0], split_path[1])
        new_path = dl_map.get(key, path)
        return "{}{}".format(mirror_url, new_path)

    if path == '':
        return mirror_url

    return "{}{}".format(mirror_url, path)


@app.route('/status')
def status():
    """ return health check status """
    resp = Response("OK")
    resp.headers['X-Client-IP'] = get_ip()
    resp.headers['X-Request-Scheme'] = get_scheme()
    return resp


@app.route('/reload')
def signal_reload():
    """ trigger graceful reload via uWSGI """
    uwsgi.reload()
    return "reloading"


@app.route('/mirrors')
def show_mirrors():
    """ return all_mirrors in json format to requestor
    prepend http:// if no scheme is present """
    mirror_list = mirror.all_mirrors()
    for region in mirror_list.keys():
        for i in range(len(mirror_list[region])):
            if mirror_list[region][i].find('://', 3, 8) == -1:
                mirror_list[region][i] = 'http://' + mirror_list[region][i]
    return dumps(mirror_list)


@app.route('/regions')
def show_regions():
    """ return all_regions in json format to requestor """
    return dumps(mirror.all_regions())


@app.route('/dl_map')
def show_dl_map(mirror_mode=mirror.mode, dl_map=DL_MAP):
    """ returns a direct-download map """
    if mirror_mode == "dl_map":
        return dumps(dl_map)
    return "no map. in direct mode"


@app.route('/geoip')
def show_geoip(reader=geolite_reader):
    """ returns the geoip location of the client IP """
    return dumps(reader.get(get_ip()))


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """ default app route for redirect """
    resp = redirect(get_redirect(path, get_ip(), get_scheme()), 302)
    resp.headers['X-Request-Scheme'] = get_scheme()

    return resp


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=False, port=80)
