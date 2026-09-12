# MNIST Classifier Web App

Django + TensorFlow web app that classifies a hand-drawn digit uploaded as a
28x28 CSV. Deployed on AWS Lightsail via Docker, exposed publicly with ngrok.

## Team

| Person | Role | Owns |
|---|---|---|
| | A — Infrastructure | `Dockerfile`, `requirements.txt`, `config/settings.py`, AWS, ngrok, deploys |
| | B — ML & Writeup | `classifier/ml/`, `static/analysis/`, `notebooks/`, `samples/`, article text |
| | C — Backend | `classifier/views.py`, `forms.py`, `utils.py`, `urls.py`, `config/urls.py` |
| | D — Frontend | `classifier/templates/`, `static/css/` |

**Nobody edits a file they do not own.** Message the owner instead. This one
rule removes most merge conflicts.

## Setup (every teammate, once)

```bash
git clone https://github.com/MichaelG-B/mnist-classifier.git
cd mnist-classifier

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt   # 5-10 min, TensorFlow is large
python manage.py migrate
python verify_setup.py            # all checks should pass
python manage.py runserver
```

Open <http://localhost:8000>.

**Python 3.10-3.13.** On Apple Silicon Macs pip installs the regular
`tensorflow` package instead of `tensorflow-cpu`; requirements.txt handles this
automatically via a platform marker. Do not edit those two lines.

## Routes

| URL | What | Status |
|---|---|---|
| `/` | Smoke test, proves TensorFlow imports | temporary, C removes |
| `/mock/` | Fake result page with random data | temporary, C removes at integration |
| `/accounts/login/` | Login | permanent |
| `/accounts/signup/` | 404 on purpose — requirement 1b | n/a |

## The two contracts

These let four people work at once. Agreed at kickoff; do not change without
telling the other person.

**C to D — the result template context:**

```python
{
    "prediction":    int,           # 0-9
    "confidence":    float,         # 0.0-1.0
    "probabilities": [float] * 10,  # index = digit
    "image_uri":     str,           # "data:image/png;base64,..."
    "error":         str or None,
}
```

D builds against `/mock/` and never waits for C.

**B to C — the predictor:**

```python
predict(arr_28x28_scaled) -> np.ndarray shape (10,), sums to 1.0
```

C imports `from classifier.ml.predictor import predict` and calls it. When B
swaps the stub for the real model, C changes nothing.

## Git workflow

```bash
git checkout main && git pull origin main
git checkout -b feat/c-auth
# ... work ...
git add -A && git commit -m "Add login and gate all views"
git push -u origin feat/c-auth
# open a pull request; a teammate reviews and merges
```

Never commit to `main`. Never merge your own PR.

## Deploying (Person A only)

```bash
./deploy.sh                                  # on the AWS box
docker exec -it site python manage.py migrate
docker exec -it site python manage.py createsuperuser   # username: dan (password found in class assignment)
```

The `dan` account must be created **on the server**; the server database is
separate from everyone's local one.

## Reminder

Delete the Lightsail instance at the end of the semester or the card on file
gets charged.
