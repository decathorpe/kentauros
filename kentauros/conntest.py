"""
This module contains one function (:py:func:`is_connected`), which is used for
basic connectivity checks before actions that require internet access / access
to a specific URL.
"""


import socket
from urllib.parse import urlparse


def is_connected(host_url: str):
    """
    This function tries to create a connection to the hostname specified by the
    URL argument. If any error occurs during connecting, ``False`` is returned.

    Arguments:
        str host_url:   URL of the host connectivity will checked to

    Returns:
        bool:   ``True`` if connection setup successful, ``False`` if not
    """

    hostname = urlparse(host_url).hostname

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

