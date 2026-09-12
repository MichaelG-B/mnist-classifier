# OWNER: Person A. Nobody else edits this file.
#
# Read this as a recipe:
#   start from a minimal Linux with Python -> copy in the package list ->
#   install them -> copy in our code -> run the server.

FROM python:3.11-slim

# Stops Python buffering output, so `docker logs` shows errors immediately
# instead of holding them until the buffer fills.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# requirements.txt is copied and installed BEFORE the rest of the code on
# purpose. Docker caches each step. Because our code changes constantly and
# our dependencies almost never do, this ordering means a code change reuses
# the cached TensorFlow install instead of redownloading it -- the difference
# between a 20-second rebuild and a 12-minute one.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# 0.0.0.0 matters. Plain `runserver` listens only to the same machine, which
# inside a container means the container itself -- the page would be
# unreachable from outside with no error message to explain why.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
