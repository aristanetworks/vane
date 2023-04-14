""" Tests for vane.utils functions """
from collections.abc import Iterable

import pytest
import vane.utils


class UtilsTests:
    """Set of tests for vane/utils.py"""

    def test_make_iterable_from_string(self):
        """Verify string is made iterable"""
        result = vane.utils.make_iterable("test")
        assert isinstance(result, Iterable)
        assert len(result) == 1

    def test_make_iterable_from_unicode(self):
        """Verify unicode string is made iterable"""
        result = vane.utils.make_iterable("test")
        assert isinstance(result, Iterable)
        assert len(result) == 1

    def test_make_iterable_from_iterable(self):
        """Verify list is made iterable"""
        result = vane.utils.make_iterable(["test"])
        assert isinstance(result, Iterable)
        assert len(result) == 1

    def test_make_iterable_raises_type_error(self):
        """Verify type error is raised"""
        with pytest.raises(TypeError):
            vane.utils.make_iterable(object())

    def test_get_current_fixture_testclass(self, request):
        """Verify get current fixture testclass"""
        print(request)
        result = vane.utils.get_current_fixture_testclass(request)
        assert result == "UtilsTests"

    def test_get_current_fixture_testname(self, request):
        """Verify get current fixture testclass"""
        result = vane.utils.get_current_fixture_testname(request)
        assert result == "test_get_current_fixture_testname"
