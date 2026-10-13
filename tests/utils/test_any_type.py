import pytest
from src.utils.any_type import ANY_TYPE, AnyType


class TestAnyType:
    def test_is_wildcard_string(self):
        assert isinstance(ANY_TYPE, AnyType)
        assert ANY_TYPE == "*"

    @pytest.mark.parametrize("other", ["IMAGE", "AUDIO", "STRING", "*", ""])
    def test_is_never_different(self, other):
        assert (other != ANY_TYPE) is False
        assert ANY_TYPE.__ne__(other) is False
