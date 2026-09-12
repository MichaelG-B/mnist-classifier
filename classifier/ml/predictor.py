"""
Model loading and prediction.

OWNER: Person B (ML)

=============================================================================
THIS IS A STUB. It returns random numbers, not real predictions.
It exists so Person C can write and test the backend before the model exists.
Person B replaces the body of predict() in Session B2. The SIGNATURE BELOW
MUST NOT CHANGE -- Person C is writing code against it right now.
=============================================================================

CONTRACT (agreed at kickoff, see TEAM_ACTION_PLAN.md section 4):

    predict(arr) -> numpy array

    INPUT:  numpy array, shape (28, 28), dtype float, values scaled 0.0-1.0
            (Person C handles the 0-255 -> 0-1 scaling before calling this.)

    OUTPUT: numpy array, shape (10,), probabilities that sum to 1.0
            Index = digit. So result[7] is the probability the image is a 7.
"""

import numpy as np

# Set to True by the real implementation so the UI can warn when it is fake.
MODEL_IS_REAL = False

MODEL = None


def predict(arr_28x28_scaled):
    """Return a length-10 probability vector for a scaled 28x28 image."""
    p = np.random.rand(10)
    p[np.random.randint(10)] += 6.0          # make one digit clearly "win"
    return p / p.sum()


# =============================================================================
# PERSON B: in Session B2, delete everything above except the imports and
# replace it with this. Nothing in Person C's code needs to change.
#
# from pathlib import Path
# from tensorflow import keras
#
# MODEL_IS_REAL = True
# MODEL_PATH = Path(__file__).parent / "mnist_model.keras"
# MODEL = keras.models.load_model(MODEL_PATH)
#
# def predict(arr_28x28_scaled):
#     batch = arr_28x28_scaled.reshape(1, 28, 28, 1)
#     return MODEL.predict(batch, verbose=0)[0]
#
# Note that load_model sits at module level, OUTSIDE the function, on purpose.
# Python runs it once when the server starts. Moving it inside predict() would
# reload the model from disk on every single upload, adding several seconds to
# every request and making the site feel broken.
#
# Build the path from Path(__file__).parent, not a relative string, because the
# working directory differs between your laptop and the Docker container.
# =============================================================================
