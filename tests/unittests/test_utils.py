""" Tests for vane.utils functions """
from collections.abc import Iterable

import pytest
from vane import utils


class UtilsTests:
    """Tests for utils"""

    def test_make_iterable_from_string(self):
        """Verify string is made iterable"""
        result = utils.make_iterable("test")
        assert isinstance(result, Iterable)
        assert len(result) == 1

    def test_make_iterable_from_unicode(self):
        """Verify unicode string is made iterable"""
        result = utils.make_iterable("test")
        assert isinstance(result, Iterable)
        assert len(result) == 1

    def test_make_iterable_from_iterable(self):
        """Verify list is made iterable"""
        result = utils.make_iterable(["\u2728"])
        assert isinstance(result, Iterable)
        assert len(result) == 1

    def test_make_iterable_raises_type_error(self):
        """Verify type error is raised"""
        with pytest.raises(TypeError):
            utils.make_iterable(object())

    def test_get_current_fixture_testclass(self, request):
        """Verify get current fixture testclass"""
        result = utils.get_current_fixture_testclass(request)
        assert result == "UtilsTests"

    def test_get_current_fixture_testname(self, request):
        """Verify get current fixture testname"""
        result = utils.get_current_fixture_testname(request)
        assert result == "test_get_current_fixture_testname"

    def test_remove_comments(self):
        """Test that remove comments works"""
        input_string = """# this is a comment
        this is not"""
        expected_result = "        this is not"
        result = utils.remove_comments(input_string)
        assert result == expected_result

    def test_remove_comments_empty_string(self):
        """Test that remove comments works with empty string"""
        input_string = ""
        expected_result = ""
        result = utils.remove_comments(input_string)
        assert result == expected_result
