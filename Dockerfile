FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry && \
    poetry install --no-dev --no-root && \
    pip uninstall --yes poetry

COPY frontend/ .

EXPOSE 8000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]
