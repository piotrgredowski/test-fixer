import pytest

from examples.src.sum import sum_printer


@pytest.mark.example
@pytest.mark.parametrize(
    "args, expected",
    [
        ([1, 2, 3], "1 + 2 + 3 = 6"),
        ([1, 2, 3, 4], "1 + 2 + 3 + 4 = 10"),
        ([1], "1 = 1"),
    ],
)
def test_sum_printer(args, expected):
    assert sum_printer(*args) == expected
