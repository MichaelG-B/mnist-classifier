"""
Run this to confirm your environment is correct:  python verify_setup.py

Every teammate runs this after cloning. If all checks pass, you are ready to
work. If one fails, the message tells you what to fix.
"""
import sys
from pathlib import Path

FAIL = []
def check(name, ok, hint=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    if not ok:
        FAIL.append((name, hint))

print("\nEnvironment")
v = sys.version_info
check(f"Python {v.major}.{v.minor} (need 3.10-3.13)",
      v.major == 3 and 10 <= v.minor <= 13,
      "TensorFlow supports Python 3.10-3.13. Install one of those.")

check("Running inside a virtual environment",
      sys.prefix != sys.base_prefix,
      "Run:  source venv/bin/activate   (Windows: venv\\Scripts\\activate)")

print("\nPackages")
for mod, hint in [("django", "pip install -r requirements.txt"),
                  ("numpy", "pip install -r requirements.txt"),
                  ("PIL", "pip install pillow"),
                  ("tensorflow", "pip install -r requirements.txt  (Mac: tensorflow==2.21.*)")]:
    try:
        m = __import__(mod)
        ver = getattr(m, "__version__", "?")
        check(f"{mod} {ver}", True)
    except ImportError:
        check(mod, False, hint)

print("\nProject files")
root = Path(__file__).parent
for f in ["manage.py", "Dockerfile", "requirements.txt", ".gitignore",
          "config/settings.py", "classifier/views.py",
          "classifier/ml/predictor.py",
          "classifier/templates/base.html",
          "classifier/templates/registration/login.html"]:
    check(f, (root / f).exists(), "Re-clone the repo; a file is missing.")

print("\nSettings")
try:
    import os, django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    from django.conf import settings
    check("'classifier' in INSTALLED_APPS", "classifier" in settings.INSTALLED_APPS)
    check("CSRF_TRUSTED_ORIGINS set for ngrok",
          any("ngrok" in o for o in getattr(settings, "CSRF_TRUSTED_ORIGINS", [])),
          "Without this, login fails with 403 through the public URL.")
    check("LOGIN_URL set", bool(getattr(settings, "LOGIN_URL", None)))
except Exception as exc:
    check("Django settings load", False, str(exc))

print("\nContract: predictor")
try:
    import numpy as np
    from classifier.ml.predictor import predict, MODEL_IS_REAL
    out = predict(np.random.rand(28, 28))
    check("predict() returns shape (10,)", out.shape == (10,))
    check("predict() sums to 1.0", abs(float(out.sum()) - 1.0) < 1e-6)
    print(f"       (model is {'REAL' if MODEL_IS_REAL else 'STUB -- Person B replaces in Session B2'})")
except Exception as exc:
    check("predictor import", False, str(exc))

print()
if FAIL:
    print(f"{len(FAIL)} check(s) failed:\n")
    for name, hint in FAIL:
        print(f"  - {name}\n      {hint}")
    sys.exit(1)
print("All checks passed. Run:  python manage.py runserver\n")
