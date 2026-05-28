# Stage 1: Build
FROM ubuntu:24.04 AS build

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    pkg-config \
    ca-certificates \
    libxml2-dev \
    libfontconfig1-dev \
    libfreetype-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/pdfalto

RUN git clone --recurse-submodules https://github.com/kermitt2/pdfalto.git . \
    && git submodule update --init --recursive \
    && cmake . \
    && make -j"$(nproc)"

# Stage 2: Runtime
FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/pdfalto/pdfalto /usr/local/bin/pdfalto

RUN mkdir -p /shared && chmod 777 /shared

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py /app/main.py

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]