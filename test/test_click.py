import click.testing
import io
import logging
import os
import pathlib
import sys
import command_line_utilities as clu


def test_output_format_option(click_runner: click.testing.CliRunner):

    @click.command()
    @clu.click.output_format_option
    def click_command(output_format: clu.OutputFormat):
        assert isinstance(output_format, clu.OutputFormat)
        assert output_format == clu.OutputFormat.JSON

    result = click_runner.invoke(click_command, ["--output-format", "json"])
    assert result.exit_code == 0


def test_output_dir_option(click_runner: click.testing.CliRunner):

    @click.command()
    @clu.click.output_dir_option
    def click_command(output_dir: pathlib.Path):
        assert isinstance(output_dir, pathlib.Path)
        assert os.path.samefile("/var/tmp", output_dir)

    result = click_runner.invoke(click_command, ["--output-dir", "/var/tmp"])
    assert result.exit_code == 0


def test_sort_order(click_runner: click.testing.CliRunner):

    @click.command()
    @clu.click.sort_order_option
    def click_command(sort_order: clu.SortOrder):
        assert isinstance(sort_order, clu.SortOrder)
        assert sort_order == clu.SortOrder.DESCENDING

    result = click_runner.invoke(click_command, ["--sort-order", "descending"])
    assert result.exit_code == 0


def test_logging_verbose(click_runner: click.testing.CliRunner):

    @click.command()
    @clu.click.logging_options
    def click_command():
        assert logging.getLogger("test").getEffectiveLevel() == logging.DEBUG

    result = click_runner.invoke(click_command, ["--verbose"])
    assert result.exit_code == 0


def test_logging_silent(click_runner: click.testing.CliRunner):

    @click.command()
    @clu.click.logging_options
    def click_command():
        assert logging.getLogger("test").getEffectiveLevel() == logging.ERROR

    result = click_runner.invoke(click_command, ["--silent"])
    assert result.exit_code == 0


def test_logging_none(click_runner: click.testing.CliRunner):

    @click.command()
    @clu.click.logging_options
    def click_command():
        assert logging.getLogger("test").getEffectiveLevel() == logging.INFO

    result = click_runner.invoke(click_command, [])
    assert result.exit_code == 0


def test_comma_separated_list():
    expected_values = ["foo", '"bar baz"', "bop_foo"]
    actual_values = clu.click.comma_separated_list(",".join(expected_values))

    assert len(expected_values) == len(actual_values)
    for i in range(len(expected_values)):
        assert expected_values[i] == actual_values[i]


def test_read_stdin(capsys, monkeypatch):
    expected = "Test of stdin"
    monkeypatch.setattr(sys, "stdin", io.StringIO(expected))
    stdin = clu.click.read_stdin("stdin")
    captured = capsys.readouterr()
    assert "Reading plaintext from stdin" in captured.err
    assert stdin == expected


def test_read_stdin_bypassed(capsys, monkeypatch):
    expected = "Test of stdin"
    monkeypatch.setattr(sys, "stdin", io.StringIO(expected))
    stdin = clu.click.read_stdin("Foo")
    assert stdin == "Foo"
