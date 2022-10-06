from pprint import pprint
from sdk import LiquidationClient, UNDERLYING_ETH


def main(args):
    client = LiquidationClient("http://localhost:8545",
                               "http://localhost:8080",
                               args.eth_private_key,
                               )
    accounts = client.liquidate(args.address, UNDERLYING_ETH)
    pprint(accounts)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('address',
                        type=str,
                        help="Address to liquidatable",
                        )
    parser.add_argument('eth_private_key',
                        type=str,
                        help="Ethereum private key (we do not store this information)")
    args = parser.parse_args()

    main(args)
