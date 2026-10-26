# Multi-stage lightweight container for netlog-cli
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY netlog/ netlog/

RUN pip install --no-cache-dir --upgrade pip build && \
    python -m build --wheel --outdir /dist

FROM python:3.11-slim

LABEL maintainer="Mokshith Reddy <mokshithr530@gmail.com>"
LABEL description="High-performance CLI network telemetry dashboard"

WORKDIR /root

COPY --from=builder /dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp/*.whl

# Note: Host networking (--net=host) is required to inspect host network sockets
ENTRYPOINT ["netlog"]
CMD []
