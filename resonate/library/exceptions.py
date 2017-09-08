"""Generic Exception Class."""


class GenericException(Exception):
    """Exceptions."""

    def __init__(self, msg):
        """Init."""
        self.msg = msg

    def __str__(self):
        """STR."""
        return self.msg
