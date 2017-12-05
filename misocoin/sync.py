import requests
import json

from werkzeug.serving import WSGIRequestHandler


class MisocoinRequestHandler(WSGIRequestHandler):
    '''
    Don't want verbose logging
    '''

    def log(self, type, message, *args):
        return


def misocoin_cli(m, args, host='localhost', port=4000):
    url = "http://{}:{}/jsonrpc".format(host, port)
    headers = {'content-type': 'application/json'}

    # Example echo method
    payload = {
        "method": m,
        "params": args,
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()

    try:
        return response['result']
    except:
        return response
