import click
import pathlib
from ...output import OutputFormat
from ...sort import SortOrder


def output_format_option(decorated_function):
    decorate = click.option(
        "--output-format",
        "output_format",
        type=click.Choice(OutputFormat, case_sensitive=False),
        default=OutputFormat.TABLE,
        help="Output format.",
    )
    return decorate(decorated_function)


def output_dir_option(decorated_function):
    decorate = click.option(
        "--output-dir",
        type=pathlib.Path,
        default=None,
        help="Directory for file output. Required with --output-format to write files; omit to print to stdout.",
    )
    return decorate(decorated_function)


def sort_order_option(decorated_function):
    decorate = click.option(
        "--sort-order",
        "sort_order",
        type=click.Choice(SortOrder, case_sensitive=False),
        default=SortOrder.ASCENDING,
        help="Sort order",
    )
    return decorate(decorated_function)
