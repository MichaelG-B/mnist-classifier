"""
Upload validation for the classify page.  OWNER: Person C.

Kept separate from views.py on purpose: this file has no Django or TensorFlow
imports, so it can be tested and read on its own.
"""

import base64
import io

import numpy as np
from PIL import Image

MAX_UPLOAD_BYTES = 1_000_000  # a 28x28 CSV is a few KB; 1 MB is very generous


class UploadError(Exception):
    """Raised with a message that is safe to show directly to the user."""


def parse_upload(upload):
    """
    Validate an uploaded file. Return a 28x28 float array scaled to 0-1.

    Each way the file can be wrong raises UploadError with its own message.
    """
    name = (upload.name or "").lower()
    if not name.endswith(".csv"):
        raise UploadError("That file isn't a .csv")

    if upload.size > MAX_UPLOAD_BYTES:
        raise UploadError("That file is too large to be a 28x28 image")

    try:
        # utf-8-sig also strips the invisible BOM that Excel adds to CSVs
        text = upload.read().decode("utf-8-sig")
    except UnicodeDecodeError:
        raise UploadError("That file isn't readable as text") from None

    if not text.strip():
        raise UploadError("That file is empty")

    try:
        # ndmin=2: a one-row file stays 2-D, so the shape check below can
        #          report it instead of crashing.
        # comments=None: don't silently treat '#' as the start of a comment.
        arr = np.loadtxt(io.StringIO(text), delimiter=",", ndmin=2, comments=None)
    except ValueError:
        raise UploadError(
            "Couldn't read comma-separated numbers. "
            "Check for a header row or text entries."
        ) from None

    if arr.shape != (28, 28):
        rows, cols = arr.shape
        raise UploadError(f"Expected 28x28, got {rows} by {cols}")

    if not np.isfinite(arr).all():
        raise UploadError("Contains empty or non-numeric cells")

    if arr.min() < 0 or arr.max() > 255:
        raise UploadError("Values must be between 0 and 255")

    # Scale detection: a 0-1 image can never contain a value above 1, so
    # anything above 1 must be on the 0-255 scale.
    # Edge case: an all-black image is all zeros on BOTH scales, so the two are
    # indistinguishable -- but they are also identical after scaling, so it
    # doesn't matter. (Same for a 0-255 image whose brightest pixel is exactly 1.)
    if arr.max() > 1.0:
        arr = arr / 255.0

    return arr


def to_data_uri(arr):
    """
    Render a 0-1 array as a 280x280 PNG data URI.

    A data URI goes straight into <img src>, so there are no media files to
    save or serve (which is a pain inside Docker). NEAREST keeps the pixels
    crisp; the default smoothing turns a 28x28 image into mush at 280x280.
    """
    pixels = np.round(arr * 255).astype("uint8")
    img = Image.fromarray(pixels).resize((280, 280), Image.Resampling.NEAREST)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
