import os

__all__ = [
    'BASE_DIR', 'ABS_PATH', 'ENV_BOOL', 'ENV_NUM', 'ENV_STR', 'ENV_LIST', 'PARDIR', 'ENV_TUPLE'
]


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

PARDIR = os.pardir

APPLICATION_NAME = "vode-atom"

ENV_PATH = os.path.join('/etc/secrets/', APPLICATION_NAME)


def ABS_PATH(*args):
    return os.path.join(BASE_DIR, *args)


def ENV_BOOL(name, default=False):
    """
    Get a boolean value from environment variable.
    If the environment variable is not set or value is not one or "true" or
    "false", the default value is returned instead.
    """

    if name not in os.environ:
        return default
    if os.environ[name].lower() in ['true', 'yes', '1']:
        return True
    elif os.environ[name].lower() in ['false', 'no', '0']:
        return False
    else:
        return default


def ENV_NUM(name, default=None):
    """
    Get a integer value from environment variable.
    If the environment variable is not set, the default value is returned
    instead.
    """
    return int(os.environ.get(name, default))


def ENV_STR(name, default=None):
    """
    Get a string value from environment variable.
    If the environment variable is not set, the default value is returned
    instead.
    """

    return os.environ.get(name, default)


def ENV_LIST(name, separator, default=None):
    """
    Get a list of string values from environment variable.
    If the environment variable is not set, the default value is returned
    instead.
    """
    if default is None:
        default = []

    if name not in os.environ:
        return default
    return os.environ[name].split(separator)


def ENV_TUPLE(name, separator, default=None):
    """
    Get a tuple of string values from environment variable.
    If the environment variable is not set, the default value is returned
    instead.
    """
    if default is None:
        default = ()

    if name not in os.environ:
        return default
    return tuple(os.environ[name].split(separator))


def _load_env_file():

    if os.path.exists(os.path.join(BASE_DIR, ".env")):
        envfile = os.path.join(BASE_DIR, ".env")
    else:
        envfile = os.path.join(ENV_PATH, ".env")

    if os.path.isfile(envfile):
        for line in open(envfile):
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            os.environ[k] = v


_load_env_file()
