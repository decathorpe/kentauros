import socket
from urllib.parse import urlparse


MAX_TRIES = 3
WAIT_SECS = 5


def trial(address: str) -> bool:
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
    hostname = urlparse(host_url).hostname

    tries = MAX_TRIES

    while tries:
        success = trial(hostname)
        if success:
            return True
        else:
            tries -= 1

    return False
