from setuptools import setup
import codecs
import os.path

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get(attribute, rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith(attribute):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

setup(
   version=get("version", "pyproject.toml"),
   name=get("name", "pyproject.toml")
)
