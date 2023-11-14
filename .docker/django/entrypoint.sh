#!/usr/bin/env bash

# configure db vars
export POSTGRES_USER=${POSTGRES_USER:-"postgres"}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-"postgres"}
export POSTGRES_HOST=${POSTGRES_HOST:-"postgres"}
export POSTGRES_DB=${POSTGRES_DB:-"postgres"}
export POSTGRES_PORT=${POSTGRES_PORT:-"5432"}
export DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
export IPYTHONDIR="/app/.ipython"
export ENVIROMENT=${ENVIROMENT:-local}
export DJANGO_SETTINGS_MODULE=config.settings.${ENVIROMENT}

postgres_ready() {
python << END
import sys

import psycopg2

try:
    psycopg2.connect(
        dbname="${POSTGRES_DB}",
        user="${POSTGRES_USER}",
        password="${POSTGRES_PASSWORD}",
        host="${POSTGRES_HOST}",
        port="${POSTGRES_PORT}",
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)

END
}
# avoid check postgresql with root user
is_user_root () { [ "${EUID:-$(id -u)}" -eq 0 ]; }
if is_user_root; then
    echo "Logging as root user"
else
    until postgres_ready; do
      >&2 echo 'Waiting for PostgreSQL to become available...'
      >&2 echo $DATABASE_URL
      sleep 1
    done
    >&2 echo 'PostgreSQL is available'
fi

cd /app

# entrypoints
if [[ "${1}" == "shell" ]]; then
    exec /bin/bash
elif [[ "${1}" == "runserver" ]]; then
    exec dev up
elif [[ "${1}" == "migrate-noinput" ]]; then
    exec python manage.py migrate --noinput
elif [[ "${1}" == "collectstatic" ]]; then
    exec python manage.py collectstatic --noinput
elif [[ "${1}" == "celery" ]]; then
    printf "started Docker container as runtype \e[1;93mcelery\e[0m\n"
    QUEUES="${QUEUES:-celery}"
    LOG_LEVEL="${LOG_LEVEL:-info}"
    CONCURRENCY="${CONCURRENCY:-4}"
    MAX_TASKS="${MAX_TASKS:-1000}"
    CELERY_POOL="${CELERY_POOL:-prefork}"
    exec celery -A config.celery_app worker \
        -P ${CELERY_POOL} \
        -l ${LOG_LEVEL} \
        -c ${CONCURRENCY} \
        --max-tasks-per-child=${MAX_TASKS} \
        ${EXTRA_ARGS} \
        -Q ${QUEUES}
elif [[ "${1}" == "celerybeat" ]]; then
    printf "started Docker container as runtype \e[1;93mcelerybeat\e[0m\n"
    exec celery -A config.celery_app beat
else
    exec "$@"
fi
