""" Module setup dependencies """
import codecs
import os.path
from setuptools import setup


def read(rel_path):
    """Read function to read rel_path"""

    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as file:
        return file.read()


def get(attribute, rel_path):
    """get(): gets the attribute value from file at rel_path"""

    for line in read(rel_path).splitlines():
        if line.startswith(attribute):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]

    raise RuntimeError("Unable to find version string.")


setup(version=get("version", "pyproject.toml"), name=get("name", "pyproject.toml"))
