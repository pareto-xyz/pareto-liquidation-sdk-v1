import os, json
import requests
import time

from collections import defaultdict
from eth_account import Account
from web3 import Web3, HTTPProvider
from web3.auto import w3
from web3.middleware import construct_sign_and_send_raw_middleware


from sdk import constants
from sdk.utils import (create_session, 
                       get_query_path,
                       make_request,
                       UNDERLYING_ETH,
                       VALID_UNDERLYING,
                       )


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
                 eth_private_key,
                 timeout=constants.DEFAULT_TIMEOUT,
                 ):
        if api_host.endswith('/'):
            api_host = api_host[:-1]

        if web3_host.endswith('/'):
            web3_host = web3_host[:-1]

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
        uri = get_query_path(f'{self.host}/public/margin/check/all/{underlying}')
        response = make_request(self.session, uri, 'GET', timeout=self.timeout)
        data = response.data
        print(data)

    def cancel_open_orders(self, address, underlying=UNDERLYING_ETH):
        r"""If an address is below margin, we can cancel all their open orders.
        Arguments:
        --
        address (string): Address of the EOA to cancel
        underlying (integer, default=UNDERLYING_ETH): Underlying token.
        """
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

    def liquidate(self):
        pass
