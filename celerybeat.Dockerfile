FROM python:3.11

WORKDIR /app/

# Install Poetry
RUN pip install celery eventlet numpy cpmpy redis loguru

COPY . /app
ENV PYTHONPATH=/app


CMD ["celery", "-A", "worker.app", "beat"]
