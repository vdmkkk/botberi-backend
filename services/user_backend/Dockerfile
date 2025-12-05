FROM python:3.12-slim AS runtime

ARG INSTALL_DEV="false"
ARG SERVICE_PATH="services/user_backend"
ARG SHARED_MODELS_PATH="packages/shared_psql_models"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY ${SERVICE_PATH}/requirements/ /tmp/requirements/
COPY ${SHARED_MODELS_PATH}/ /tmp/shared_psql_models/

RUN pip install --upgrade pip \
    && pip install /tmp/shared_psql_models \
    && pip install -r /tmp/requirements/base.txt \
    && if [ "$INSTALL_DEV" = "true" ]; then pip install -r /tmp/requirements/dev.txt; fi

COPY ${SERVICE_PATH}/ /app

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${API_PORT:-8010}"]


