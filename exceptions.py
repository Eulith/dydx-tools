class BadJurisdictionException(Exception):
    def __init__(self, message):
        super(BadJurisdictionException, self).__init__(message)
        self.message = message
