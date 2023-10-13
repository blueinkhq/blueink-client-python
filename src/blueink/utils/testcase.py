class TestCase:
    def assert_true(self, val):
        if val is None:
            assert False, f"{val} is None, not True"

        assert val, f"{val} is False, not True"

    def assert_false(self, val):
        if val is None:
            assert False, f"{val} is None, not False"

        assert not val, f"{val} is True, not False"

    def assert_equal(self, a, b, msg=None):
        assert a == b, f"{a} != {b} {msg}"

    def assert_not_equal(self, a, b):
        assert a != b, f"{a} == {b}"

    def assert_in(self, item, container):
        assert item in container

    def assert_not_in(self, item, container):
        assert item not in container, f"{item} is not in array/set"

    def assert_len(self, container, length):
        assert len(container) == length, f"{len(container)} != {length}"

    def assert_not_none(self, item):
        assert item is not None, "f Value is None when it should not be"

    def assert_none(self, item):
        assert item is None, "f Value is not None when it should be"
