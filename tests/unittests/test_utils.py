""" Tests for vane.utils functions """
from collections.abc import Iterable

import pytest
import vane.utils


def test_make_iterable_from_string():
    """Verify string is made iterable"""
    result = vane.utils.make_iterable("test")
    assert isinstance(result, Iterable)
    assert len(result) == 1


def test_make_iterable_from_unicode():
    """Verify unicode string is made iterable"""
    result = vane.utils.make_iterable("test")
    assert isinstance(result, Iterable)
    assert len(result) == 1


def test_make_iterable_from_iterable():
    """Verify list is made iterable"""
    result = vane.utils.make_iterable(["test"])
    assert isinstance(result, Iterable)
    assert len(result) == 1


def test_make_iterable_raises_type_error():
    """Verify type error is raised"""
    with pytest.raises(TypeError):
        vane.utils.make_iterable(object())
