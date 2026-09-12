# Project Workflow — Start Here

**Repo:** https://github.com/MichaelG-B/mnist-classifier
**Read this first.** It explains where the project stands, how the four of us
work without tripping over each other, and what happens next.

---

## Contents

1. [Where we are right now](#1-where-we-are-right-now)
2. [What we're building](#2-what-were-building)
3. [The four roles](#3-the-four-roles)
4. [Why the repo already has fake code in it](#4-why-the-repo-already-has-fake-code-in-it)
5. [File ownership](#5-file-ownership)
6. [Git workflow](#6-git-workflow)
7. [Your work, by role](#7-your-work-by-role)
8. [Timeline](#8-timeline)
9. [Integration day](#9-integration-day)
10. [Submission checklist](#10-submission-checklist)
11. [Troubleshooting](#11-troubleshooting)
12. [Glossary](#12-glossary)

---

## 1. Where we are right now

**Done:**

- GitHub repo created, public, skeleton pushed (35 files)
- Django project runs locally, verified end to end
- `Dockerfile` written and the folder structure laid out
- **TensorFlow 2.21 confirmed installing and importing cleanly** — this was the
  main risk and it's cleared
- Two placeholder files committed so we can work in parallel from day one
- `verify_setup.py` script that checks any teammate's environment and reports
  exactly what's wrong

**Not done:**

- Roles unassigned
- Nothing deployed to AWS yet — this is the next critical step
- No model trained
- No real functionality: no login, no upload, no classification
- No styling (and styling is **50% of the grade**)

**In short:** the plumbing works, the house isn't built.

---

## 2. What we're building

A web app where a logged-in user uploads a 28×28 CSV of pixel values and gets
back a classified digit, running on a cloud server that anyone can reach.

The eight graded requirements:

| # | Requirement | Owner |
|---|---|---|
| 1 | Login required; account `dan`; no self-registration; everything gated | C |
| 2 | Article explaining the network, with good/bad examples and failure analysis | B + D |
| 3 | CSV upload; auto-detect 0–255 vs 0–1 scale; reject bad files with a clear alert | C |
| 4 | Classify and display the image | C + D |
| 5 | Start-over button | C + D |
| 6 | Backend running on AWS, with a screenshot | A |
| 7 | **Site looks good — 50% of the grade** | D |
| 8 | GitHub repo accessible | A |

Worth reading that table twice. Requirement 7 alone is worth as much as
requirements 1 through 6 combined.

---

## 3. The four roles

The honest problem with a four-person web project is that a web app is a single
object. If all four of us open the same file, we spend the project resolving
merge conflicts instead of building. So we split **by file**, and where two
people's work meets, we agree on the interface before either writes code.

| Role | What you own | Hours | Weight |
|---|---|---|---|
| **A — Infrastructure** | Docker, AWS, ngrok, settings, all deploys | ~7 | Front-loaded, blocks everyone |
| **B — ML & Writeup** | Model training, analysis images, article text | ~7 | Lightest code, real writing |
| **C — Backend** | Auth, upload, validation, prediction views | ~9 | Heaviest code |
| **D — Frontend** | Every template, all styling, article layout | ~9 | **Half the grade** |

Some honest guidance on picking:

- **A** should be whoever is most comfortable in a terminal and willing to put a
  card on an AWS account. Busiest person in week one, least busy in week two.
- **B** should be whoever likes notebooks. Light on code, so this person also
  writes the article — that's a real deliverable, not a footnote.
- **C** should be whoever knows Django best or is most willing to read docs.
- **D** is not the consolation prize. It's the single highest-leverage role we
  have. Give it to whoever will care that the spacing is consistent.

Fill in at the kickoff:

```
A (Infrastructure) = ______________
B (ML & Writeup)   = ______________
C (Backend)        = ______________
D (Frontend)       = ______________
```

---

## 4. Why the repo already has fake code in it

Two files in the repo return made-up data on purpose. This is the idea the whole
schedule depends on, so it's worth understanding before you start.

### The problem

Normally this project runs in sequence: B trains the model, then C writes the
backend that calls it, then D styles the pages that display it. D — who owns
half our grade — waits a week and a half before starting, then panics.

### The fix

Both handoffs get a **fake version committed on day one**, with the real shape
agreed in advance. Everyone builds against the fake, and when the real thing
lands, nothing has to change.

### Contract 1 — C hands data to D

`classifier/views.py` has a `mock_result` view at **http://localhost:8000/mock/**
that produces random predictions. Refresh it and the numbers change.

It always supplies exactly these five values:

```python
{
    "prediction":    int,           # 0-9, the predicted digit
    "confidence":    float,         # 0.0-1.0, probability of the winner
    "probabilities": [float] * 10,  # all ten, index = digit
    "image_uri":     str,           # "data:image/png;base64,..." -> <img src="">
    "error":         str or None,   # user-facing message, or None on success
}
```

**D builds and styles the entire result page against `/mock/` starting today.**
When C's real view arrives, it returns the same five keys and D's template works
untouched.

### Contract 2 — B hands the model to C

`classifier/ml/predictor.py` currently returns random numbers. The signature is
the contract:

```python
predict(arr_28x28_scaled) -> np.ndarray, shape (10,), sums to 1.0
```

In goes a 28×28 array scaled 0–1. Out come ten probabilities.

**C writes `from classifier.ml.predictor import predict` and calls it today.**
When B swaps the stub for the trained model, C changes nothing.

### The rule

Neither contract changes without the other person agreeing. Teams that skip this
discover on integration day that the backend returns `pred` while the template
expects `prediction`, and lose an evening reconciling.

---

## 5. File ownership

**Nobody edits a file they don't own.** If you need a change elsewhere, message
the owner. This single rule removes most merge conflicts.

| File / folder | Owner |
|---|---|
| `Dockerfile`, `requirements.txt`, `.gitignore`, `deploy.sh`, `README.md` | **A** |
| `config/settings.py` | **A** |
| `config/urls.py`, `classifier/urls.py` | **C** |
| `classifier/views.py`, `forms.py`, `utils.py` | **C** |
| `classifier/ml/**`, `static/analysis/**`, `notebooks/**`, `samples/**` | **B** |
| `classifier/templates/**`, `static/css/**` | **D** |

`settings.py` is the one file two people genuinely need. **A owns it.** When C
needs `LOGIN_URL` added, C asks A. Feels bureaucratic; saves an afternoon.

Every file in the repo has an owner comment at the top.

---

## 6. Git workflow

### Setup, once

```bash
git clone https://github.com/MichaelG-B/mnist-classifier.git
cd mnist-classifier
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt   # 5-10 min
python manage.py migrate
python verify_setup.py            # every line should say PASS
python manage.py runserver
```

Open http://localhost:8000 — green "TensorFlow imported successfully" means
you're good. Also check `/mock/`.

Python 3.10–3.13. On Apple Silicon Macs, `requirements.txt` automatically
installs `tensorflow` instead of `tensorflow-cpu` (the CPU-only package has no
Mac ARM build). Don't edit those two lines.

**Activate the venv every time you open a new terminal.** Forgetting is the most
common confusion — the symptom is `ModuleNotFoundError: No module named 'django'`
on a project that worked yesterday.

### Daily

```bash
git checkout main && git pull origin main
git checkout -b feat/c-auth          # your letter, what you're doing
# work
git add -A
git commit -m "Add login and gate all views"
git push -u origin feat/c-auth
# open a pull request on GitHub; someone else reviews and merges
```

### The five rules

1. Never commit directly to `main`.
2. Never edit a file you don't own.
3. `git pull origin main` before starting work each day.
4. Open a PR when something works; **don't merge your own**.
5. Commit small and often, not one giant commit at the end.

**Merge conflict?** `git merge --abort` returns you to safety. Post in the chat
and fix it with someone rather than alone.

---

## 7. Your work, by role

### Person A — Infrastructure (~7 h, front-loaded)

**You are the critical path. Everything else can happen on laptops; only your
work makes the site real. Target: deployed within three days.**

**A1 — Get the skeleton onto the internet (3 h).** Do this first, before any
features exist.

1. Test the Docker build on your laptop: `docker build -t mnist-site .` then
   `docker run -p 8000:8000 mnist-site`. Debugging locally is far easier than on
   a remote box.
2. Create an AWS account. Card required for verification; start early, it can
   take hours.
3. Launch a Lightsail instance. **Pick OS Only → Ubuntu**, not the Django
   blueprint — that one ships with its own web server already holding the ports
   we need. (Check with the instructor before deviating; if they require the
   blueprint, stop the Bitnami stack first with
   `sudo /opt/bitnami/ctlscript.sh stop`.)
4. **Add swap space before anything else.** The free instance doesn't have
   enough RAM to install TensorFlow and the build dies with a bare `Killed`:
   ```bash
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   free -h          # Swap row should show 2G
   ```
5. Install tools, then **log out and back in** so the docker permission applies:
   ```bash
   sudo apt update && sudo apt install -y docker.io git tmux
   sudo usermod -aG docker $USER
   ```
6. Clone, build, run. First build takes 10–15 min.
7. Install ngrok, add your authtoken, then run it **inside tmux** so it survives
   logout:
   ```bash
   tmux new -s tunnel
   ngrok http 8000
   # Ctrl+B, release, then D to detach
   ```
8. Test the public URL **from your phone on cellular data**, not WiFi. That
   proves it's actually public.
9. Post the URL in the chat.
10. **Set a calendar reminder to delete the instance at end of semester**, all
    four of us invited. The free period expires and the card gets charged.

**A2 — Redeploy on demand (2 h, week 2).** `deploy.sh` is already in the repo;
copy it to the AWS box. Redeploy after each major merge. Check `docker ps` after
each one; `docker logs site` shows why if it died.

**A3 — Submission materials (30 min).** Screenshot of `docker ps` running on
AWS (requirement 6), final ngrok URL, README updated with who did what.

> Note on the ngrok URL: the free tier gives a new address every time the tunnel
> restarts. Grab the final URL **after** the last deploy, not before.

---

### Person B — ML & Writeup (~7 h)

**B1 — Train the model (90 min, week 1).** Use Google Colab, no local install
needed.

```python
import tensorflow as tf
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0
x_train, x_test = x_train[..., None], x_test[..., None]

model = tf.keras.Sequential([
    tf.keras.layers.Conv2D(32, 3, activation="relu", input_shape=(28,28,1)),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Conv2D(64, 3, activation="relu"),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation="relu"),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(10, activation="softmax"),
])
model.compile(optimizer="adam", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
history = model.fit(x_train, y_train, epochs=5, validation_split=0.1)
model.save("mnist_model.keras")
```

Five epochs gets ~99%. **Don't tune it.** Nothing grades accuracy. Hours spent
chasing 99.4% are hours not spent on the article or the styling, which *are*
graded.

Write down your architecture choices as you go — you need them for the article
and won't remember next week.

**B2 — Harvest writeup material (90 min, same sitting).** Do this before closing
the notebook; coming back means retraining. Save as PNGs into `static/analysis/`:

- Training and validation curves from `history.history`
- A grid of ~10 confidently **correct** predictions
- A grid of ~10 **misclassified** ones, labeled "true X → said Y". Sort by
  *highest confidence among the wrong ones* — the confidently-wrong cases make
  much better writeup material than borderline coin flips.
- A confusion matrix (note the worst pairs, usually 4/9 and 3/5)

**Look at those ten failures and write down what you notice.** That's your
analysis section and it's far easier to write while staring at the images.

Also generate test CSVs into `samples/`: one per digit on the 0–255 scale, one
on the 0–1 scale (so C can prove the auto-detection works), plus deliberately
broken ones in `samples/bad/` — a `.txt` file, a 10×10 CSV, one with a header
row, one containing text.

**B3 — Swap in the real model (15 min).** Replace the stub in `predictor.py`
per the instructions in its comments, commit `mnist_model.keras`, tell C.

**B4 — Write the article (2 h, week 2).** 800–1200 words, handed to D as
markdown. D does layout, you do words. Structure: the problem → the data → the
architecture in plain language → training → results → **where it fails** → what
we'd do next.

The failure section is what separates a good submission from an average one.
Requirement 2 explicitly asks *why* some images classify poorly. Go past "these
are hard" — talk about ambiguous handwriting, digits sharing strokes, and the
fact that MNIST is centered and size-normalized so the model never learned to
handle off-center input. That last point matters for the CSVs real users upload.

---

### Person C — Backend (~9 h)

You're unblocked immediately — B's stub is already committed.

**C1 — Auth (2 h).** Django's built-in system, already routed at `/accounts/`.
It deliberately has **no signup page**, which satisfies requirement 1b by doing
nothing.

Ask A to add `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL` to
settings (already done in the skeleton — verify). Create the account:

```bash
python manage.py createsuperuser     # username: dan, password from the assignment
```

That account is local-only. **It must be created again on the AWS box** at
integration — requirement 1a is an easy mark to drop.

Then `@login_required` on **every** view. Test in a private browser window: every
URL should bounce to login. One ungated view loses the mark.

**C2 — Upload and validation (3 h).** Validate in layers so each failure gets a
specific, user-facing message:

```python
if not name.lower().endswith(".csv"):    -> "That file isn't a .csv"
if not decodable as utf-8:               -> "That file isn't readable as text"
if np.loadtxt fails:                     -> "Couldn't read as comma-separated numbers.
                                            Check for a header row or text entries."
if arr.shape != (28, 28):                -> "Expected 28x28, got {r} by {c}"
if np.isnan(arr).any():                  -> "Contains empty or non-numeric cells"
if arr.min() < 0 or arr.max() > 255:     -> "Values must be between 0 and 255"
```

Scale detection (requirement 3a) is one line:

```python
if arr.max() > 1.0:
    arr = arr / 255.0
```

If anything exceeds 1, it must be the 0–255 scale — the 0–1 scale can't produce
a value above 1.

> Edge case worth a code comment: an all-black image is all zeros on *both*
> scales, so they're indistinguishable. They're also identical after scaling, so
> it doesn't matter. A grader reading closely will appreciate that you noticed.

**C3 — Predict and display (2 h).** Render the image as a base64 data URI, which
sidesteps serving media files entirely (a real pain in Docker):

```python
img = Image.fromarray((arr * 255).astype("uint8"), mode="L").resize((280,280), Image.NEAREST)
```

`Image.NEAREST` keeps the pixels crisp; the default smoothing turns a 28×28
image into mush at 280×280.

Call `predict(arr)`, then return the five contract keys to `result.html`.
Requirement 5's start-over button is just a link back to `/` — no state to clear
since each result renders fresh.

**Test against every file in `samples/`**, including the broken ones. Each should
produce a clear message, never a Django error page.

**C4 — Integration support (1.5 h).** Delete `/mock/`, create `dan` on the
server.

---

### Person D — Frontend (~9 h)

**Requirement 7: 50% of the grade is appearance.** Your work is worth as much as
everyone else's combined. You're unblocked from day one via `/mock/`.

**D1 — Framework and shell (2 h).** Don't hand-write CSS from scratch; you don't
have the hours and it'll look worse. Pick one:

- **Tailwind via CDN** — `<script src="https://cdn.tailwindcss.com"></script>`.
  Most control, style with utility classes inline.
- **Pico.css** — one link, plain HTML looks good automatically. Near-zero effort.
- **Bootstrap** — middle ground, very well documented.

Build `base.html` first with a nav bar and consistent spacing, then have every
page `{% extends "base.html" %}`. Consistency across pages reads as "designed";
three differently-styled pages read as "rushed."

**Set constraints and hold them: two fonts, three colors.** Most amateur-looking
sites look amateur because they use six.

> One Django gotcha: `{% extends %}` must be the **literal first tag** in the
> file. A comment above it breaks the page.

**D2 — The three pages (3 h).** Login (first thing a grader sees — make it look
deliberate; keep `{% csrf_token %}` inside the form or login silently fails),
upload page (errors as styled alert boxes, not bare text), and the result page
built against `/mock/`.

Specific things that earn visible points on the result page:

- The digit rendered large with `image-rendering: pixelated`
- Ten horizontal confidence bars rather than a single number — shows the model's
  uncertainty, looks considered, takes ten minutes
- A clear "classify another" button

**D3 — Article page (2 h).** B gives you markdown. Constrain the text column to
65–75 characters — full-width paragraphs are the most common giveaway of an
unstyled page. Clear heading hierarchy, B's four images with captions, generous
line height. Link it from the nav.

**D4 — Polish (2 h).** Mobile width check (nothing should overflow), a loading
state on the submit button so the page doesn't look frozen during inference,
every error state styled, a favicon, hover states on everything clickable,
consistent spacing. Then show it to someone outside the team — if they can't
tell what it does in five seconds, the home page needs work.

---

## 8. Timeline

### Week 1

| Day | Who | What |
|---|---|---|
| 1 | All | Roles assigned, everyone running locally, contracts agreed |
| **1–3** | **A** | **Deploy skeleton to AWS. Critical path.** |
| 2–4 | B | Train model, harvest images, generate sample CSVs |
| 2–5 | C | Auth, then upload and validation |
| 2–5 | D | Framework, `base.html`, login and upload pages |
| **4** | All | **Sync #1 (15 min):** is it live? blockers? |
| 5 | A | Redeploy with B's model |

### Week 2

| Day | Who | What |
|---|---|---|
| 6–8 | C | Prediction view, wire up the real predictor |
| 6–8 | D | Result page, article page |
| 6–9 | B | Write article, hand to D |
| **8** | All | **Sync #2 (30 min):** demo what you have |
| 9 | All | **Integration day** (section 9) |
| 10 | D | Polish pass |
| 10 | A | Final deploy, screenshots |
| **11** | All | **Final review:** everyone tests the live site independently |
| 12 | — | Buffer — do not plan work here |

**On day 12:** something will go wrong; it always does. If we plan to finish on
the deadline we'll submit something broken. Plan to finish two days early.

**Syncs are 15 minutes.** Three questions each: what's done, what's blocked,
will you hit your next date. If someone's stuck, pair with them for an hour —
don't wait another week and hope.

---

## 9. Integration day

All four, ~3 hours, same call.

1. **Merge in order (30 min):** A's config → B's model → C's backend → D's
   templates, testing after each. If something breaks you know which merge did it.
2. **Swap mock for real (15 min):** C deletes `/mock/`. D's templates should work
   unchanged — if they don't, the contract drifted and now's when we find out.
3. **Full local test (30 min), each person independently:**
   - Logged out → redirected to login
   - Log in as `dan`
   - Upload a 0–255 sample → correct
   - Upload the 0–1 sample → correct (proves scale detection)
   - Upload every file in `samples/bad/` → clear message each, no error page
   - Start over → clean upload page
   - Read the article page
   - Log out → locked out again
4. **Deploy (45 min):** A runs `./deploy.sh`, then creates `dan` **on the
   server** — fresh database, the account doesn't exist there yet:
   ```bash
   docker exec -it site python manage.py migrate
   docker exec -it site python manage.py createsuperuser
   ```
5. **Test live (30 min):** same eight steps on the ngrok URL, from a device
   that isn't A's laptop.
6. **Capture materials (20 min):** screenshots, final URL, repo link.

Things that only appear in production: a 403 on login if `CSRF_TRUSTED_ORIGINS`
is missing (it's already in settings — don't remove it), and a slow first
prediction while the model loads.

---

## 10. Submission checklist

Verify each on the **live** site, not locally.

| # | Check | Owner |
|---|---|---|
| 1 | Logged-out visitor is redirected | C |
| 1a | `dan` exists **on the server**, login works from a phone | C + A |
| 1b | No signup link; `/accounts/signup/` 404s | C |
| 1c | Every URL tested logged out | C |
| 2 | Article live, readable, all four images render | B + D |
| 3 | Upload works live | C |
| 3a | Both 0–255 and 0–1 samples classify correctly | C |
| 3b | Every file in `samples/bad/` gives a clear message | C + D |
| 4 | Digit shown alongside the image | C + D |
| 5 | Start-over returns to a clean page | C + D |
| 6 | `docker ps` screenshot captured on AWS | A |
| 7 | **Mobile tested, consistent styling, polish done** | D |
| 8 | Repo link included | A |

Plus: ngrok URL current and captured last; tunnel running inside tmux; README
lists who did what; calendar reminder set to delete the Lightsail instance.

---

## 11. Troubleshooting

**`ModuleNotFoundError: No module named 'django'`** — venv isn't active.
`source venv/bin/activate`. Needed in every new terminal.

**`docker build` prints `Killed`** — out of memory. On AWS, add swap (A1 step 4).
On a laptop, raise Docker Desktop's memory limit to 4 GB.

**403 Forbidden on login through the ngrok URL but fine locally** —
`CSRF_TRUSTED_ORIGINS` missing from settings. It's in the skeleton; don't remove it.

**ngrok URL worked yesterday, dead today** — tunnel died because it wasn't in
tmux. `tmux attach -t tunnel` to check. The URL changes on restart.

**Every page 500s** — `docker logs site` shows the actual traceback. Usually a
missing file path or a template name typo.

**Model file not found on the server** — check it's actually committed
(`git ls-files | grep keras`) and that `predictor.py` builds its path from
`Path(__file__).parent`, not a relative string.

**Predictions right locally, wrong on the server** — preprocessing mismatch.
Print `arr.min()`, `arr.max()`, `arr.shape` right before `predict()` and compare
against B's notebook.

**Port 8000 in use on AWS** — leftover container. `docker ps -a` then
`docker rm -f <name>`.

**`{% extends %}` error** — it must be the literal first tag in the template.

**Merge conflict** — `git merge --abort`, then post in the chat.

---

## 12. Glossary

**Django** — the Python library that turns a web request into a web page. You
write functions called *views*; each returns HTML.

**View** — a Python function handling one request, returning one page.

**Template** — an HTML file with placeholders like `{{ prediction }}` that Django
fills in.

**Context** — the dictionary a view hands to a template. Contract 1 is a context.

**Docker** — packages the app plus Python plus TensorFlow into one bundle (an
*image*) that runs identically everywhere. Saves installing TensorFlow by hand on
the server.

**Container** — a running instance of an image.

**Lightsail** — a rented Linux computer in an Amazon data center, operated
through a browser terminal.

**ngrok** — gives that rented computer a public web address, since by default
nothing on the internet can reach it.

**tmux** — keeps a program running after you close the terminal. Without it ngrok
dies on logout and the site goes down.

**Swap** — disk space used as memory overflow. Without it, installing TensorFlow
on a small server fails.

**CSRF** — a security check where Django rejects form submissions from
unrecognised addresses. The reason for the `CSRF_TRUSTED_ORIGINS` setting.

**Base64 data URI** — a way to embed an image directly in HTML as text, so we
never configure file serving.

**venv** — a private copy of Python inside the project folder, so our package
versions don't collide with anything else on your machine.
