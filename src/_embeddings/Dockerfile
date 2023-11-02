FROM python:3.11-slim as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PIPENV_NOSPIN=true \
    NUMBA_CACHE_DIR=/tmp \
    PYTHONPATH=/app \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Copy your application files into the container
COPY requirements.txt /app

# Install your Python dependencies
RUN pip install -r requirements.txt

# Copy your application files into the container
COPY . /app

# Create and switch to a new user
RUN useradd --create-home appuser
USER appuser
RUN python -c 'from sentence_transformers import SentenceTransformer; embedder = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")'
COPY . /app

# Command to run your FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]