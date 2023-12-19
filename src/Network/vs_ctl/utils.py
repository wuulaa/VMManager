"""
Utilities.
"""

from subprocess import PIPE
from subprocess import Popen
from uuid import UUID


def run(args):
    """
    Wrapper of 'subprocess.run'.

    :param args: Command arguments to execute.
    :return: instance of 'subprocess.Popen'.
    """
    popen = Popen(args, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    popen.wait()

    return popen


def is_valid_uuid(uuid):
    """
    Returns `True` if the given `uuid` is valid, otherwise returns `False`.

    :param uuid: str type value to be validated.
    :return: `True` if valid, else `False`.
    """
    try:
        UUID(uuid)
    except ValueError:
        return False
    return True