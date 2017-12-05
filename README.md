# misocoin
Educational Bitcoin protocol reimplemented in Python

## Basic usage
```
./miscoind.py -host=<localhost> -port=<4000> -priv_key=<60c8cb60c21143fffdd682f399ef3baa4b67c56a1f83a274284cfe7c57e007ed>
```

## Basic API
```
./misocoin-cli.py get_info
./misocoin-cli.py get_block <block_number>
./misocoin-cli.py get_balance
./misocoin-cli.py send_misocoin <to_address> <amount>

# To specify which host and port
./misocoin-cli.py -host=<localhost> -port=<4000> [args]
```

## Setup two nodes

Terminal 1:
```
./miscoind.py -port=4001 -priv_key=60c8cb60c21143fffdd682f399ef3baa4b67c56a1f83a274284cfe7c57e007ed
```

Terminal 2:
```
./misocoind.py -port=4002 -nodes=localhost:4001 -priv_key=c551a109f752cf7ae8b3e2c8f33349c8840cf9bfc86cf05863dad0bb8a626667
```