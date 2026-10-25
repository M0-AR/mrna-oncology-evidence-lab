FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DEFAULT_TIMEOUT=120

WORKDIR /app

COPY pyproject.toml README.md Makefile ./
COPY src ./src
COPY config ./config
COPY data ./data
COPY evidence ./evidence
COPY tests ./tests
COPY scripts ./scripts
COPY preview.html index.html .nojekyll ./
COPY assets ./assets

RUN apt-get update \
    && apt-get install -y --no-install-recommends make \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --retries 10 -e ".[dev]"

CMD ["python", "-m", "mrna_evidence.pipeline"]
