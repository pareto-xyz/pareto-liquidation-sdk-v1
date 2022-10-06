from pprint import pprint
from sdk import LiquidationClient, UNDERLYING_ETH


def main():
    client = LiquidationClient("http://localhost:8545",
                               "http://localhost:8080",
                               )
    accounts = client.get_liquidatable_accounts(UNDERLYING_ETH)
    pprint(accounts)


if __name__ == "__main__":
    main()
