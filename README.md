# MNIST Digit Classifier

A convolutional neural network that reads handwritten digits, wrapped in a
password-protected Django site where you can upload your own 28×28 image and
watch the network classify it.

**Live site:** https://hunger-remover-radiation.ngrok-free.dev
**Test accuracy:** 99.59% on the MNIST test set (9,959 of 10,000 correct)

Group Project 1 — Image Classification

---

## What's on the site

Everything sits behind a login. There is no sign-up page; accounts are created
by an administrator.

- **Write-up** (`/`) — how the network was built, what worked and what didn't,
  examples of correctly and incorrectly classified digits, and an analysis of
  where and why the model gets confused.
- **Classify a digit** (`/classify/`) — upload a CSV of pixel intensities
  (28 rows × 28 columns, no header row). Values may be 0–255 or already scaled
  to 0–1; the site detects which. It renders the image, runs it through the
  model, and shows the predicted digit alongside the probability for all ten
  classes. Files that aren't a valid 28×28 CSV are rejected with a message
  explaining what's wrong.

## Team

| | Role | Contribution |
|---|---|---|
| Michael Beyer | Infrastructure | AWS Lightsail server, Docker build and compose setup, ngrok tunnel, Django settings, deployments, code review |
| Harelle Keli | Model & write-up | CNN design and training, test-set evaluation, analysis figures, sample test files, article text |
| Pri Balekai | Backend | Authentication, CSV upload and validation, scale detection, classification view |
| Panav Ladha | Frontend | Page templates, visual design and CSS, write-up page layout |

## How it works

```
browser ──► ngrok (public HTTPS) ──► Lightsail host :8000 ──► Docker container
                                                               └─ Django
                                                                   └─ TensorFlow model
```

- The trained model (`classifier/ml/mnist_model.keras`) loads once when the
  server starts, not on every request.
- The uploaded digit is rendered as an inline base64 PNG, so nothing is written
  to disk per request.
- The SQLite database holding the login account lives on a Docker volume, so it
  survives redeploys.

We split the work by file rather than by feature, and agreed the data passed
between each pair of roles before either side wrote code. Placeholder versions
of the model and the results page were committed on day one so all four of us
could build in parallel.

## Repository layout

```
classifier/
  ml/                 trained model and the predict() wrapper
  templates/          all page templates
  views.py, urls.py   request handling
  validation.py       CSV checks
config/               Django settings and root URL config
notebooks/            model training notebook
samples/              one test CSV per digit, plus a 0–1 scaled example
  bad/                intentionally malformed files for testing rejection
static/
  css/style.css       site styling
  analysis/           figures used on the write-up page
Dockerfile, docker-compose.yml, requirements.txt, deploy.sh
```

## Running locally

```bash
git clone https://github.com/MichaelG-B/mnist-classifier.git
cd mnist-classifier
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt     # 5–10 min; TensorFlow is large
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open http://localhost:8000. Requires Python 3.10–3.13. On Apple Silicon
Macs, `requirements.txt` installs `tensorflow` in place of `tensorflow-cpu`
automatically.

## Deployment

Hosted on an AWS Lightsail instance (Django blueprint, Debian 12, 2 GB RAM)
running Docker. ngrok runs inside a tmux session so the tunnel stays up after
the terminal closes.

To redeploy after changes merge to `main`, on the server:

```bash
~/deploy.sh
```

First-time server setup, and the problems worth knowing about:

- **Swap.** Add 2 GB of swap before the first build; the TensorFlow install can
  exhaust memory otherwise.
- **Docker** is installed from Docker's official Debian repository.
- **Container networking.** The Bitnami image's firewall drops forwarded
  traffic, so containers on Docker's default bridge network have no outbound
  internet access and pip cannot reach PyPI during the build. The build
  therefore runs with `--network=host` (see `deploy.sh`). Inbound traffic to
  the published port is unaffected.
- **`platform: linux/amd64`** in `docker-compose.yml` makes builds on Apple
  Silicon produce the same architecture as the server; `tensorflow-cpu` has no
  ARM64 Linux build.
- **Database volume.** Run `mkdir -p ~/mnist-classifier/data` once before the
  first deploy, then create the login account inside the running container:
  ```bash
  sudo docker exec -it site python manage.py migrate
  sudo docker exec -it site python manage.py createsuperuser
  ```
- **CSRF.** ngrok's free domain is `*.ngrok-free.dev`. It is listed in
  `CSRF_TRUSTED_ORIGINS`; without it, login returns a 403 through the public
  URL while working fine locally.

**Delete the Lightsail instance at the end of the semester.**
