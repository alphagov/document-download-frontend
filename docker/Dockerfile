FROM python:3.11-slim-bookworm AS base

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/* /tmp/*

WORKDIR /home/vcap/app

##### Frontend Build Image ###################################################
ARG NODE_VERSION=20

FROM ghcr.io/alphagov/notify/unit-tests-image:python311-node20 as frontend_build

WORKDIR /usr/frontend
COPY app app
COPY package-lock.json package.json rollup.config.mjs ./

RUN npm ci --no-audit \
    && npm run build

###### Python Build Image #####################################################
FROM base AS python_build

RUN echo "Install OS dependencies for python app requirements" &&  \
    apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/* /tmp/*

COPY requirements.txt .

RUN pip install uv

ENV UV_CACHE_DIR='/tmp/uv-cache/'
RUN echo "Installing python dependencies" && \
    python3 -m venv /opt/venv && \
    uv pip sync --python /opt/venv/bin/python requirements.txt

COPY . .

RUN make generate-version-file # This file gets copied across

##### Production Image #######################################################
FROM base AS production

RUN groupadd -r notify && useradd -r -g notify notify && chown -R notify:notify /home/vcap

USER notify

RUN mkdir /home/vcap/logs

COPY --from=python_build --chown=root:root /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

COPY --chown=notify:notify app app
COPY --chown=notify:notify application.py entrypoint.sh gunicorn_config.py ./
COPY --from=frontend_build /usr/frontend/app/static app/static
COPY --from=frontend_build /usr/frontend/app/templates app/templates
COPY --from=frontend_build --chown=notify:notify /usr/local/lib /usr/local/lib
COPY --from=frontend_build --chown=notify:notify /usr/local/bin /usr/local/bin
COPY --from=python_build --chown=notify:notify /home/vcap/app/app/version.py app/version.py
USER root
RUN python -m compileall . && \
    chown -R notify:notify /home/vcap/app && \
    chmod +x /home/vcap/app/entrypoint.sh
USER notify

ENTRYPOINT [ "/home/vcap/app/entrypoint.sh" ]

##### Test Image ##############################################################
FROM production as test

USER root

RUN echo "Install OS dependencies for test build" \
    && apt-get update && \
    apt-get install -y --no-install-recommends \
      curl \
      git \
      make \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/* /tmp/*
RUN usermod -aG sudo notify
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER notify

ENV HOME=/home/vcap

# Copying to overwrite is faster than RUN chown notify:notify ...
COPY --from=python_build --chown=notify:notify /opt/venv /opt/venv

# Make sure the app/ directory is there so that "make bootstrap" can create app/version.py
RUN mkdir -p app

# Install dev/test requirements
RUN pip install uv
COPY --chown=notify:notify Makefile requirements_for_test.txt package-lock.json package.json rollup.config.mjs ./
ENV UV_CACHE_DIR='/tmp/uv-cache/'
RUN make bootstrap

# Copy from the real world, one dir up (project root) into the environment's current working directory
# Docker will rebuild from here down every time.
COPY --chown=notify:notify . .
