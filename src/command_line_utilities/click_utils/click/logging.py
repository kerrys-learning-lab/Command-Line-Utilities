import click
import functools
import logging
import rich.logging
from ... import utils


def logging_options(wrapped_command_function):

    @click.option("-v", "--verbose", is_flag=True, help="Enable DEBUG logging.")
    @click.option("-s", "--silent", is_flag=True, help="Enable only ERROR logging.")
    @functools.wraps(wrapped_command_function)
    def wrapper(*args, verbose: bool, silent: bool, **kwargs):
        if verbose and silent:
            raise click.UsageError("--verbose and --silent are mutually exclusive")

        level = logging.INFO
        if verbose:
            level = logging.DEBUG
        if silent:
            level = logging.ERROR

        logging.basicConfig(
            format="%(name)20s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            level=level,
            handlers=[rich.logging.RichHandler(console=utils.console)],
        )

        logging.getLogger().setLevel(level)

        for lgr in ['urllib3.connectionpool']:
            logging.getLogger(lgr).setLevel(logging.ERROR)

        return wrapped_command_function(*args, **kwargs)

    return wrapper
