"""
Model loading and prediction.

OWNER: Person B (ML)


CONTRACT:
    Input:  28x28 NumPy array scaled from 0.0 to 1.0
    Output: NumPy array containing 10 probabilities that sum to 1.0
"""

from pathlib import Path

import numpy as np
from tensorflow import keras


MODEL_IS_REAL = True

MODEL_PATH = Path(__file__).parent / "mnist_model.keras"
MODEL = keras.models.load_model(MODEL_PATH)


def predict(arr_28x28_scaled):
    """Return 10 digit probabilities for one scaled 28x28 image."""
    batch = np.asarray(
        arr_28x28_scaled,
        dtype=np.float32
    ).reshape(1, 28, 28, 1)

    return MODEL.predict(batch, verbose=0)[0]
