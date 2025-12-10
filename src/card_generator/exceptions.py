class CodedError(Exception):
    """Exception with an error code."""

    exit_code = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UnknownError(CodedError):
    """Exception to signal an unknown error."""

    exit_code = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
