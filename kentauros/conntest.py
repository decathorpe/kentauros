"""
This module contains a simple function which is used for basic connectivity checks before actions
that require internet access / access to a specific URL.
"""


import socket
from urllib.parse import urlparse


MAX_TRIES = 3
WAIT_SECS = 5


def trial(address: str) -> bool:
    """
    This helper function attempts to connect to a remote host exactly once.

    Arguments:
        str address:    URL string

    Returns:
        bool:           *True* if successful, *False* if not
    """

    try:
        host = socket.gethostbyname(address)
        with socket.create_connection((host, 80), 2):
            pass
    except socket.herror:
        return False
    except socket.gaierror:
        return False
    except socket.timeout:
        return False
    except OSError:
        return False

    return True


def is_connected(host_url: str) -> bool:
    """
    This function tries to create a connection to the hostname specified by the URL argument. If any
    error occurs during connecting, *False* is returned.

    Arguments:
        str host_url:   URL of the host connectivity will checked to

    Returns:
        bool:           *True* if connection setup successful, *False* if not
    """

    hostname = urlparse(host_url).hostname

    tries = MAX_TRIES

    while tries:
        success = trial(hostname)
        if success:
            return True
        else:
            tries -= 1

    return False
