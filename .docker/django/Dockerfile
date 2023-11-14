FROM python:3.11.6-slim-bullseye as python

# build stage
FROM python as python-build-stage

ARG BUILD_ENVIRONMENT=local

RUN apt-get update && \
  apt-get install --no-install-recommends -y \
  build-essential \
  libpq-dev

COPY ./requirements .
RUN pip wheel --wheel-dir /usr/src/app/wheels  \
  -r ${BUILD_ENVIRONMENT}.txt

# run stage
FROM python as python-run-stage

ARG BUILD_ENVIRONMENT=local
ARG APP_HOME=/app
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV BUILD_ENV ${BUILD_ENVIRONMENT}

RUN apt-get update && apt-get install --no-install-recommends -y \
  sudo git bash-completion nano ssh

RUN groupadd --gid 1000 dev-user \
  && useradd --uid 1000 --gid dev-user --shell /bin/bash --create-home dev-user \
  && echo dev-user ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/dev-user \
  && chmod 0440 /etc/sudoers.d/dev-user

RUN apt-get update && apt-get install --no-install-recommends -y \
  libpq-dev \
  gettext \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

COPY --from=python-build-stage /usr/src/app/wheels  /wheels/

RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/*

COPY ./.docker/django/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//g' /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./.docker/django/dev /usr/local/bin/dev
RUN sed -i 's/\r$//g' /usr/local/bin/dev
RUN chmod +x /usr/local/bin/dev


# copy application code to WORKDIR
COPY . ${APP_HOME}
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
