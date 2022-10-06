import os, json

from eth_account import Account
from web3 import Web3, HTTPProvider
from web3.auto import w3
from web3.middleware import construct_sign_and_send_raw_middleware


from sdk import constants
from sdk.utils import (create_session, 
                       get_query_path,
                       make_request,
                       )
from sdk.constants import UNDERLYING_ETH, VALID_UNDERLYING

cur_dir = os.path.dirname(os.path.realpath(__file__))
abi_dir = os.path.join(cur_dir, "abi")


CONTRACT_ADDRS = {
    UNDERLYING_ETH: os.environ.get("MARGIN_CONTRACT"),
}

CONTRACT_ABIS = {
    UNDERLYING_ETH: os.path.join(abi_dir, "margin_v1_abi.json"),
}


class LiquidationClient:
    r"""Bot that queries the backend to fetch margin accounts, find the 
    ones below margin, and execute liquidation.
    Arguments
    --
    web3_host (string): Host for the Web3 provider
    api_host (string): Host for the backend endpoint
    eth_private_key (string): Private key for ETH
    timeout (integer): Number of ms to wait prior to timeout
    """
    def __init__(self,
                 web3_host,
                 api_host,
                 eth_private_key=None,
                 timeout=constants.DEFAULT_TIMEOUT,
                 ):
        if api_host.endswith('/'):
            api_host = api_host[:-1]

        if web3_host.endswith('/'):
            web3_host = web3_host[:-1]

        account = None

        if eth_private_key is not None:
            assert eth_private_key.startswith("0x"), "Private key must start with 0x hex prefix"
            account = Account.from_key(eth_private_key)

            # now we can use web3.eth.send_transaction(), Contract.functions.xxx.transact() functions
            # with local private key through middleware 
            w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))

        # Create web3 provider
        provider = Web3(HTTPProvider('http://localhost:8545',
                                     request_kwargs={'timeout': 60},
                                     ))

        # Note we do not save the private key
        self.account = account
        self.provider = provider
        self.api_host = api_host
        self.web3_host = web3_host
        self.session = create_session()
        self.timeout = timeout

    def get_liquidatable_accounts(self, underlying=UNDERLYING_ETH):
        r"""Call the Pareto backend to get a list of all margin accounts. 
        Parse these accounts to find those that are below margin.
        Arguments:
        --
        underlying (integer, default=UNDERLYING_ETH): Underlying token.
        """
        assert underlying in VALID_UNDERLYING, \
            "get_liquidatable_accounts: underlying not supported"

        uri = get_query_path(f'{self.api_host}/public/margin/check/all/{underlying}')
        response = make_request(self.session, uri, 'GET', timeout=self.timeout)

        if 'message' not in response.data:
            return []

        checks = response.data['message']['checks']
        accounts = response.data['message']['users']

        # Filter the accounts by those that are below margin
        liquidatable_accounts = [accounts[i] for i in range(len(accounts)) if not checks[i]]
        return liquidatable_accounts

    def check_if_liquidatable(self, address, underlying=UNDERLYING_ETH):
        r"""Check if an address is liquidatable.
        Arguments:
        --
        address (string): Address of the EOA to cancel
        underlying (integer, default=UNDERLYING_ETH): Underlying token.
        """
        assert underlying in VALID_UNDERLYING, \
            "check_if_liquidatable: underlying not supported"

        params = {'address': address}
        uri = get_query_path(f'{self.api_host}/public/margin/check/{underlying}',
                             params=params,
                             )
        response = make_request(self.session, uri, 'GET', timeout=self.timeout)

        if 'message' not in response.data:
            return False

        return response.data['message']['check']

    def cancel_open_orders(self, address, underlying=UNDERLYING_ETH):
        r"""If an address is below margin, we can cancel all their open orders.
        Arguments:
        --
        address (string): Address of the EOA to cancel
        underlying (integer, default=UNDERLYING_ETH): Underlying token.
        """
        # A similar check is performed on the backend
        assert self.check_if_liquidatable(address, underlying=underlying), \
            "cancel_open_orders: user is not under margin"

        assert underlying in VALID_UNDERLYING, \
            "cancel_open_orders: underlying not supported"
        uri = get_query_path(f'{self.host}/public/margin/liquidate/{underlying}')
        body = {
            'address': address
        }
        response = make_request(self.session,
                                uri,
                                'POST',
                                body=body,
                                timeout=self.timeout,
                                )
        data = response.data
        print(data)

    def liquidate(self, address, underlying=UNDERLYING_ETH):
        r"""Liquidate the specified address through the Pareto smart contract.
        User must be below margin to be liquidated.
        Arguments:
        --
        address (string): Address of the EOA to cancel
        underlying (integer, default=UNDERLYING_ETH): Underlying token.
        """
        assert self.account is not None, \
            "liquidate: you must provide your private key to do this"

        # A similar check is performed on the backend
        assert self.check_if_liquidatable(address, underlying=underlying), \
            "liquidate: user is not under margin"

        assert underlying in VALID_UNDERLYING, \
            "liquidate: underlying not supported"

        assert self.provider is not None, \
            "liquidate: fail to initialize Web3 provider"

        assert self.provider.isConnected(), \
            "liquidate: fail to connect to Web3 provider"

        contract = w3.eth.contract(address=CONTRACT_ADDRS[underlying],
                                   abi=json.loads(CONTRACT_ABIS[underlying]),
                                   )
        # Call contract function
        # https://leftasexercise.com/2021/08/22/using-web3-py-to-interact-with-a-smart-contract/
        # https://ethereum.stackexchange.com/questions/127130/how-to-call-certain-solidity-function-based-on-python-function-parameter
        tx_hash = contract.functions.liquidate(address).transact({"from": self.account.address})

        # wait for transaction to be mined
        w3.eth.wait_for_transaction_receipt(tx_hash)
