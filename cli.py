#! /usr/bin/env python
import requests
import json
import sys


def misocoin_client(m, args):
    url = "http://localhost:4000/jsonrpc"
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

    print(json.dumps(response['result']))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Missing method')
        exit(0)

    misocoin_client(sys.argv[1], sys.argv[2:])
