FROM python:3.6-slim

ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY

ENV PYTHONUNBUFFERED=1 \
	NODEJS_VERSION=6.3.1-1nodesource1~jessie1 \
	DEBIAN_FRONTEND=noninteractive

RUN \
	echo "Install base packages" \
	&& ([ -z "$HTTP_PROXY" ] || echo "Acquire::http::Proxy \"${HTTP_PROXY}\";" > /etc/apt/apt.conf.d/99HttpProxy) \
	&& apt-get update \
	&& apt-get install -y --no-install-recommends \
		make \
		curl \
		git \
		build-essential \
		zip \
	    rlwrap \
	&& echo "Clean up" \
	&& rm -rf /var/lib/apt/lists/* /tmp/* \
	&& echo "Install nodejs" \
	&& cd /tmp \
	&& curl -x "$HTTP_PROXY" -sSLO https://deb.nodesource.com/node_6.x/pool/main/n/nodejs/nodejs_${NODEJS_VERSION}_amd64.deb \
	&& dpkg -i /tmp/nodejs_${NODEJS_VERSION}_amd64.deb \
	&& echo "Clean up" \
	&& rm -rf /var/lib/apt/lists/* /tmp/*

RUN \
	echo "Install global pip packages" \
	&& pip install \
		virtualenv \
		awscli \
		wheel

WORKDIR /var/project

COPY requirements.txt requirements.txt
COPY requirements-app.txt requirements-app.txt
COPY requirements-dev.txt requirements-dev.txt

RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .
