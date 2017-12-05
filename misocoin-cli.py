#! /usr/bin/env python
import requests
import json
import sys

from functools import reduce
from misocoin.sync import misocoin_cli


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Missing method')
        exit(0)

    config = filter(lambda x: x[0] is '-', sys.argv[1:])
    config_kwargs = reduce(lambda x, y: {y.split(
        '=')[0][1:]: y.split('=')[1], **x}, config, {})

    params = list(filter(lambda x: x[0] is not '-', sys.argv[1:]))

    result = misocoin_cli(params[0], params[1:], **config_kwargs)

    print(json.dumps(result))
