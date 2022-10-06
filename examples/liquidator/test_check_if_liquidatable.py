from pprint import pprint
from sdk import LiquidationClient, UNDERLYING_ETH


def main(args):
    client = LiquidationClient("http://localhost:8545",
                               "http://localhost:8080",
                               )
    liquidatable = client.check_if_liquidatable(args.address, UNDERLYING_ETH)
    pprint(liquidatable)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('address',
                        type=str,
                        help="Address to check if liquidatable",
                        )
    args = parser.parse_args()

    main(args)
