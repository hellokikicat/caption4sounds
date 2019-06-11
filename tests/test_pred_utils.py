""" Unit Test for prediction_utils.py"""

import pytest

from ..api.prediction_utils import to_blocks
import numpy as np


@pytest.mark.parametrize(
    "input_array", [np.random.poisson(lam=10, size=(n, 128)) for n in [60, 61]]
)
@pytest.mark.parametrize("window_size", [5, 8])
def test_to_blocks(input_array, window_size):
    output = to_blocks(input_array, window_size, 2, 2)
    assert output.shape == (
        int((input_array.shape[0] - window_size) / 2) + 1,
        window_size * 2,
        128,
    )
