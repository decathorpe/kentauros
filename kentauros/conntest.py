"""
# TODO: napoleon module docstring
kentauros.conntest module
connectivity test to arbitrary URL
"""

import socket
from urllib.parse import urlparse


def is_connected(url):
    """
    # TODO: napoleon function docstring
    kentauros.conntest.is_connected():
    function that tests if the host behind "url" is reachable
    """

    hostname = urlparse(url).hostname

    try:
        host = socket.gethostbyname(hostname)
        socket.create_connection((host, 80), 2)
    except socket.herror:
        return False
    except socket.gaierror:
        return False
    except socket.timeout:
        return False

    return True

