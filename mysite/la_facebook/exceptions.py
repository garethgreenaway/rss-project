class FacebookSettingsKeyError(KeyError):
    """ 
    see settings docs
    """
    pass


class NotAuthorized(Exception):
    pass


class MissingToken(Exception):
    pass


class UnknownResponse(Exception):
    pass


class ServiceFail(Exception):
    pass
