<h1><p align="center">Misocoin</p></h1>

<p align="center">
    <img src="https://i.imgur.com/LURNf2q.jpg"/>
</p>

Misocoin is a _barebones_ Bitcoin-like protocol implemented in Python 3.x. It was written as a challenge for myself to see if I could implement a bitcoin clone from scratch.

## Quick start

1. Make sure you're in a Python 3.x environment. I recommend using [miniconda](https://conda.io/miniconda.html)
2. `git clone git@github.com:kendricktan/misocoin.git`
3. `cd misocoin && pip install -r requirements.txt`
4. To start the misocoin daemon, run

```bash
# To start it on localhost:4000 with a random private key
./misocoind.py

** [Welcome] Your misocoin address is 610d2657b8c4df8da493bbe0671e7406d2bee7a6
 * Running on http://localhost:4000/ (Press CTRL+C to quit)

# To start it on localhost:4001 with a specific private key
# ./misocoind.py -host=localhost -port=4001 -priv_key=<60c8cb60c21143fffdd682f399ef3baa4b67c56a1f83a274284cfe7c57e007ed>
```

5. Once you have the daemon running, you can interact with the daemon it via the API

```bash
./misocoin-cli.py get_info
./misocoin-cli.py get_block <block_number>
./misocoin-cli.py get_balance
./misocoin-cli.py send_misocoin <to_address> <amount>

# To specify which host and port the daemon is located at
# ./misocoin-cli.py -host=<localhost> -port=<4000> [methods [args..]]
```

6. To connect misocoin with other nodes, try running `./misocoind.py -nodes=host1:port1,host2:port2`. E.g:

- Terminal 1:
```
./misocoind.py -port=4001
```

- Terminal 2:
```
./misocoind.py -port=4002 -nodes=localhost:4001
```

## What in misocoin

- [x] EDCSA
- [x] Dynamic difficulty (based on network hashing power)
- [x] Proof-of-Work
- [x] Consensus

## Todo?

- [] Nicer exception handling
- [] Enforce functional paradigm

## FAQ

- Who's miso?

Miso is my cat. You can find out about him more on [his instagram page](http://instagram.com/mr.miso.oz/).
