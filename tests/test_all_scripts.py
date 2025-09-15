"""Run all the scripts."""

import os
import subprocess

import pytest


def get_scripts():
    """List out the scripts folder and return anything ending in .py"""
    scripts = []
    for name in os.listdir("scripts"):
        if name.endswith(".py"):
            scripts.append(os.path.join("scripts", name))
    return scripts


@pytest.mark.parametrize("name", get_scripts())
def test_script(name):
    """Run this script and check for many things."""
    with subprocess.Popen(
        ["python", name], stderr=subprocess.PIPE, stdout=subprocess.PIPE
    ) as proc:
        _stdout, stderr = proc.communicate()
        assert proc.returncode in [0, 1, 2], (
            f"Script {name} failed with {proc.returncode}, "
            f"stderr: {stderr.decode()}"
        )
    assert b"Traceback" not in stderr, (
        f"Script {name} had a traceback in stderr: {stderr.decode()}"
    )
    assert b"Error" not in stderr, (
        f"Script {name} had an error in stderr: {stderr.decode()}"
    )
    assert b"Exception" not in stderr, (
        f"Script {name} had an exception in stderr: {stderr.decode()}"
    )
    assert b"Warning" not in stderr, (
        f"Script {name} had a warning in stderr: {stderr.decode()}"
    )
