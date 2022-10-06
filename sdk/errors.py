class ParetoError(Exception):
    r"""Base error class for al exceptions. Other errors will inherit from this."""


class ParetoSDKError(ParetoError):
    r"""General error with Pareto's SDK.
    Arguments:
    --
    response (Response): Response object
    """
    def __init__(self, response):
        self.status_code = response.status_code
        try:
            self.msg = response.json()
        except ValueError:
            self.msg = response.text
        self.response = response
        self.request = getattr(response, 'request', None)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'ParetoSDKError(status_code={}, response={})'.format(self.status_code,
                                                                    self.msg,
                                                                    )
