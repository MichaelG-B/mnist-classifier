"""
Views.

OWNER: Person C (Backend)

Nobody else edits this file. If you need something here, message Person C.

Right now this contains two temporary views:
  * home()        -- a smoke test that proves TensorFlow imports (delete later)
  * mock_result() -- fake data so Person D can build the result page today

Person C replaces these with the real classify() view in Sessions C2-C4.
"""

import random

from django.http import HttpResponse
from django.shortcuts import render


def home(request):
    """
    TEMPORARY smoke test. Person C deletes this in Session C3.

    The TensorFlow import is the entire point of this view. TensorFlow is the
    heaviest thing we depend on and the most likely thing to fail on a small
    AWS instance. Importing it in a page that does not use it forces that
    failure to surface on day one, during kickoff, when there is nothing else
    to blame -- rather than the night before the deadline when it could be any
    one of a hundred things.
    """
    try:
        import tensorflow as tf
        tf_status = f"TensorFlow {tf.__version__} imported successfully."
        ok = True
    except Exception as exc:                                  # noqa: BLE001
        tf_status = f"TensorFlow FAILED to import: {exc}"
        ok = False

    colour = "#166534" if ok else "#991b1b"
    return HttpResponse(
        "<div style='font-family:system-ui;max-width:34rem;margin:4rem auto'>"
        "<h1 style='margin:0 0 .5rem'>Skeleton alive</h1>"
        f"<p style='color:{colour};font-weight:600'>{tf_status}</p>"
        "<p>If you can read this, Django is running and the environment is "
        "correct. Next: <a href='/mock/'>/mock/</a> (Person D builds against "
        "this).</p></div>"
    )


def mock_result(request):
    """
    TEMPORARY fake result page. Person C deletes this on integration day.

    This exists so Person D can build and style the entire result page today,
    without waiting for the real backend or the trained model. Refresh the page
    for new random data.

    The dictionary below IS the contract from TEAM_ACTION_PLAN.md section 4.
    Person C's real view returns exactly these keys. Person D's template can
    rely on them. Neither person changes them without telling the other.
    """
    probs = [random.random() for _ in range(10)]
    winner = random.randrange(10)
    probs[winner] += 6.0
    total = sum(probs)
    probs = [p / total for p in probs]

    return render(request, "classifier/result.html", {
        "prediction": winner,                    # int, 0-9
        "confidence": probs[winner],             # float, 0.0-1.0
        "probabilities": probs,                  # list of 10 floats
        "image_uri": "",                         # data URI; empty in the mock
        "error": None,                           # str or None
        "is_mock": True,
    })
