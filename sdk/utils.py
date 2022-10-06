import requests
from sdk.errors import ParetoSDKError


def create_session():
    r"""Creates a new session instance."""
    session = requests.session()
    session.headers.update({
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'pareto/python',
    })
    return session


def get_query_path(url, params={}):
    r"""Creates full URI endpoint.
    Arguments:
    --
    url (string): Base URI. Includes URI parameters.
    params (Dict[string, any], default={}): Query parameters
    """
    if len(params) == 0:
        return url
    params_str = '&'.join('{key}={value}'.format(key=x[0], value=x[1]) 
                                for x in params.items()
                                if x[1] is not None
                                )
    if params_str:
        return f'{url}?{params_str}'

    return url


class Response:
    r"""Generic response object.
    Arguments:
    --
    data (Dict[string, any], default={}): JSON response data
    headers (Optional[Dict[string, any]]): Headers in the response
    """
    def __init__(self, data={}, headers=None):
        self.data = data
        self.headers = headers


def make_request(session,
                 uri,
                 method,
                 headers=None,
                 body={},
                 timeout=3000,
                 ):
    r"""Make a generic HTTP request.
    Arguments:
    --
    session (request.Session): Session instance
    uri (string): full URI endpoint
    headers (Optional[Dict[string, any]], default=None): Header information
    body (Dict[string, any], default={}): Body data. Send as `json` attribute
    timeout (integer, default=3000): Maximum seconds to wait before timeout
    """
    assert method.upper() in ['GET', 'POST'], f'method {method} not supported'
    response = getattr(session, method.lower())(uri, 
                                                headers=headers,
                                                json=body,
                                                timeout=timeout,
                                                )
    if not str(response.status_code).startswith('2'):
        raise ParetoSDKError(response)

    if response.content:
        return Response(response.json(), response.headers)
    else:
        return Response('{}', response.headers)
