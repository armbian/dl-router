import os
import tempfile
import json

import pytest

from main import app


TEST_IPS = [ 
        "10.0.0.1",
        "1.2.3.4",
        "123.254.123.233",
        "5.254.123.233",
    ]

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_status(client):
    """ test the status endpoint """

    rv = client.get('/status')
    assert rv.data == b'OK'

def test_mirrors(client):
    """ test the mirrors endpoint """

    rv = client.get('/mirrors')
    jsondata = rv.data.decode('utf-8')

    assert isinstance(json.loads(jsondata), dict)

def test_regions(client):
    """ test the regions endpoint """

    rv = client.get('/regions')
    jsondata = rv.data.decode('utf-8')

    assert isinstance(json.loads(jsondata), list)

def test_regions_proxied(client):
    """ test the regions endpoint, but send x-forwarded-for headers """

    for address in TEST_IPS:
        test_headers = {
            "X-Forwarded-For" : address,
            }
        rv = client.get('/regions', headers=test_headers)
        jsondata = rv.data.decode('utf-8')
        assert isinstance(json.loads(jsondata), list)

def test_status_proxied(client):
    """ test the status endpoint, but send x-forwarded-for headers 
        the status endpoint sends an X-Client-IP header in the response
        """

    for address in TEST_IPS:
        test_headers = {
            "X-Forwarded-For" : address,
            }
        rv = client.get('/status', headers=test_headers)
        assert 'X-Client-IP' in rv.headers
        assert rv.headers.get('X-Client-IP') == address
