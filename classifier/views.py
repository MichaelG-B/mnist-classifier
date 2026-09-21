"""
Views.  OWNER: Person C (Backend).

Every view here is behind @login_required (requirement 1c).
"""

import logging

import numpy as np
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .ml.predictor import predict
from .validation import UploadError, parse_upload, to_data_uri

logger = logging.getLogger(__name__)

RESULT_TEMPLATE = "classifier/result.html"


def _context(prediction=None, confidence=None, probabilities=None,
             image_uri="", error=None):
    """The five-key contract with Person D's templates. Don't rename these."""
    return {
        "prediction": prediction,              # int 0-9
        "confidence": confidence,              # float 0.0-1.0
        "probabilities": probabilities or [],  # list of 10 floats
        "image_uri": image_uri,                # "data:image/png;base64,..."
        "error": error,                        # str or None
    }


@login_required
def home(request):
    """The write-up page."""
    return render(request, "classifier/home.html")


@login_required
@require_http_methods(["GET", "POST"])
def classify(request):
    """
    GET  -> empty upload page (this is also what "Start over" links to).
    POST -> validate the CSV, run the model, show the result on the same page.
    """
    if request.method == "GET":
        return render(request, RESULT_TEMPLATE, _context())

    upload = request.FILES.get("csv_file")
    if upload is None:
        return render(request, RESULT_TEMPLATE,
                      _context(error="Choose a .csv file first."), status=400)

    try:
        arr = parse_upload(upload)
    except UploadError as exc:
        return render(request, RESULT_TEMPLATE,
                      _context(error=str(exc)), status=400)

    try:
        # float() converts numpy float32 -> plain Python float for the template
        probs = [float(p) for p in predict(arr)]
    except Exception:  # noqa: BLE001 -- never show the user a Django error page
        logger.exception("Model prediction failed")
        return render(
            request, RESULT_TEMPLATE,
            _context(error="Something went wrong classifying that image. "
                           "Please try again."),
            status=500,
        )

    prediction = int(np.argmax(probs))
    return render(request, RESULT_TEMPLATE, _context(
        prediction=prediction,
        confidence=probs[prediction],
        probabilities=probs,
        image_uri=to_data_uri(arr),
    ))
