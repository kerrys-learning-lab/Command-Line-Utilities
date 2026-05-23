import click
import functools
import pathlib
from ...output import OutputFormat
from ...sort import SortOrder
from . utils import read_stdin
from ... import logger
from ... import utils

def _click_callback_dry_run(ctx: click.Context,
                            param: click.Parameter,
                            value: bool) -> bool:
    utils.IS_DRY_RUN = value
    logger.Logger.TAGS.append('dry-run')
    return value


def _click_callback_read_stdin(prompt: str|bool|None,
                               ctx: click.Context,
                               param: click.Parameter,
                               value: str) -> str:
    return read_stdin(value, prompt=prompt)


def dryrun_option(decorated_function):
    decorate = click.option("--dry-run",
                            "dry_run",
                            is_flag=True,
                            callback=_click_callback_dry_run,
                            help="Do not perform any mutations.")

    return decorate(decorated_function)


def output_format_option(decorated_function):
    decorate = click.option("--output-format",
                            "output_format",
                            type=click.Choice(OutputFormat, case_sensitive=False),
                            default=OutputFormat.TABLE,
                            help="Output format.",
    )
    return decorate(decorated_function)


def output_dir_option(decorated_function):
    decorate = click.option("--output-dir",
                            type=pathlib.Path,
                            default=None,
                            help="Directory for file output. Required with --output-format to write files; omit to print to stdout.")
    return decorate(decorated_function)


def sort_order_option(decorated_function):
    decorate = click.option("--sort-order",
                            "sort_order",
                            type=click.Choice(SortOrder, case_sensitive=False),
                            default=SortOrder.ASCENDING,
                            help="Sort order")
    return decorate(decorated_function)


def stdin_argument(argument_name: str,
                   prompt: str|bool|None = None,
                   required: bool = False,
                   **kwargs):

    def decorator(decorated_function):
        decorate = click.argument(argument_name,
                                  callback=functools.partial(_click_callback_read_stdin, prompt),
                                  required=required,
                                  **kwargs)
        return decorate(decorated_function)

    return decorator
