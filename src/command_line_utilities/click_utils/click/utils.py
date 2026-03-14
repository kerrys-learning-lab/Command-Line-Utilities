import click
import sys


def comma_separated_list(value) -> list[str]:
    """Parse a comma-separated string."""
    return [v.strip() for v in value.split(",") if v.strip()]


def enforce_mutually_exclusive(
    mutex_list: list[str], ctx: click.Context, current: click.Parameter, value
):
    param_keys = list(ctx.params.keys())
    if value:
        param_keys.append(current.human_readable_name)
    if sum(p in param_keys for p in mutex_list) > 1:
        raise click.UsageError(f"These options are mutually exclusive: {mutex_list}")


def read_stdin(value: str, prompt: str = None) -> str:
    """If value is '--', read from stdin; otherwise return as-is."""
    if value != "--":
        return value

    prompt = prompt or "Reading plaintext from stdin."
    print(
        f"{prompt}.  New-line/LF is allowed.  Use CTRL-D on a blank line to end",
        file=sys.stderr,
    )
    print("-----", file=sys.stderr)
    return sys.stdin.read()
